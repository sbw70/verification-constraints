# Copyright (c) 2026 Seth Brian Wells. All rights reserved.
# Proprietary. Commercial licensing available. Research licensing available.
# Use of this file is governed by the license terms in the module-license-notice folder.

#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import hashlib
import hmac
import json
import os
import threading
import time
import urllib.request
from typing import Dict, Any, List, Tuple

# -----------------------------
# Network layout (single-process demo)
# -----------------------------
HUB_A_HOST = "0.0.0.0"
HUB_A_PORT = 8080

HUB_B_HOST = "0.0.0.0"
HUB_B_PORT = 8081

PROVIDER_HOST = "0.0.0.0"
PROVIDER_A_PORT = 9090
PROVIDER_B_PORT = 9091
PROVIDER_C_PORT = 9092

HUB_A_INTAKE_URL = f"http://127.0.0.1:{HUB_A_PORT}/submit"
HUB_A_OUTCOME_URL = f"http://127.0.0.1:{HUB_A_PORT}/outcome"

HUB_B_INTAKE_URL = f"http://127.0.0.1:{HUB_B_PORT}/submit"
HUB_B_OUTCOME_URL = f"http://127.0.0.1:{HUB_B_PORT}/outcome"

PROVIDER_A_INGEST_URL = f"http://127.0.0.1:{PROVIDER_A_PORT}/ingest"
PROVIDER_B_INGEST_URL = f"http://127.0.0.1:{PROVIDER_B_PORT}/ingest"
PROVIDER_C_INGEST_URL = f"http://127.0.0.1:{PROVIDER_C_PORT}/ingest"

# -----------------------------
# Demo parameters
# -----------------------------
MAX_REQUEST_BYTES = 1024 * 64  # 64KB
BIND_TAG = "BIND_V1"

EXPECTED_CONTEXT = "CTX_ALPHA"
PROVIDER_HMAC_KEY = b"PROVIDER_ONLY_KEY_CHANGE_ME"

# Routing configuration (mechanical; hub does not interpret provider semantics)
# - versioned and selectable
ROUTING_CONFIG: Dict[str, Dict[str, Any]] = {
    "v1": {
        "enabled": True,
        "fanout_providers": ["PROVIDER_A", "PROVIDER_B", "PROVIDER_C"],
        "relay_hubs": ["HUB_B"],
    }
}
ACTIVE_ROUTING_VERSION = "v1"

PROVIDER_MAP: Dict[str, str] = {
    "PROVIDER_A": PROVIDER_A_INGEST_URL,
    "PROVIDER_B": PROVIDER_B_INGEST_URL,
    "PROVIDER_C": PROVIDER_C_INGEST_URL,
}

HUB_MAP: Dict[str, str] = {
    "HUB_A": HUB_A_INTAKE_URL,
    "HUB_B": HUB_B_INTAKE_URL,
}

# Transient coordination tracking (not execution state)
# correlation_id -> created_at_ns
PENDING: Dict[str, int] = {}
PENDING_TTL_NS = 30 * 1_000_000_000  # 30s


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def bind_request(request_repr_hex: str, verification_context: str) -> str:
    msg = (BIND_TAG + "|" + request_repr_hex + "|" + verification_context).encode("utf-8")
    return hashlib.sha256(msg).hexdigest()


def provider_boundary_signature(provider_id: str, request_repr_hex: str, verification_context: str, binding: str, stage: str) -> str:
    msg = (provider_id + "|" + stage + "|" + request_repr_hex + "|" + verification_context + "|" + binding).encode("utf-8")
    return hmac.new(PROVIDER_HMAC_KEY, msg, hashlib.sha256).hexdigest()


def now_ns() -> int:
    return time.time_ns()


def _http_post_json(url: str, payload: Dict[str, Any], timeout_s: float = 2.0) -> None:
    data = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s):
        pass


def fire_and_forget_post(url: str, payload: Dict[str, Any], timeout_s: float = 2.0) -> None:
    def _send():
        try:
            _http_post_json(url, payload, timeout_s=timeout_s)
        except Exception:
            return

    threading.Thread(target=_send, daemon=True).start()


def correlation_id_from(request_repr_hex: str, hub_id: str) -> str:
    seed = (hub_id + "|" + request_repr_hex + "|" + str(now_ns())).encode("utf-8")
    return "CORR_" + sha256_hex(seed)[:20]


