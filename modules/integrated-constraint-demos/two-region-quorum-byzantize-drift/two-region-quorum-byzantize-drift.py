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

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import hashlib
import hmac
import json
import threading
import time
import urllib.request
from queue import Queue, Empty
from typing import Dict, Any, Tuple

# -----------------------------
# Tunables
# -----------------------------
TOTAL_REQUESTS = 100
FAILOVER_AT = 50
MAX_REQUEST_BYTES = 1024 * 64
HTTP_TIMEOUT_S = 1.25

POST_WORKERS = 10
POST_QUEUE_MAX = 2000

# -----------------------------
# Determinism + binding
# -----------------------------
RUN_SEED = b"TWO_REGION_DETERMINISTIC_SEED"
BIND_TAG = "NUVL_BIND_V2"
EXPECTED_CONTEXT = "CTX_ALPHA"

# -----------------------------
# Region topology (ports)
# -----------------------------
HOST = "0.0.0.0"

# Region 1
NUVL_R1_PORT = 8010
HUB_R1_A_PORT = 8110
HUB_R1_B_PORT = 8111
PROV_R1_A_PORT = 8210
PROV_R1_B_PORT = 8211
PROV_R1_C_PORT = 8212

# Region 2
NUVL_R2_PORT = 8020
HUB_R2_A_PORT = 8120
HUB_R2_B_PORT = 8121
PROV_R2_A_PORT = 8220
PROV_R2_B_PORT = 8221
PROV_R2_C_PORT = 8222

def url(port: int, path: str) -> str:
    return f"http://127.0.0.1:{port}{path}"

NUVL_R1_URL = url(NUVL_R1_PORT, "/nuvl")
NUVL_R2_URL = url(NUVL_R2_PORT, "/nuvl")

HUB_R1_A_SUBMIT = url(HUB_R1_A_PORT, "/submit")
HUB_R1_A_OUTCOME = url(HUB_R1_A_PORT, "/outcome")
HUB_R1_B_SUBMIT = url(HUB_R1_B_PORT, "/submit")
HUB_R1_B_OUTCOME = url(HUB_R1_B_PORT, "/outcome")

HUB_R2_A_SUBMIT = url(HUB_R2_A_PORT, "/submit")
HUB_R2_A_OUTCOME = url(HUB_R2_A_PORT, "/outcome")
HUB_R2_B_SUBMIT = url(HUB_R2_B_PORT, "/submit")
HUB_R2_B_OUTCOME = url(HUB_R2_B_PORT, "/outcome")

PROV_R1_A_INGEST = url(PROV_R1_A_PORT, "/ingest")
PROV_R1_B_INGEST = url(PROV_R1_B_PORT, "/ingest")
PROV_R1_C_INGEST = url(PROV_R1_C_PORT, "/ingest")

PROV_R2_A_INGEST = url(PROV_R2_A_PORT, "/ingest")
PROV_R2_B_INGEST = url(PROV_R2_B_PORT, "/ingest")
PROV_R2_C_INGEST = url(PROV_R2_C_PORT, "/ingest")

# -----------------------------
# Multi-domain
# -----------------------------
DOMAINS = ["payments", "storage", "identity", "compute"]

DOMAIN_THRESHOLDS = {
    "payments": 0.70,
    "storage": 0.55,
    "identity": 0.78,
    "compute": 0.60,
}

# -----------------------------
# Provider-only secrets
# -----------------------------
PROV_KEYS = {
    "PROVIDER_A": b"PROVIDER_A_ONLY_KEY_CHANGE_ME",
    "PROVIDER_B": b"PROVIDER_B_ONLY_KEY_CHANGE_ME",
    "PROVIDER_C": b"PROVIDER_C_ONLY_KEY_CHANGE_ME",
}
PROV_MODEL_SEEDS = {
    "PROVIDER_A": b"PROVIDER_A_MODEL_SEED_CHANGE_ME",
    "PROVIDER_B": b"PROVIDER_B_MODEL_SEED_CHANGE_ME",
    "PROVIDER_C": b"PROVIDER_C_MODEL_SEED_CHANGE_ME",
}

