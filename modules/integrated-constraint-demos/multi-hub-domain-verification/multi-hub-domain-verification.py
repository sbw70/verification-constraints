#!/usr/bin/env python3
# Copyright 2026 Seth Brian Wells
#
# This file incorporates components derived from the NUVL core,
# which is licensed under the Apache License, Version 2.0.
# A copy of the Apache License may be obtained at:
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Except for the Apache-2.0 licensed NUVL core components,
# all additional orchestration, failover, quorum, adversarial,
# and integration logic contained in this file is proprietary.
#
# Commercial deployment, redistribution, or integration of
# the proprietary portions requires a separate written license agreement.

from http.server import ThreadingHTTPServer as HTTPServer, BaseHTTPRequestHandler
import hashlib
import hmac
import json
import os
import random
import threading
import time
import urllib.request
from typing import Dict, Any, List, Tuple, Optional

# ============================================================
# CONFIG
# ============================================================
PORT_BASE = int(os.getenv("PORT_BASE", "12000"))  # change if you collide with other repls

# Hubs (two hubs = multi-hub mesh)
HUB_A_HOST = "0.0.0.0"
HUB_A_PORT = PORT_BASE + 80
HUB_B_HOST = "0.0.0.0"
HUB_B_PORT = PORT_BASE + 81

# Providers (multi-provider fanout)
PROVIDER_HOST = "0.0.0.0"
PROVIDER_A_PORT = PORT_BASE + 90
PROVIDER_B_PORT = PORT_BASE + 91
PROVIDER_C_PORT = PORT_BASE + 92

# URLs
HUB_A_SUBMIT_URL = f"http://127.0.0.1:{HUB_A_PORT}/submit"
HUB_A_OUTCOME_URL = f"http://127.0.0.1:{HUB_A_PORT}/outcome"
HUB_B_SUBMIT_URL = f"http://127.0.0.1:{HUB_B_PORT}/submit"
HUB_B_OUTCOME_URL = f"http://127.0.0.1:{HUB_B_PORT}/outcome"

PROVIDER_A_INGEST_URL = f"http://127.0.0.1:{PROVIDER_A_PORT}/ingest"
PROVIDER_B_INGEST_URL = f"http://127.0.0.1:{PROVIDER_B_PORT}/ingest"
PROVIDER_C_INGEST_URL = f"http://127.0.0.1:{PROVIDER_C_PORT}/ingest"

MAX_REQUEST_BYTES = 1024 * 64  # 64KB

# Opaque headers (treated as opaque by hubs/NUVL)
EXPECTED_CONTEXT = "CTX_ALPHA"

# Domains drive *routing only* (mechanical). Providers can also use domain in their own logic.
DOMAINS = ["payments", "identity", "storage"]
DEFAULT_DOMAIN = "payments"

# Request run controls (keep small enough for Replit)
TOTAL_REQUESTS = int(os.getenv("TOTAL_REQUESTS", "100"))
SPOOF_RATE = float(os.getenv("SPOOF_RATE", "0.10"))     # percent of requests with spoofed context
UNKNOWN_DOMAIN_RATE = float(os.getenv("UNKNOWN_DOMAIN_RATE", "0.10"))  # percent with unknown domain
OVERSIZE_RATE = float(os.getenv("OVERSIZE_RATE", "0.05"))  # percent oversize (hub drops before routing)

# Determinism
RANDOM_SEED_ENV = os.getenv("RANDOM_SEED", "")
RANDOM_SEED: Optional[int] = int(RANDOM_SEED_ENV) if RANDOM_SEED_ENV.strip() else None

# Print controls: keep console clean
PRINT_PROVIDER_LINES = False  # set True if you want per-provider INIT/NOT lines
PRINT_HUB_RELAY_LINES = False # set True if you want per-outcome relay lines

# ============================================================
# MECHANICAL PRIMITIVES (NUVL/Hubs)
# ============================================================
BIND_TAG = "NUVL_BIND_V1"

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def mechanical_bind(request_repr_hex: str, verification_context: str, domain: str) -> str:
    # Mechanical / deterministic; no secrets
    msg = (BIND_TAG + "|" + request_repr_hex + "|" + verification_context + "|" + domain).encode("utf-8")
    return hashlib.sha256(msg).hexdigest()

def now_ns() -> int:
    return time.time_ns()

def _http_post_json(url: str, payload: Dict[str, Any], timeout_s: float = 2.0) -> None:
    data = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Connection": "close", "Content-Type": "application/json"},
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

