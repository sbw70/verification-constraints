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

from http.server import BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from http.server import HTTPServer
import hashlib
import hmac
import json
import threading
import time
import urllib.request
from queue import Queue, Empty
from typing import Dict, Any, Tuple

# -----------------------------
# Tunables (Replit-friendly)
# -----------------------------
TOTAL_REQUESTS = 100
OFFLINE_FIRST_N = 60               # provider offline for first N requests
MAX_REQUEST_BYTES = 1024 * 64
HTTP_TIMEOUT_S = 1.25
POST_WORKERS = 8
POST_QUEUE_MAX = 1000

# -----------------------------
# Topology
# -----------------------------
HOST = "0.0.0.0"
NUVL_PORT = 8300
RELAY_PORT = 8310                   # offline buffer (conveyance-only)
PROVIDER_PORT = 8320                # authoritative provider boundary
UPLINK_INTERVAL_S = 0.15            # how often uplink attempts delivery when online

NUVL_URL = f"http://127.0.0.1:{NUVL_PORT}/nuvl"
RELAY_INGEST_URL = f"http://127.0.0.1:{RELAY_PORT}/relay"
PROVIDER_INGEST_URL = f"http://127.0.0.1:{PROVIDER_PORT}/ingest"

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

# -----------------------------
# Mechanical binding (NUVL core)
# -----------------------------
BIND_TAG = "NUVL_BIND_V1"
EXPECTED_CONTEXT = "CTX_ALPHA"

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def nuvl_bind(request_repr_hex: str, verification_context: str, domain: str) -> str:
    msg = (BIND_TAG + "|" + request_repr_hex + "|" + verification_context + "|" + domain).encode("utf-8")
    return sha256_hex(msg)

# -----------------------------
# Provider-only secret (provider boundary)
# -----------------------------
PROVIDER_KEY = b"PROVIDER_ONLY_KEY_CHANGE_ME"

def provider_boundary_sig(request_repr_hex: str, domain: str) -> str:
    msg = (request_repr_hex + "|" + domain).encode("utf-8")
    return hmac.new(PROVIDER_KEY, msg, hashlib.sha256).hexdigest()

# -----------------------------
# POST worker pool (prevents thread explosion)
# -----------------------------
POSTQ: "Queue[Tuple[str, Dict[str, Any]]]" = Queue(maxsize=POST_QUEUE_MAX)