def prune_pending() -> None:
    cutoff = now_ns() - PENDING_TTL_NS
    stale = [cid for cid, t in PENDING.items() if t < cutoff]
    for cid in stale:
        PENDING.pop(cid, None)


def routing_plan() -> Tuple[List[str], List[str], str]:
    cfg = ROUTING_CONFIG.get(ACTIVE_ROUTING_VERSION, {})
    if not cfg or not cfg.get("enabled", False):
        return ([], [], ACTIVE_ROUTING_VERSION)
    providers = list(cfg.get("fanout_providers", []))
    hubs = list(cfg.get("relay_hubs", []))
    return (providers, hubs, ACTIVE_ROUTING_VERSION)


# -----------------------------
# Provider implementation
# -----------------------------
class ProviderHandler(BaseHTTPRequestHandler):
    provider_id = "PROVIDER_X"
    hub_outcome_url = HUB_A_OUTCOME_URL  # provider reports to the hub that contacted it (hub passes this in payload)

    def log_message(self, fmt, *args):
        return

    def do_POST(self):
        if self.path != "/ingest":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length > 0 else b""
        if length > MAX_REQUEST_BYTES:
            self.send_response(204)
            self.end_headers()
            return

        try:
            msg = json.loads(body.decode("utf-8"))
        except Exception:
            self.send_response(204)
            self.end_headers()
            return

        # Hub-forwarded payload (opaque request bytes are NOT required here; only representations)
        request_repr = msg.get("request_repr", "")
        verification_context = msg.get("verification_context", "")
        binding = msg.get("binding", "")
        correlation_id = msg.get("correlation_id", "")
        return_outcome_url = msg.get("return_outcome_url", "")

        initiated = False
        if verification_context == EXPECTED_CONTEXT:
            expected = bind_request(request_repr, verification_context)
            if binding == expected:
                initiated = True

        if initiated:
            start_sig = provider_boundary_signature(self.provider_id, request_repr, verification_context, binding, "START")
            complete_sig = provider_boundary_signature(self.provider_id, request_repr, verification_context, binding, "COMPLETE")
            print(f"{self.provider_id}: INITIATED")
            outcome = {
                "provider_id": self.provider_id,
                "correlation_id": correlation_id,
                "request_repr": request_repr,
                "boundary": {
                    "start": start_sig,
                    "complete": complete_sig,
                },
                "provider_initiated": True,
            }
        else:
            print(f"{self.provider_id}: NOT INITIATED")
            outcome = {
                "provider_id": self.provider_id,
                "correlation_id": correlation_id,
                "request_repr": request_repr,
                "boundary": None,
                "provider_initiated": False,
            }

        # Provider may emit an outcome signal for relay/reporting; hub remains non-authoritative
        if isinstance(return_outcome_url, str) and return_outcome_url.startswith("http"):
            fire_and_forget_post(return_outcome_url, outcome)

        self.send_response(204)
        self.end_headers()


def make_provider_server(provider_id: str, port: int):
    handler_cls = type(f"{provider_id}Handler", (ProviderHandler,), {"provider_id": provider_id})
    return HTTPServer((PROVIDER_HOST, port), handler_cls)