# ============================================================
# EXTENSION: Provider-side adaptive evaluation + boundary artifacts (PROPRIETARY SECTION)
# ============================================================
BOUNDARY_TAG = "BOUNDARY_V1"
PROVIDER_BOUNDARY_KEY = b"PROVIDER_ONLY_BOUNDARY_KEY_CHANGE_ME"
PROVIDER_MODEL_SEED = b"PROVIDER_ONLY_MODEL_SEED_CHANGE_ME"

# Domain-specific thresholds (provider-only policy surface)
PROVIDER_THRESHOLDS = {
    "payments": 0.55,
    "identity": 0.60,
    "storage": 0.50,
}

def provider_adaptive_score(provider_id: str, rr: str, ctx: str, domain: str) -> float:
    # Provider-only “model” stand-in
    material = (provider_id + "|" + domain + "|" + rr + "|" + ctx).encode("utf-8")
    digest = hmac.new(PROVIDER_MODEL_SEED, material, hashlib.sha256).digest()
    n = int.from_bytes(digest[:8], "big")
    base = (n % 10_000_000) / 10_000_000.0
    if ctx == EXPECTED_CONTEXT:
        base = min(1.0, base + 0.15)
    return base

def provider_boundary_artifact(operation_id: str, stage: str, rr: str) -> Dict[str, Any]:
    ts = now_ns()
    payload = f"{BOUNDARY_TAG}|{operation_id}|{stage}|{rr}|{ts}".encode("utf-8")
    sig = hmac.new(PROVIDER_BOUNDARY_KEY, payload, hashlib.sha256).hexdigest()
    return {"operation_id": operation_id, "stage": stage, "ts": ts, "sig": sig}

# ============================================================
# ROUTING (Hub mechanical config)
# ============================================================
PROVIDER_MAP: Dict[str, str] = {
    "PROVIDER_A": PROVIDER_A_INGEST_URL,
    "PROVIDER_B": PROVIDER_B_INGEST_URL,
    "PROVIDER_C": PROVIDER_C_INGEST_URL,
}
HUB_MAP: Dict[str, str] = {
    "HUB_A": HUB_A_SUBMIT_URL,
    "HUB_B": HUB_B_SUBMIT_URL,
}

# Mechanical routing plan per domain (no semantics inferred)
ROUTING: Dict[str, Dict[str, Any]] = {
    "payments": {"fanout_providers": ["PROVIDER_A", "PROVIDER_B"], "relay_hubs": ["HUB_B"]},
    "identity": {"fanout_providers": ["PROVIDER_B", "PROVIDER_C"], "relay_hubs": []},
    "storage":  {"fanout_providers": ["PROVIDER_C"], "relay_hubs": ["HUB_B"]},
    # unknown domain => fail-closed by conveyance (no routing)
}

def routing_plan(domain: str) -> Tuple[List[str], List[str]]:
    cfg = ROUTING.get(domain, {})
    return (list(cfg.get("fanout_providers", [])), list(cfg.get("relay_hubs", [])))

def correlation_id_from(hub_id: str, rr: str, domain: str) -> str:
    seed = (hub_id + "|" + rr + "|" + domain + "|" + str(now_ns())).encode("utf-8")
    return "CORR_" + sha256_hex(seed)[:24]

# ============================================================
# COUNTERS (clean benchmark output)
# ============================================================
LOCK = threading.Lock()

# requester-side
REQ_SENT = 0
REQ_CTX_SPOOFED = 0
REQ_DOMAIN_UNKNOWN = 0
REQ_OVERSIZED = 0

# hub-side (mechanical)
HUB_ACCEPTED = 0
HUB_ROUTED_TO_PROVIDER = 0
HUB_RELAYED_TO_HUB = 0

# provider-side outcomes observed at hub outcome endpoint
OUTCOME_TOTAL = 0
OUTCOME_INITIATED = 0
OUTCOME_NOT_INITIATED = 0
OUTCOME_BY_PROVIDER = {"PROVIDER_A": {"init": 0, "no": 0},
                       "PROVIDER_B": {"init": 0, "no": 0},
                       "PROVIDER_C": {"init": 0, "no": 0}}
OUTCOME_BY_DOMAIN: Dict[str, Dict[str, int]] = {}

def bump_domain(domain: str, initiated: bool) -> None:
    with LOCK:
        OUTCOME_BY_DOMAIN.setdefault(domain, {"init": 0, "no": 0})
        if initiated:
            OUTCOME_BY_DOMAIN[domain]["init"] += 1
        else:
            OUTCOME_BY_DOMAIN[domain]["no"] += 1

