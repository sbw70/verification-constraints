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
import os
import random
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

# ============================================================
# CONFIG
# ============================================================

TOTAL_REQUESTS = 100
RANDOM_SEED = 1337  # set None for nondeterministic

DOMAINS = ["payments", "identity", "storage"]
EXPECTED_CONTEXT = "CTX_ALPHA"

# Randomized during run (so it "looks real"):
FAILOVER_MIN = 35
FAILOVER_MAX = 65

BYZANTINE_MIN = 60
BYZANTINE_MAX = 95

QUORUM_THRESHOLD = 2  # 2-of-3

# Region A
NUVL_A_PORT = 8000
HUB_A_PORT = 8100

# Region B
NUVL_B_PORT = 8001
HUB_B_PORT = 8101

AUDITOR_PORT = 8200

PROVIDER_PORTS = {
    "PROVIDER_A": 9001,
    "PROVIDER_B": 9002,
    "PROVIDER_C": 9003,
}

# Provider authority (provider-only in real deployments; demo keeps them local)
PROVIDER_KEYS = {
    "PROVIDER_A": b"A_KEY",
    "PROVIDER_B": b"B_KEY",
    "PROVIDER_C": b"C_KEY",
}

# Domain-specific thresholds (provider-controlled)
PROVIDER_THRESHOLDS = {
    "payments": 0.55,
    "identity": 0.60,
    "storage": 0.50,
}

# Transport tuning (prevents "can't start new thread")
MAX_WORKERS = 64
HTTP_TIMEOUT_S = 2.0

# ============================================================
# Thread-safe counters / state
# ============================================================

CURRENT_REQUEST_INDEX = 0
CURRENT_LOCK = threading.Lock()

HUB_RELAY_COUNTS = {"HUB_A": 0, "HUB_B": 0}
HUB_LOCK = threading.Lock()

PROVIDER_INIT_COUNTS = {k: 0 for k in PROVIDER_PORTS}
PROVIDER_INIT_BY_DOMAIN = {
    "PROVIDER_A": {d: 0 for d in DOMAINS},
    "PROVIDER_B": {d: 0 for d in DOMAINS},
    "PROVIDER_C": {d: 0 for d in DOMAINS},
}
PROVIDER_LOCK = threading.Lock()

AUDIT_LOG = {}  # rr -> list[bool]
AUDIT_LOCK = threading.Lock()
SIGNED_OUTCOMES = 0
BAD_SIGNATURES = 0
QUORUM_SUCCESS = 0
QUORUM_FAIL = 0

# ============================================================
# HTTP helpers (bounded async)
# ============================================================

_POOL = ThreadPoolExecutor(max_workers=MAX_WORKERS)

def _post_json(url: str, payload: dict) -> None:
    data = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Connection": "close", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S):
        pass

def fire_and_forget(url: str, payload: dict) -> None:
    # bounded concurrency via thread pool (no per-request thread explosion)
    try:
        _POOL.submit(_post_json, url, payload)
    except Exception:
        pass

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

# ============================================================
# PROVIDERS (extension module: provider-only decision + signature)
# ============================================================

def provider_score(pid: str, rr: str, ctx: str, domain: str) -> float:
    seed = PROVIDER_KEYS[pid]
    material = f"{pid}|{domain}|{rr}|{ctx}".encode("utf-8")
    digest = hmac.new(seed, material, hashlib.sha256).digest()
    n = int.from_bytes(digest[:8], "big")
    base = (n % 10_000_000) / 10_000_000.0
    if ctx == EXPECTED_CONTEXT:
        base += 0.15
    return min(base, 1.0)

def sign(pid: str, rr: str) -> str:
    return hmac.new(PROVIDER_KEYS[pid], rr.encode("utf-8"), hashlib.sha256).hexdigest()

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class ProviderHandler(BaseHTTPRequestHandler):
    provider_id = "PROVIDER_X"
    byzantine_flip_at = 10**9  # set at runtime

    def log_message(self, *args):  # quiet
        return

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b""
            msg = json.loads(raw.decode("utf-8"))

            rr = msg.get("request_repr", "")
            ctx = msg.get("verification_context", "")
            domain = msg.get("domain", "payments")

            s = provider_score(self.provider_id, rr, ctx, domain)
            initiated = bool(s >= PROVIDER_THRESHOLDS.get(domain, 0.60))

            # extension: Byzantine injection (flip after randomized index)
            with CURRENT_LOCK:
                idx = CURRENT_REQUEST_INDEX
            if self.provider_id == "PROVIDER_C" and idx >= self.byzantine_flip_at:
                initiated = not initiated

            if initiated:
                with PROVIDER_LOCK:
                    PROVIDER_INIT_COUNTS[self.provider_id] += 1
                    if domain in PROVIDER_INIT_BY_DOMAIN[self.provider_id]:
                        PROVIDER_INIT_BY_DOMAIN[self.provider_id][domain] += 1

            # provider emits signed outcome to non-authoritative auditor
            fire_and_forget(
                f"http://127.0.0.1:{AUDITOR_PORT}/audit",
                {
                    "provider": self.provider_id,
                    "request_repr": rr,
                    "domain": domain,
                    "initiated": initiated,
                    "signature": sign(self.provider_id, rr),
                },
            )
        except Exception:
            pass

        self.send_response(204)
        self.end_headers()