def _http_post_json(url: str, payload: Dict[str, Any], timeout_s: float = HTTP_TIMEOUT_S) -> None:
    data = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    req = urllib.request.Request(
        url,
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

def fire_and_forget_post(url: str, payload: Dict[str, Any]) -> None:
    try:
        POSTQ.put_nowait((url, payload))
    except Exception:
        return

def start_post_pool() -> None:
    for _ in range(POST_WORKERS):
        threading.Thread(target=post_worker, daemon=True).start()

# ============================================================
# Offline/Air-Gap extension (conveyance buffer)
# ============================================================
_RELAY_LOCK = threading.Lock()
_RELAY_BUFFER: "list[Dict[str, Any]]" = []

class RelayHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def do_POST(self):
        if self.path != "/relay":
            self.send_response(404); self.end_headers(); return

        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_REQUEST_BYTES:
            self.send_response(204); self.end_headers(); return

        body = self.rfile.read(length) if length > 0 else b""
        try:
            artifact = json.loads(body.decode("utf-8"))
        except Exception:
            self.send_response(204); self.end_headers(); return

        with _RELAY_LOCK:
            _RELAY_BUFFER.append(artifact)

        self.send_response(204)
        self.end_headers()

def start_relay():
    ThreadingHTTPServer((HOST, RELAY_PORT), RelayHandler).serve_forever()

# ============================================================
# Temporal Gatekeeping extension (provider authority)
# ============================================================
_PROVIDER_LOCK = threading.Lock()
_PROVIDER_ONLINE = False
_PROVIDER_SEEN = 0
_PROVIDER_INITIATED = 0
_PROVIDER_BIND_FAIL = 0

class ProviderHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def do_POST(self):
        global _PROVIDER_SEEN, _PROVIDER_INITIATED, _PROVIDER_BIND_FAIL

        if self.path != "/ingest":
            self.send_response(404); self.end_headers(); return

        with _PROVIDER_LOCK:
            online = _PROVIDER_ONLINE
        if not online:
            self.send_response(204); self.end_headers(); return

        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_REQUEST_BYTES:
            self.send_response(204); self.end_headers(); return

        body = self.rfile.read(length) if length > 0 else b""
        try:
            artifact = json.loads(body.decode("utf-8"))
        except Exception:
            self.send_response(204); self.end_headers(); return

        rr = str(artifact.get("request_repr", ""))
        ctx = str(artifact.get("verification_context", ""))
        domain = str(artifact.get("domain", ""))
        binding = str(artifact.get("binding", ""))

        expected = nuvl_bind(rr, ctx, domain)
        binding_ok = hmac.compare_digest(binding, expected)
        initiated = bool(binding_ok and ctx == EXPECTED_CONTEXT)

        _ = provider_boundary_sig(rr, domain)

        with _PROVIDER_LOCK:
            _PROVIDER_SEEN += 1
            if initiated:
                _PROVIDER_INITIATED += 1
            elif not binding_ok:
                _PROVIDER_BIND_FAIL += 1

        self.send_response(204)
        self.end_headers()

def start_provider():
    ThreadingHTTPServer((HOST, PROVIDER_PORT), ProviderHandler).serve_forever()

# ============================================================
# NUVL core (neutral bind + forward + disengage)
# ============================================================
class NUVLHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def do_POST(self):
        if self.path != "/nuvl":
            self.send_response(404); self.end_headers(); return

        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_REQUEST_BYTES:
            self.send_response(204); self.end_headers(); return

        raw = self.rfile.read(length) if length > 0 else b""
        ctx = self.headers.get("X-Verification-Context", "")
        domain = self.headers.get("X-Domain", "payments")

        rr = sha256_hex(raw)
        binding = nuvl_bind(rr, ctx, domain)

        artifact = {
            "request_repr": rr,
            "verification_context": ctx,
            "domain": domain,
            "binding": binding,
            "seq": int(self.headers.get("X-Seq", "0")),
        }

        fire_and_forget_post(RELAY_INGEST_URL, artifact)

        self.send_response(204)
        self.end_headers()

def start_nuvl():
    ThreadingHTTPServer((HOST, NUVL_PORT), NUVLHandler).serve_forever()

# ============================================================
# Uplink: relay -> provider (deferred transmission)
# ============================================================
_UPLINK_STOP = False
_UPLINK_SENT = 0

def uplink_loop():
    global _UPLINK_SENT
    while True:
        if _UPLINK_STOP:
            return

        with _PROVIDER_LOCK:
            online = _PROVIDER_ONLINE

        if online:
            batch = []
            with _RELAY_LOCK:
                if _RELAY_BUFFER:
                    batch = _RELAY_BUFFER[:50]
                    del _RELAY_BUFFER[:50]
            for art in batch:
                fire_and_forget_post(PROVIDER_INGEST_URL, art)
                _UPLINK_SENT += 1

        time.sleep(UPLINK_INTERVAL_S)

# ============================================================
# Requester benchmark
# ============================================================
def requester_send(seq: int, payload: bytes, ctx: str, domain: str) -> int:
    req = urllib.request.Request(
        NUVL_URL,
        data=payload,
        headers={
            "Content-Type": "application/octet-stream",
            "Connection": "close",
            "X-Verification-Context": ctx,
            "X-Domain": domain,
            "X-Seq": str(seq),
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S) as resp:
        return int(resp.status)

def main():
    start_post_pool()

    threading.Thread(target=start_relay, daemon=True).start()
    threading.Thread(target=start_provider, daemon=True).start()
    threading.Thread(target=start_nuvl, daemon=True).start()
    threading.Thread(target=uplink_loop, daemon=True).start()

    time.sleep(0.6)

    domains = ["payments", "storage", "identity"]
    payload_base = {"op": "transfer", "amount": 100, "to": "acct_123"}

    t0 = time.perf_counter()
    ok = 0
    err = 0

    global _PROVIDER_ONLINE

    for seq in range(TOTAL_REQUESTS):
        domain = domains[seq % len(domains)]
        payload = dict(payload_base)
        payload["seq"] = seq
        payload["domain"] = domain
        raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

        if seq == OFFLINE_FIRST_N:
            with _PROVIDER_LOCK:
                _PROVIDER_ONLINE = True

        ctx = EXPECTED_CONTEXT if (seq % 10 != 0) else "CTX_SPOOFED"
        try:
            st = requester_send(seq, raw, ctx, domain)
            if st == 204:
                ok += 1
            else:
                err += 1
        except Exception:
            err += 1

    time.sleep(1.2)
    POSTQ.join()

    t1 = time.perf_counter()
    total_ms = (t1 - t0) * 1000.0
    avg_ms = total_ms / max(1, TOTAL_REQUESTS)

    with _RELAY_LOCK:
        buffered_left = len(_RELAY_BUFFER)
    with _PROVIDER_LOCK:
        seen = _PROVIDER_SEEN
        initiated = _PROVIDER_INITIATED
        bind_fail = _PROVIDER_BIND_FAIL

    print("===== OFFLINE/AIR-GAP + TEMPORAL GATEKEEPING (NUVL CORE + EXT) =====")
    print(f"Total requests:         {TOTAL_REQUESTS}")
    print(f"Provider offline first: {OFFLINE_FIRST_N} requests")
    print(f"Requester saw 204:      {ok}/{TOTAL_REQUESTS} (errors={err})")
    print(f"Requester time:         {total_ms:.2f} ms (avg {avg_ms:.4f} ms/req)")
    print(f"Relay buffered left:    {buffered_left}")
    print(f"Uplink enqueued:        {_UPLINK_SENT}")
    print("")
    print("Provider (authority):")
    print(f"Artifacts seen (online): {seen}")
    print(f"Initiated (valid ctx):   {initiated}")
    print(f"Binding mismatches:      {bind_fail}")
    print("==============================================================")

if __name__ == "__main__":
    main()