# ============================================================
# PROVIDERS
# ============================================================
class ProviderHandler(BaseHTTPRequestHandler):
    provider_id = "PROVIDER_X"

    def log_message(self, fmt, *args):  # silence server logs
        return

    def do_POST(self):
        if self.path != "/ingest":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_REQUEST_BYTES:
            self.send_response(204)
            self.end_headers()
            return

        body = self.rfile.read(length) if length > 0 else b""
        try:
            msg = json.loads(body.decode("utf-8"))
        except Exception:
            self.send_response(204)
            self.end_headers()
            return

        rr = str(msg.get("request_repr", ""))
        ctx = str(msg.get("verification_context", ""))
        domain = str(msg.get("domain", ""))
        binding = str(msg.get("binding", ""))
        corr = str(msg.get("correlation_id", ""))
        return_outcome_url = str(msg.get("return_outcome_url", ""))

        # Provider validates mechanical binding
        expected = mechanical_bind(rr, ctx, domain)
        binding_ok = hmac.compare_digest(binding, expected)

        # Provider-only decision
        score = provider_adaptive_score(self.provider_id, rr, ctx, domain)
        threshold = PROVIDER_THRESHOLDS.get(domain, 1.0)  # unknown domains fail closed at provider
        initiated = bool(binding_ok and score >= threshold)

        # Optional boundary artifacts (not used by hub to decide)
        outcome: Dict[str, Any]
        if initiated:
            op_id = sha256_hex((rr + "|" + ctx + "|" + domain).encode("utf-8"))
            start_b = provider_boundary_artifact(op_id, "START", rr)
            complete_b = provider_boundary_artifact(op_id, "COMPLETE", rr)
            outcome = {
                "provider_id": self.provider_id,
                "correlation_id": corr,
                "domain": domain,
                "provider_initiated": True,
                "score": round(score, 6),
                "boundary": {"start": start_b["sig"], "complete": complete_b["sig"]},
            }
            if PRINT_PROVIDER_LINES:
                print(f"{self.provider_id}: INITIATED domain={domain} score={score:.3f} corr={corr[:12]}...")
        else:
            outcome = {
                "provider_id": self.provider_id,
                "correlation_id": corr,
                "domain": domain,
                "provider_initiated": False,
                "score": round(score, 6),
                "boundary": None,
            }
            if PRINT_PROVIDER_LINES:
                print(f"{self.provider_id}: NOT_INITIATED domain={domain} score={score:.3f} binding_ok={binding_ok} corr={corr[:12]}...")

        if return_outcome_url.startswith("http"):
            fire_and_forget_post(return_outcome_url, outcome)

        self.send_response(204)
        self.end_headers()

def make_provider(provider_id: str, port: int) -> HTTPServer:
    handler_cls = type(f"{provider_id}Handler", (ProviderHandler,), {"provider_id": provider_id})
    return HTTPServer((PROVIDER_HOST, port), handler_cls)