# -----------------------------
# Threading HTTP server
# -----------------------------
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

# -----------------------------
# Small helpers
# -----------------------------
def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def hmac_hex(key: bytes, msg: bytes) -> str:
    return hmac.new(key, msg, hashlib.sha256).hexdigest()

# -----------------------------
# Apache-2.0 NUVL CORE (neutral bind + forward)
# -----------------------------
def nuvl_bind(request_repr_hex: str, verification_context: str, domain: str) -> str:
    msg = (BIND_TAG + "|" + request_repr_hex + "|" + verification_context + "|" + domain).encode("utf-8")
    return sha256_hex(msg)

# -----------------------------
# Deterministic replay harness
# -----------------------------
def deterministic_domain_for(seq: int) -> str:
    return DOMAINS[seq % len(DOMAINS)]

def make_payload(seq: int, domain: str) -> bytes:
    obj = {
        "op": "dispatch",
        "seq": seq,
        "domain": domain,
        "amount": 100 + (seq % 7),
        "to": f"acct_{1000 + (seq % 23)}",
    }
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")

def base_request_id(request_repr: str) -> str:
    return "RID_" + request_repr[:16]

def deterministic_byzantine_start(total_requests: int, failover_at: int) -> int:
    # Deterministic, but appears random. Always after failover (if possible).
    if total_requests <= 1:
        return 0
    lo = min(max(failover_at + 1, 0), total_requests - 1)
    span = max(1, total_requests - lo)
    off = int(hmac_hex(RUN_SEED, b"BYZ_START")[:2], 16) % span
    return lo + off

# -----------------------------
# POST worker pool (prevents thread explosion)
# -----------------------------
POSTQ: "Queue[Tuple[str, Dict[str, Any]]]" = Queue(maxsize=POST_QUEUE_MAX)