def make_provider_server(pid: str, port: int, byz_flip_at: int) -> ThreadingHTTPServer:
    handler = type(f"{pid}Handler", (ProviderHandler,), {"provider_id": pid, "byzantine_flip_at": byz_flip_at})
    return ThreadingHTTPServer(("0.0.0.0", port), handler)

# ============================================================
# HUBS (extension module: multi-hub relay mesh, mechanical fanout)
# ============================================================

class HubHandler(BaseHTTPRequestHandler):
    hub_name = "HUB_X"
    peer_hub_url = None  # set on class
    fanout_provider_urls = []  # set on class
    auditor_url = None  # optional (not used here)

    def log_message(self, *args):
        return

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b""
            msg = json.loads(raw.decode("utf-8"))

            # fanout to providers (mechanical)
            for url in self.fanout_provider_urls:
                fire_and_forget(url, msg)

            # peer relay (mechanical)
            if self.peer_hub_url:
                with HUB_LOCK:
                    HUB_RELAY_COUNTS[self.hub_name] += 1
                fire_and_forget(self.peer_hub_url, msg)
        except Exception:
            pass

        self.send_response(204)
        self.end_headers()

def make_hub_server(hub_name: str, port: int, peer_hub_url: str, provider_urls: list) -> ThreadingHTTPServer:
    handler = type(
        f"{hub_name}Handler",
        (HubHandler,),
        {
            "hub_name": hub_name,
            "peer_hub_url": peer_hub_url,
            "fanout_provider_urls": provider_urls,
        },
    )
    return ThreadingHTTPServer(("0.0.0.0", port), handler)

# ============================================================
# NUVL FRONTS (core: representation + forward, no outcomes)
# ============================================================

class NUVLHandler(BaseHTTPRequestHandler):
    hub_url = None  # set on class

    def log_message(self, *args):
        return

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b""

            rr = sha256_hex(raw)
            ctx = self.headers.get("X-Verification-Context", "")
            domain = self.headers.get("X-Domain", "payments")

            # core: forward representation only, constant response
            fire_and_forget(
                self.hub_url,
                {"request_repr": rr, "verification_context": ctx, "domain": domain},
            )
        except Exception:
            pass

        self.send_response(204)
        self.end_headers()

def make_nuvl_server(port: int, hub_port: int) -> ThreadingHTTPServer:
    handler = type(
        f"NUVL_{port}Handler",
        (NUVLHandler,),
        {"hub_url": f"http://127.0.0.1:{hub_port}/hub"},
    )
    return ThreadingHTTPServer(("0.0.0.0", port), handler)

# ============================================================
# AUDITOR (extension module: non-authoritative quorum aggregation)
# ============================================================

class AuditorHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def do_POST(self):
        global SIGNED_OUTCOMES, BAD_SIGNATURES, QUORUM_SUCCESS, QUORUM_FAIL

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b""
            msg = json.loads(raw.decode("utf-8"))

            rr = msg.get("request_repr", "")
            pid = msg.get("provider", "")
            initiated = bool(msg.get("initiated", False))
            sig = msg.get("signature", "")

            if pid not in PROVIDER_KEYS:
                self.send_response(204); self.end_headers(); return

            # verify provider signature (auditor trusts only provider keys, not timing/endpoints)
            if sig != sign(pid, rr):
                with AUDIT_LOCK:
                    BAD_SIGNATURES += 1
                self.send_response(204); self.end_headers(); return

            with AUDIT_LOCK:
                SIGNED_OUTCOMES += 1
                AUDIT_LOG.setdefault(rr, []).append(initiated)
                if len(AUDIT_LOG[rr]) == 3:
                    if sum(1 for x in AUDIT_LOG[rr] if x) >= QUORUM_THRESHOLD:
                        QUORUM_SUCCESS += 1
                    else:
                        QUORUM_FAIL += 1
        except Exception:
            pass

        self.send_response(204)
        self.end_headers()

def make_auditor_server() -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("0.0.0.0", AUDITOR_PORT), AuditorHandler)

# ============================================================
# REQUESTER (extension module: region failover + randomized flips)
# ============================================================

def requester_send(port: int, payload: bytes, ctx: str, domain: str) -> None:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}/nuvl",
        data=payload,
        headers={
            "Connection": "close",
            "Content-Type": "application/octet-stream",
            "X-Verification-Context": ctx,
            "X-Domain": domain,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S):
        pass