# ============================================================
# HUBS
# ============================================================
class HubHandler(BaseHTTPRequestHandler):
    hub_id = "HUB_X"
    local_outcome_url = HUB_A_OUTCOME_URL

    def log_message(self, fmt, *args):
        return

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
        global HUB_ACCEPTED, HUB_ROUTED_TO_PROVIDER, HUB_RELAYED_TO_HUB

        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_REQUEST_BYTES:
            self.send_response(204)
            self.end_headers()
            return

        content_type = (self.headers.get("Content-Type", "") or "").lower()
        raw = self.rfile.read(length) if length > 0 else b""

        # If peer hub forwarded JSON, preserve mechanical fields verbatim
        if "application/json" in content_type:
            try:
                j = json.loads(raw.decode("utf-8")) if raw else {}
            except Exception:
                j = {}
            rr = j.get("request_repr", "")
            ctx = j.get("verification_context", "")
            domain = j.get("domain", "")
            binding = j.get("binding", "")
            corr = j.get("correlation_id", "")
            if not all(isinstance(x, str) for x in [rr, ctx, domain, binding, corr]):
                self.send_response(204)
                self.end_headers()
                return
        else:
            # requester -> hub: compute rr + mechanical bind
            ctx = self.headers.get("X-Verification-Context", "") or ""
            domain = self.headers.get("X-Domain", "") or ""
            rr = sha256_hex(raw)
            binding = mechanical_bind(rr, ctx, domain)
            corr = correlation_id_from(self.hub_id, rr, domain)

        with LOCK:
            HUB_ACCEPTED += 1

        providers, hubs = routing_plan(domain)

        # Fanout to providers (mechanical)
        for pid in providers:
            url = PROVIDER_MAP.get(pid)
            if not url:
                continue
            forward = {
                "hub_id": self.hub_id,
                "correlation_id": corr,
                "request_repr": rr,
                "verification_context": ctx,
                "domain": domain,
                "binding": binding,
                "return_outcome_url": self.local_outcome_url,
            }
            fire_and_forget_post(url, forward)
            with LOCK:
                HUB_ROUTED_TO_PROVIDER += 1

        # Relay to peer hubs (mechanical)
        for hid in hubs:
            if hid == self.hub_id:
                continue
            submit_url = HUB_MAP.get(hid)
            if not submit_url:
                continue
            relay = {
                "from_hub": self.hub_id,
                "correlation_id": corr,
                "request_repr": rr,
                "verification_context": ctx,
                "domain": domain,
                "binding": binding,
            }
            fire_and_forget_post(submit_url, relay)
            with LOCK:
                HUB_RELAYED_TO_HUB += 1

        self.send_response(204)
        self.end_headers()

    def _handle_outcome(self):
        global OUTCOME_TOTAL, OUTCOME_INITIATED, OUTCOME_NOT_INITIATED

        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_REQUEST_BYTES:
            self.send_response(204)
            self.end_headers()
            return

        body = self.rfile.read(length) if length > 0 else b""
        try:
            msg = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            msg = {}

        pid = str(msg.get("provider_id", ""))
        domain = str(msg.get("domain", ""))
        initiated = bool(msg.get("provider_initiated", False))
        corr = str(msg.get("correlation_id", ""))

        with LOCK:
            OUTCOME_TOTAL += 1
            if initiated:
                OUTCOME_INITIATED += 1
            else:
                OUTCOME_NOT_INITIATED += 1
            if pid in OUTCOME_BY_PROVIDER:
                if initiated:
                    OUTCOME_BY_PROVIDER[pid]["init"] += 1
                else:
                    OUTCOME_BY_PROVIDER[pid]["no"] += 1

        bump_domain(domain, initiated)

        if PRINT_HUB_RELAY_LINES and pid and corr:
            print(f"{self.hub_id}: RELAYED provider={pid} domain={domain} initiated={initiated} corr={corr[:12]}...")

        self.send_response(204)
        self.end_headers()

def make_hub(hub_id: str, host: str, port: int, local_outcome_url: str) -> HTTPServer:
    handler_cls = type(f"{hub_id}Handler", (HubHandler,), {"hub_id": hub_id, "local_outcome_url": local_outcome_url})
    return HTTPServer((host, port), handler_cls)