def _http_post_json(url_str: str, payload: Dict[str, Any], timeout_s: float = HTTP_TIMEOUT_S) -> None:
    data = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    req = urllib.request.Request(
        url_str,
        data=data,
        headers={"Content-Type": "application/json", "Connection": "close"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout_s):
        pass

def post_worker() -> None:
    while True:
        try:
            u, p = POSTQ.get(timeout=1.0)
        except Empty:
            continue
        try:
            _http_post_json(u, p, timeout_s=HTTP_TIMEOUT_S)
        except Exception:
            pass
        finally:
            POSTQ.task_done()

def fire_and_forget_post(url_str: str, payload: Dict[str, Any]) -> None:
    try:
        POSTQ.put_nowait((url_str, payload))
    except Exception:
        return

def start_post_pool() -> None:
    for _ in range(POST_WORKERS):
        threading.Thread(target=post_worker, daemon=True).start()

# -----------------------------
# Auditor (observer-only) - quorum + per-domain results
# -----------------------------
class Auditor:
    def __init__(self):
        self._lock = threading.Lock()
        self._seen: Dict[str, Dict[str, bool]] = {}
        self.quorum_success = 0
        self.quorum_fail = 0
        self.by_domain: Dict[str, Dict[str, int]] = {d: {"success": 0, "fail": 0} for d in DOMAINS}

    def observe(self, base_rid: str, domain: str, provider_id: str, initiated: bool) -> None:
        with self._lock:
            if base_rid not in self._seen:
                self._seen[base_rid] = {}
            self._seen[base_rid][provider_id] = bool(initiated)
            if len(self._seen[base_rid]) == 3:
                votes = list(self._seen[base_rid].values())
                ok = (votes.count(True) >= 2)
                if ok:
                    self.quorum_success += 1
                    self.by_domain[domain]["success"] += 1
                else:
                    self.quorum_fail += 1
                    self.by_domain[domain]["fail"] += 1

AUDITOR = Auditor()

# -----------------------------
# Providers (authority)
# -----------------------------
class ProviderHandler(BaseHTTPRequestHandler):
    provider_id = "PROVIDER_X"
    region = "R?"
    byz_start = 999999  # set at runtime

    def log_message(self, fmt, *args):
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

        request_repr = str(msg.get("request_repr", ""))
        verification_context = str(msg.get("verification_context", ""))
        domain = str(msg.get("domain", ""))
        binding = str(msg.get("binding", ""))
        return_outcome_url = str(msg.get("return_outcome_url", ""))
        seq = int(msg.get("seq", -1))

        expected = nuvl_bind(request_repr, verification_context, domain)
        binding_ok = hmac.compare_digest(binding, expected)

        material = (request_repr + "|" + verification_context + "|" + domain).encode("utf-8")
        seed = PROV_MODEL_SEEDS.get(self.provider_id, b"X")
        digest = hmac.new(seed, material, hashlib.sha256).digest()
        n = int.from_bytes(digest[:8], "big")
        score = (n % 10_000_000) / 10_000_000.0
        if verification_context == EXPECTED_CONTEXT:
            score = min(1.0, score + 0.20)

        threshold = DOMAIN_THRESHOLDS.get(domain, 0.75)
        initiated_real = bool(binding_ok and score >= threshold)

        initiated_reported = initiated_real
        # Deterministic byzantine drift: PROVIDER_B flips ~50% after byz_start
        if self.provider_id == "PROVIDER_B" and seq >= self.byz_start:
            flip_bit = int(hmac_hex(RUN_SEED, f"FLIP|{seq}".encode("utf-8"))[:2], 16) & 1
            if flip_bit == 1:
                initiated_reported = not initiated_real

        # Provider boundary artifacts (computed, not emitted here to keep output light)
        key = PROV_KEYS.get(self.provider_id, b"X")
        _ = hmac_hex(key, f"START|{request_repr}|{domain}".encode("utf-8"))
        _ = hmac_hex(key, f"COMPLETE|{request_repr}|{domain}".encode("utf-8"))

        if return_outcome_url.startswith("http"):
            out = {
                "provider_id": self.provider_id,
                "region": self.region,
                "seq": seq,
                "request_repr": request_repr,
                "domain": domain,
                "initiated": bool(initiated_reported),
            }
            fire_and_forget_post(return_outcome_url, out)

        self.send_response(204)
        self.end_headers()

def make_provider_server(region: str, provider_id: str, port: int, byz_start: int):
    handler_cls = type(
        f"{region}_{provider_id}_Handler",
        (ProviderHandler,),
        {"region": region, "provider_id": provider_id, "byz_start": byz_start},
    )
    return ThreadingHTTPServer((HOST, port), handler_cls)

# -----------------------------
# Hubs (mesh, non-authoritative)
# -----------------------------
class HubHandler(BaseHTTPRequestHandler):
    hub_id = "HUB_X"
    region = "R?"
    peer_submit_url = ""
    outcome_url = ""
    providers: Dict[str, str] = {}

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
        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_REQUEST_BYTES:
            self.send_response(204)
            self.end_headers()
            return

        raw = self.rfile.read(length) if length > 0 else b""
        ctype = (self.headers.get("Content-Type", "") or "").lower()

        if "application/json" in ctype:
            try:
                j = json.loads(raw.decode("utf-8"))
            except Exception:
                self.send_response(204)
                self.end_headers()
                return
            request_repr = str(j.get("request_repr", ""))
            verification_context = str(j.get("verification_context", ""))
            domain = str(j.get("domain", ""))
            binding = str(j.get("binding", ""))
            seq = int(j.get("seq", -1))
            base_rid = str(j.get("base_rid", ""))
        else:
            request_repr = sha256_hex(raw)
            verification_context = self.headers.get("X-Verification-Context", "")
            domain = self.headers.get("X-Domain", "")
            binding = nuvl_bind(request_repr, verification_context, domain)
            seq = int(self.headers.get("X-Seq", "-1"))
            base_rid = base_request_id(request_repr)

        for _, purl in self.providers.items():
            fwd = {
                "hub_id": self.hub_id,
                "region": self.region,
                "seq": seq,
                "base_rid": base_rid,
                "request_repr": request_repr,
                "verification_context": verification_context,
                "domain": domain,
                "binding": binding,
                "return_outcome_url": self.outcome_url,
            }
            fire_and_forget_post(purl, fwd)

        if self.peer_submit_url.startswith("http"):
            relay = {
                "from_hub": self.hub_id,
                "region": self.region,
                "seq": seq,
                "base_rid": base_rid,
                "request_repr": request_repr,
                "verification_context": verification_context,
                "domain": domain,
                "binding": binding,
            }
            fire_and_forget_post(self.peer_submit_url, relay)

        self.send_response(204)
        self.end_headers()

    def _handle_outcome(self):
        msg = self._read_json()
        if not msg:
            self.send_response(204)
            self.end_headers()
            return

        pid = str(msg.get("provider_id", ""))
        initiated = bool(msg.get("initiated", False))
        request_repr = str(msg.get("request_repr", ""))
        domain = str(msg.get("domain", ""))

        base_rid = base_request_id(request_repr)
        AUDITOR.observe(base_rid, domain, pid, initiated)

        self.send_response(204)
        self.end_headers()

def make_hub_server(region: str, hub_id: str, port: int, peer_submit_url: str, outcome_url: str, providers: Dict[str, str]):
    handler_cls = type(
        f"{region}_{hub_id}_Handler",
        (HubHandler,),
        {"region": region, "hub_id": hub_id, "peer_submit_url": peer_submit_url, "outcome_url": outcome_url, "providers": providers},
    )
    return ThreadingHTTPServer((HOST, port), handler_cls)

# -----------------------------
# NUVL fronts (neutral)
# -----------------------------
class NUVLHandler(BaseHTTPRequestHandler):
    region = "R?"
    hub_submit_url = ""

    def log_message(self, fmt, *args):
        return

    def do_POST(self):
        if self.path != "/nuvl":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_REQUEST_BYTES:
            self.send_response(204)
            self.end_headers()
            return

        request_bytes = self.rfile.read(length) if length > 0 else b""
        verification_context = self.headers.get("X-Verification-Context", "")
        domain = self.headers.get("X-Domain", "")
        seq = int(self.headers.get("X-Seq", "0"))

        request_repr = sha256_hex(request_bytes)
        binding = nuvl_bind(request_repr, verification_context, domain)
        base_rid = base_request_id(request_repr)

        artifact = {
            "region": self.region,
            "seq": seq,
            "base_rid": base_rid,
            "request_repr": request_repr,
            "verification_context": verification_context,
            "domain": domain,
            "binding": binding,
        }
        fire_and_forget_post(self.hub_submit_url, artifact)

        self.send_response(204)
        self.end_headers()

def make_nuvl_server(region: str, port: int, hub_submit_url: str):
    handler_cls = type(
        f"{region}_NUVL_Handler",
        (NUVLHandler,),
        {"region": region, "hub_submit_url": hub_submit_url},
    )
    return ThreadingHTTPServer((HOST, port), handler_cls)

# -----------------------------
# Requester (benchmark driver)
# -----------------------------
def requester_send(nuvl_url: str, payload: bytes, seq: int, verification_context: str, domain: str) -> int:
    req = urllib.request.Request(
        nuvl_url,
        data=payload,
        headers={
            "Content-Type": "application/octet-stream",
            "X-Verification-Context": verification_context,
            "X-Domain": domain,
            "X-Seq": str(seq),
            "Connection": "close",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S) as resp:
        return int(resp.status)

def start_server(server: HTTPServer) -> None:
    server.serve_forever()

def main():
    start_post_pool()

    byz_start = deterministic_byzantine_start(TOTAL_REQUESTS, FAILOVER_AT)

    provs_r1 = {"PROVIDER_A": PROV_R1_A_INGEST, "PROVIDER_B": PROV_R1_B_INGEST, "PROVIDER_C": PROV_R1_C_INGEST}
    provs_r2 = {"PROVIDER_A": PROV_R2_A_INGEST, "PROVIDER_B": PROV_R2_B_INGEST, "PROVIDER_C": PROV_R2_C_INGEST}

    servers = [
        make_provider_server("R1", "PROVIDER_A", PROV_R1_A_PORT, byz_start),
        make_provider_server("R1", "PROVIDER_B", PROV_R1_B_PORT, byz_start),
        make_provider_server("R1", "PROVIDER_C", PROV_R1_C_PORT, byz_start),
        make_provider_server("R2", "PROVIDER_A", PROV_R2_A_PORT, byz_start),
        make_provider_server("R2", "PROVIDER_B", PROV_R2_B_PORT, byz_start),
        make_provider_server("R2", "PROVIDER_C", PROV_R2_C_PORT, byz_start),

        make_hub_server("R1", "HUB_R1_A", HUB_R1_A_PORT, HUB_R1_B_SUBMIT, HUB_R1_A_OUTCOME, provs_r1),
        make_hub_server("R1", "HUB_R1_B", HUB_R1_B_PORT, HUB_R1_A_SUBMIT, HUB_R1_B_OUTCOME, provs_r1),
        make_hub_server("R2", "HUB_R2_A", HUB_R2_A_PORT, HUB_R2_B_SUBMIT, HUB_R2_A_OUTCOME, provs_r2),
        make_hub_server("R2", "HUB_R2_B", HUB_R2_B_PORT, HUB_R2_A_SUBMIT, HUB_R2_B_OUTCOME, provs_r2),

        make_nuvl_server("R1", NUVL_R1_PORT, HUB_R1_A_SUBMIT),
        make_nuvl_server("R2", NUVL_R2_PORT, HUB_R2_A_SUBMIT),
    ]

    for s in servers:
        threading.Thread(target=start_server, args=(s,), daemon=True).start()

    time.sleep(0.75)

    t0 = time.time()
    ok = 0
    err = 0

    for seq in range(TOTAL_REQUESTS):
        domain = deterministic_domain_for(seq)
        payload = make_payload(seq, domain)
        active_nuvl = NUVL_R1_URL if seq < FAILOVER_AT else NUVL_R2_URL
        try:
            st = requester_send(active_nuvl, payload, seq, EXPECTED_CONTEXT, domain)
            if st == 204:
                ok += 1
            else:
                err += 1
        except Exception:
            err += 1

    time.sleep(1.25)

    elapsed_ms = (time.time() - t0) * 1000.0
    avg_ms = elapsed_ms / max(1, TOTAL_REQUESTS)

    print("===== TWO-REGION / TWO-NUVL / TWO-MESH / QUORUM AUDIT =====")
    print(f"Total requests: {TOTAL_REQUESTS}")
    print(f"Failover at:    {FAILOVER_AT} (Region1 -> Region2)")
    print(f"Byzantine at:   {byz_start} (Provider_B drift begins)")
    print(f"HTTP ok:        {ok}, errors: {err}")
    print(f"Total time:     {elapsed_ms:.2f} ms")
    print(f"Avg/request:    {avg_ms:.4f} ms")
    print("")
    print("Auditor Results (2-of-3 quorum on initiated signals):")
    print(f"Quorum successes: {AUDITOR.quorum_success}")
    print(f"Quorum failures:  {AUDITOR.quorum_fail}")
    print("")
    print("By domain:")
    for d in DOMAINS:
        s = AUDITOR.by_domain[d]["success"]
        f = AUDITOR.by_domain[d]["fail"]
        print(f"  {d:>9}: success={s:3d} fail={f:3d}")
    print("==========================================================")

    time.sleep(0.5)

if __name__ == "__main__":
    main()