# -----------------------------
# Hub implementation
# -----------------------------
class HubHandler(BaseHTTPRequestHandler):
    hub_id = "HUB_X"
    peer_hub_submit_url = HUB_B_INTAKE_URL  # used when relaying to other hubs
    local_outcome_url = HUB_A_OUTCOME_URL   # where providers should post outcomes for this hub

    def log_message(self, fmt, *args):
        return

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_REQUEST_BYTES:
            return {}
        body = self.rfile.read(length) if length > 0 else b""
        if not body:
            return {}
        try:
            return json.loads(body.decode("utf-8"))
        except Exception:
            return {}

    def do_POST(self):
        if self.path == "/submit":
            self._handle_submit()
            return
        if self.path == "/outcome":
            self._handle_outcome()
            return

        self.send_response(404)
        self.end_headers()

    def _handle_submit(self):
        # Accept either raw bytes (requester -> hub) or forwarded JSON (hub -> hub)
        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_REQUEST_BYTES:
            self.send_response(204)
            self.end_headers()
            return

        content_type = (self.headers.get("Content-Type", "") or "").lower()
        raw = self.rfile.read(length) if length > 0 else b""

        verification_context = self.headers.get("X-Verification-Context", "")
        request_repr = sha256_hex(raw)
        binding = bind_request(request_repr, verification_context)

        # If a peer hub forwarded JSON, preserve its request_repr/binding if provided (mechanical relay)
        if "application/json" in content_type:
            try:
                j = json.loads(raw.decode("utf-8")) if raw else {}
            except Exception:
                j = {}
            rr = j.get("request_repr")
            vc = j.get("verification_context")
            bd = j.get("binding")
            if isinstance(rr, str) and isinstance(vc, str) and isinstance(bd, str):
                request_repr = rr
                verification_context = vc
                binding = bd

        prune_pending()
        corr = correlation_id_from(request_repr, self.hub_id)
        PENDING[corr] = now_ns()

        providers, hubs, version = routing_plan()

        # Forward to providers (fan-out) mechanically
        for pid in providers:
            url = PROVIDER_MAP.get(pid)
            if not url:
                continue
            forward = {
                "hub_id": self.hub_id,
                "routing_version": version,
                "correlation_id": corr,
                "request_repr": request_repr,
                "verification_context": verification_context,
                "binding": binding,
                "return_outcome_url": self.local_outcome_url,
            }
            fire_and_forget_post(url, forward)

        # Relay to other hubs (multi-hub) mechanically
        for hid in hubs:
            if hid == self.hub_id:
                continue
            submit_url = HUB_MAP.get(hid)
            if not submit_url:
                continue
            relay = {
                "from_hub": self.hub_id,
                "routing_version": version,
                "correlation_id": corr,
                "request_repr": request_repr,
                "verification_context": verification_context,
                "binding": binding,
            }
            fire_and_forget_post(submit_url, relay)

        # Constant response; hub does not return authorization outcome
        self.send_response(204)
        self.end_headers()

    def _handle_outcome(self):
        msg = self._read_json()
        if not msg:
            self.send_response(204)
            self.end_headers()
            return

        # Non-authoritative relay/recording
        corr = msg.get("correlation_id", "")
        pid = msg.get("provider_id", "")
        initiated = bool(msg.get("provider_initiated", False))

        # Print only minimal, operator-neutral output
        # Hub does not determine success/failure; it only relays signals
        if isinstance(pid, str) and isinstance(corr, str):
            print(f"{self.hub_id}: RELAYED_OUTCOME provider={pid} correlation={corr} initiated={initiated}")

        self.send_response(204)
        self.end_headers()


def make_hub_server(hub_id: str, host: str, port: int, local_outcome_url: str):
    handler_cls = type(
        f"{hub_id}Handler",
        (HubHandler,),
        {"hub_id": hub_id, "local_outcome_url": local_outcome_url},
    )
    return HTTPServer((host, port), handler_cls)


# -----------------------------
# Requester (demo driver)
# -----------------------------
def requester_send(payload: bytes, verification_context: str, hub_submit_url: str) -> int:
    req = urllib.request.Request(
        hub_submit_url,
        data=payload,
        headers={
            "Content-Type": "application/octet-stream",
            "X-Verification-Context": verification_context,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=2) as resp:
        return resp.status


def start_server(server: HTTPServer) -> None:
    server.serve_forever()


def main():
    # Start providers
    provider_a = make_provider_server("PROVIDER_A", PROVIDER_A_PORT)
    provider_b = make_provider_server("PROVIDER_B", PROVIDER_B_PORT)
    provider_c = make_provider_server("PROVIDER_C", PROVIDER_C_PORT)

    # Start hubs
    hub_a = make_hub_server("HUB_A", HUB_A_HOST, HUB_A_PORT, HUB_A_OUTCOME_URL)
    hub_b = make_hub_server("HUB_B", HUB_B_HOST, HUB_B_PORT, HUB_B_OUTCOME_URL)

    threading.Thread(target=start_server, args=(provider_a,), daemon=True).start()
    threading.Thread(target=start_server, args=(provider_b,), daemon=True).start()
    threading.Thread(target=start_server, args=(provider_c,), daemon=True).start()
    threading.Thread(target=start_server, args=(hub_a,), daemon=True).start()
    threading.Thread(target=start_server, args=(hub_b,), daemon=True).start()

    time.sleep(0.6)

    size_bytes = os.path.getsize(__file__)
    print(f"Reference size: {size_bytes} bytes ({size_bytes/1024:.1f} KiB)")

    payload = b'{"op":"dispatch","target":"multi_hub","amount":100,"to":"acct_123"}'

    print("Requester: sending request 1...")
    print("Requester saw status:", requester_send(payload, EXPECTED_CONTEXT, HUB_A_INTAKE_URL))

    # Keep alive for async outcome relay prints
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