# ============================================================
# REQUESTER (benchmark driver)
# ============================================================
def requester_send(payload: bytes, verification_context: str, domain: str, hub_submit_url: str) -> int:
    req = urllib.request.Request(
        hub_submit_url,
        data=payload,
        headers={
            "Connection": "close",
            "Content-Type": "application/octet-stream",
            "X-Verification-Context": verification_context,
            "X-Domain": domain,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=2) as resp:
        return resp.status

def start_server(server: HTTPServer) -> None:
    server.serve_forever()

def run_benchmark() -> Dict[str, float]:
    global REQ_SENT, REQ_CTX_SPOOFED, REQ_DOMAIN_UNKNOWN, REQ_OVERSIZED

    if RANDOM_SEED is None:
        random.seed()
    else:
        random.seed(RANDOM_SEED)

    payload_ok = b'{"op":"transfer","amount":100,"to":"acct_123"}'
    oversize_payload = b"A" * (MAX_REQUEST_BYTES + 1)

    t0 = time.perf_counter()
    ok_204 = 0

    for _ in range(TOTAL_REQUESTS):
        with LOCK:
            REQ_SENT += 1

        # choose context
        if random.random() < SPOOF_RATE:
            ctx = "CTX_SPOOFED"
            with LOCK:
                REQ_CTX_SPOOFED += 1
        else:
            ctx = EXPECTED_CONTEXT

        # choose domain
        if random.random() < UNKNOWN_DOMAIN_RATE:
            dom = "unknown_domain"
            with LOCK:
                REQ_DOMAIN_UNKNOWN += 1
        else:
            dom = random.choice(DOMAINS)

        # choose payload size
        if random.random() < OVERSIZE_RATE:
            payload = oversize_payload
            with LOCK:
                REQ_OVERSIZED += 1
        else:
            payload = payload_ok

        try:
            st = requester_send(payload, ctx, dom, HUB_A_SUBMIT_URL)
            if st == 204:
                ok_204 += 1
        except Exception:
            # requester transport errors are still observable, but we keep output clean
            pass

    t1 = time.perf_counter()
    total_ms = (t1 - t0) * 1000.0
    avg_ms = total_ms / max(1, TOTAL_REQUESTS)

    return {"total_ms": total_ms, "avg_ms": avg_ms, "ok_204": float(ok_204)}

# ============================================================
# MAIN
# ============================================================
def main():
    # Servers
    provider_a = make_provider("PROVIDER_A", PROVIDER_A_PORT)
    provider_b = make_provider("PROVIDER_B", PROVIDER_B_PORT)
    provider_c = make_provider("PROVIDER_C", PROVIDER_C_PORT)

    hub_a = make_hub("HUB_A", HUB_A_HOST, HUB_A_PORT, HUB_A_OUTCOME_URL)
    hub_b = make_hub("HUB_B", HUB_B_HOST, HUB_B_PORT, HUB_B_OUTCOME_URL)

    threading.Thread(target=start_server, args=(provider_a,), daemon=True).start()
    threading.Thread(target=start_server, args=(provider_b,), daemon=True).start()
    threading.Thread(target=start_server, args=(provider_c,), daemon=True).start()
    threading.Thread(target=start_server, args=(hub_a,), daemon=True).start()
    threading.Thread(target=start_server, args=(hub_b,), daemon=True).start()

    time.sleep(0.6)

    size_bytes = os.path.getsize(__file__)
    print(f"Reference size: {size_bytes} bytes ({size_bytes/1024:.1f} KiB)")
    print(f"Ports: HUB_A={HUB_A_PORT} HUB_B={HUB_B_PORT} PROVIDERS={PROVIDER_A_PORT},{PROVIDER_B_PORT},{PROVIDER_C_PORT}")
    if RANDOM_SEED is not None:
        print(f"Deterministic seed: {RANDOM_SEED}")
    print()

    # Run requester benchmark (times only hub 204 response path)
    r = run_benchmark()

    # Allow async forwards + outcomes to land
    time.sleep(1.0)

    # Print compact summary
    with LOCK:
        sent = REQ_SENT
        spoof = REQ_CTX_SPOOFED
        unk = REQ_DOMAIN_UNKNOWN
        over = REQ_OVERSIZED
        accepted = HUB_ACCEPTED
        routed_p = HUB_ROUTED_TO_PROVIDER
        relayed_h = HUB_RELAYED_TO_HUB
        out_total = OUTCOME_TOTAL
        out_init = OUTCOME_INITIATED
        out_no = OUTCOME_NOT_INITIATED
        byp = dict(OUTCOME_BY_PROVIDER)
        byd = dict(OUTCOME_BY_DOMAIN)

    print("=" * 62)
    print("MULTI-HUB + MULTI-DOMAIN BENCHMARK SUMMARY")
    print("=" * 62)
    print(f"Requests sent (requester):          {sent}")
    print(f"  Spoofed context (requester):      {spoof}")
    print(f"  Unknown domain (requester):       {unk}")
    print(f"  Oversized dropped at hub:         {over}")
    print(f"Hub accepted (/submit):             {accepted}")
    print(f"Hub fanout -> provider posts:       {routed_p}")
    print(f"Hub relay -> peer hub posts:        {relayed_h}")
    print(f"Requester timing (hub 204 only):")
    print(f"  Total time:                       {r['total_ms']:.2f} ms")
    print(f"  Avg per request:                  {r['avg_ms']:.4f} ms")
    print(f"Provider outcome signals observed:")
    print(f"  Total outcomes received:          {out_total}")
    print(f"  Initiated:                        {out_init}")
    print(f"  Not initiated:                    {out_no}")
    print("Outcomes by provider (init/no):")
    for pid in ["PROVIDER_A", "PROVIDER_B", "PROVIDER_C"]:
        print(f"  {pid}: {byp[pid]['init']}/{byp[pid]['no']}")
    if byd:
        print("Outcomes by domain (init/no):")
        for dom, counts in sorted(byd.items()):
            print(f"  {dom}: {counts['init']}/{counts['no']}")
    print("=" * 62)
    print()
    print("Done (servers stay up).")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