def run_benchmark(failover_at: int, byzantine_flip_at: int) -> float:
    global CURRENT_REQUEST_INDEX

    start = time.perf_counter()
    http_ok = 0
    http_err = 0

    for i in range(TOTAL_REQUESTS):
        with CURRENT_LOCK:
            CURRENT_REQUEST_INDEX = i

        region_port = NUVL_A_PORT if i < failover_at else NUVL_B_PORT

        # 10% spoofed context (looks like "someone jumped in")
        ctx = EXPECTED_CONTEXT if random.random() > 0.10 else "SPOOF"
        domain = random.choice(DOMAINS)
        payload = json.dumps({"i": i, "ts": time.time_ns()}, separators=(",", ":")).encode("utf-8")

        try:
            requester_send(region_port, payload, ctx, domain)
            http_ok += 1
        except Exception:
            http_err += 1

    elapsed_ms = (time.perf_counter() - start) * 1000.0

    # let async forwards settle
    time.sleep(1.5)

    return elapsed_ms, http_ok, http_err

# ============================================================
# MAIN
# ============================================================

def start(server):
    server.serve_forever()

def main():
    if RANDOM_SEED is None:
        random.seed()
    else:
        random.seed(RANDOM_SEED)

    # randomized points (but bounded)
    failover_at = random.randint(max(1, FAILOVER_MIN), min(TOTAL_REQUESTS - 1, FAILOVER_MAX))
    byzantine_flip_at = random.randint(max(0, BYZANTINE_MIN), min(TOTAL_REQUESTS - 1, BYZANTINE_MAX))

    # Provider URLs
    provider_urls = [f"http://127.0.0.1:{p}/ingest" for p in PROVIDER_PORTS.values()]

    # Start providers (C becomes byzantine after flip index)
    for pid, port in PROVIDER_PORTS.items():
        flip = byzantine_flip_at if pid == "PROVIDER_C" else 10**9
        srv = make_provider_server(pid, port, flip)
        threading.Thread(target=start, args=(srv,), daemon=True).start()

    # Start auditor
    threading.Thread(target=start, args=(make_auditor_server(),), daemon=True).start()

    # Start hubs (each relays to the other)
    hub_a = make_hub_server(
        "HUB_A",
        HUB_A_PORT,
        peer_hub_url=f"http://127.0.0.1:{HUB_B_PORT}/hub",
        provider_urls=provider_urls,
    )
    hub_b = make_hub_server(
        "HUB_B",
        HUB_B_PORT,
        peer_hub_url=f"http://127.0.0.1:{HUB_A_PORT}/hub",
        provider_urls=provider_urls,
    )
    threading.Thread(target=start, args=(hub_a,), daemon=True).start()
    threading.Thread(target=start, args=(hub_b,), daemon=True).start()

    # Start NUVLs (each fronts one hub)
    nuvl_a = make_nuvl_server(NUVL_A_PORT, HUB_A_PORT)
    nuvl_b = make_nuvl_server(NUVL_B_PORT, HUB_B_PORT)
    threading.Thread(target=start, args=(nuvl_a,), daemon=True).start()
    threading.Thread(target=start, args=(nuvl_b,), daemon=True).start()

    time.sleep(0.8)

    size_bytes = os.path.getsize(__file__)
    print(f"Reference size: {size_bytes} bytes ({size_bytes/1024:.1f} KiB)\n")

    elapsed_ms, http_ok, http_err = run_benchmark(failover_at, byzantine_flip_at)

    # Print summary (no spam)
    print("===== MULTI-HUB + MULTI-DOMAIN (FAILOVER + QUORUM) =====")
    print(f"Total requests:        {TOTAL_REQUESTS}")
    print(f"Failover at index:     {failover_at}")
    print(f"Byzantine provider:    PROVIDER_C (flip at {byzantine_flip_at})")
    print(f"HTTP ok:               {http_ok}, errors: {http_err}")
    print(f"Total time:            {elapsed_ms:.2f} ms")
    print(f"Avg per request:       {elapsed_ms/float(TOTAL_REQUESTS):.4f} ms\n")

    with HUB_LOCK:
        print("Hub Relay Counts (peer relays issued):")
        print(f"HUB_A relays: {HUB_RELAY_COUNTS['HUB_A']}")
        print(f"HUB_B relays: {HUB_RELAY_COUNTS['HUB_B']}\n")

    with PROVIDER_LOCK:
        print("Provider Initiations (total):")
        for k, v in PROVIDER_INIT_COUNTS.items():
            print(f"{k}: {v}")
        print("\nProvider Initiations (by domain):")
        for pid in ["PROVIDER_A", "PROVIDER_B", "PROVIDER_C"]:
            d = PROVIDER_INIT_BY_DOMAIN[pid]
            print(f"{pid}: payments={d['payments']}, identity={d['identity']}, storage={d['storage']}")
        print("")

    with AUDIT_LOCK:
        print("Auditor Results (non-authoritative aggregation):")
        print(f"Signed outcomes received: {SIGNED_OUTCOMES}")
        print(f"Bad signatures rejected:  {BAD_SIGNATURES}")
        print(f"Quorum successes:         {QUORUM_SUCCESS}")
        print(f"Quorum failures:          {QUORUM_FAIL}")
    print("========================================================\n")

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
