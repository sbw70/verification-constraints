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
import queue
import random
import threading
import time
import urllib.request
from typing import Dict, Any, List, Tuple

# ============================================================
# CONFIG (benchmark-grade defaults; Replit-friendly)
# ============================================================

TOTAL_REQUESTS = int(os.getenv("TOTAL_REQUESTS", "100"))
FAILOVER_AT = int(os.getenv("FAILOVER_AT", str(max(1, TOTAL_REQUESTS // 2))))
QUORUM_THRESHOLD = int(os.getenv("QUORUM_THRESHOLD", "2"))

EXPECTED_CONTEXT = os.getenv("EXPECTED_CONTEXT", "CTX_ALPHA")
DOMAINS = ["payments", "identity", "storage"]

# Randomization knobs (so the flip looks like a real incident)
RANDOM_SEED = os.getenv("RANDOM_SEED", "")
SEED = int(RANDOM_SEED) if RANDOM_SEED.strip() else None

BYZANTINE_PROVIDER = os.getenv("BYZANTINE_PROVIDER", "")
BYZANTINE_AT = os.getenv("BYZANTINE_AT", "")

# Region A
NUVL_A_PORT = int(os.getenv("NUVL_A_PORT", "8000"))
HUB_A_PORT = int(os.getenv("HUB_A_PORT", "8100"))

# Region B
NUVL_B_PORT = int(os.getenv("NUVL_B_PORT", "8001"))
HUB_B_PORT = int(os.getenv("HUB_B_PORT", "8101"))

AUDITOR_PORT = int(os.getenv("AUDITOR_PORT", "8200"))

PROVIDER_PORTS = {
    "PROVIDER_A": int(os.getenv("PROVIDER_A_PORT", "9001")),
    "PROVIDER_B": int(os.getenv("PROVIDER_B_PORT", "9002")),
    "PROVIDER_C": int(os.getenv("PROVIDER_C_PORT", "9003")),
}

MAX_REQUEST_BYTES = 1024 * 64

# ============================================================
# PROPRIETARY EXTENSIONS (demo harness + quorum + byzantine)
# ============================================================

PROVIDER_KEYS = {
    "PROVIDER_A": b"A_KEY",
    "PROVIDER_B": b"B_KEY",
    "PROVIDER_C": b"C_KEY",
}

PROVIDER_THRESHOLDS = {
    "payments": 0.55,
    "identity": 0.60,
    "storage": 0.50,
}

PROVIDER_INIT_COUNTS = {k: 0 for k in PROVIDER_PORTS}
PROVIDER_DOMAIN_COUNTS: Dict[str, Dict[str, int]] = {k: {d: 0 for d in DOMAINS} for k in PROVIDER_PORTS}
PROVIDER_LOCK = threading.Lock()

CURRENT_REQUEST_INDEX = 0
CURRENT_LOCK = threading.Lock()

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def sign(pid: str, rr: str) -> str:
    return hmac.new(PROVIDER_KEYS[pid], rr.encode(), hashlib.sha256).hexdigest()

def provider_score(pid: str, rr: str, ctx: str, domain: str) -> float:
    seed = PROVIDER_KEYS[pid]
    material = f"{pid}|{domain}|{rr}|{ctx}".encode()
    digest = hmac.new(seed, material, hashlib.sha256).digest()
    n = int.from_bytes(digest[:8], "big")
    base = (n % 10_000_000) / 10_000_000.0
    if ctx == EXPECTED_CONTEXT:
        base += 0.15
    return min(base, 1.0)

# ============================================================
# Fixed worker pool for outbound POSTs (prevents thread exhaustion)
# ============================================================

WORKER_COUNT = int(os.getenv("WORKER_COUNT", "12"))
POST_Q: "queue.Queue[Tuple[str, Dict[str, Any]]]" = queue.Queue(maxsize=int(os.getenv("POST_QUEUE_MAX", "5000")))

def post_json(url: str, payload: Dict[str, Any], timeout: float = 2.0) -> None:
    data = json.dumps(payload, separators=(",", ":")).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Connection": "close", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout):
        pass

def enqueue_post(url: str, payload: Dict[str, Any]) -> None:
    try:
        POST_Q.put_nowait((url, payload))
    except queue.Full:
        # Fail-closed: if the relay channel is saturated, drop the conveyance.
        return

def _worker() -> None:
    while True:
        url, payload = POST_Q.get()
        try:
            post_json(url, payload, timeout=2.0)
        except Exception:
            pass
        finally:
            POST_Q.task_done()

def start_workers() -> None:
    for _ in range(WORKER_COUNT):
        t = threading.Thread(target=_worker, daemon=True)
        t.start()

# ============================================================
# Auditor (non-authoritative aggregation + suspect scoring)
# ============================================================

AUDIT_LOG: Dict[str, Dict[str, bool]] = {}  # rr -> {provider: initiated}
AUDIT_LOCK = threading.Lock()
QUORUM_SUCCESS = 0
QUORUM_FAIL = 0

PROVIDER_DISAGREE: Dict[str, int] = {k: 0 for k in PROVIDER_PORTS}
PROVIDER_TOTAL_IN_QUORUM: Dict[str, int] = {k: 0 for k in PROVIDER_PORTS}

class AuditorHandler(BaseHTTPRequestHandler):
    def log_message(self, *args): return

    def do_POST(self):
        global QUORUM_SUCCESS, QUORUM_FAIL
        if self.path != "/audit":
            self.send_response(404); self.end_headers(); return

        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_REQUEST_BYTES:
            self.send_response(204); self.end_headers(); return

        try:
            msg = json.loads(self.rfile.read(length))
        except Exception:
            self.send_response(204); self.end_headers(); return

        rr = msg.get("request_repr", "")
        pid = msg.get("provider", "")
        initiated = bool(msg.get("initiated", False))
        sig = msg.get("signature", "")

        if pid not in PROVIDER_PORTS:
            self.send_response(204); self.end_headers(); return
        if sig != sign(pid, rr):
            self.send_response(204); self.end_headers(); return

        with AUDIT_LOCK:
            row = AUDIT_LOG.setdefault(rr, {})
            row[pid] = initiated

            if len(row) == 3:
                votes = sum(1 for v in row.values() if v)
                quorum_ok = votes >= QUORUM_THRESHOLD
                if quorum_ok:
                    QUORUM_SUCCESS += 1
                else:
                    QUORUM_FAIL += 1

                # disagreement scoring: provider disagrees if its vote != quorum outcome
                for p, v in row.items():
                    PROVIDER_TOTAL_IN_QUORUM[p] += 1
                    if bool(v) != bool(quorum_ok):
                        PROVIDER_DISAGREE[p] += 1

        self.send_response(204); self.end_headers()

# ============================================================
# Providers (authoritative; byzantine simulation)
# ============================================================

class ProviderHandler(BaseHTTPRequestHandler):
    provider_id = "X"
    def log_message(self, *args): return

    def do_POST(self):
        if self.path != "/ingest":
            self.send_response(404); self.end_headers(); return

        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_REQUEST_BYTES:
            self.send_response(204); self.end_headers(); return

        try:
            msg = json.loads(self.rfile.read(length))
        except Exception:
            self.send_response(204); self.end_headers(); return

        rr = msg.get("request_repr", "")
        ctx = msg.get("verification_context", "")
        domain = msg.get("domain", "payments")

        s = provider_score(self.provider_id, rr, ctx, domain)
        initiated = s >= PROVIDER_THRESHOLDS.get(domain, 0.60)

        with CURRENT_LOCK:
            idx = CURRENT_REQUEST_INDEX

        # byzantine: flip after the chosen index
        if self.provider_id == ACTIVE_BYZANTINE_PROVIDER and idx >= ACTIVE_BYZANTINE_AT:
            initiated = not initiated

        if initiated:
            with PROVIDER_LOCK:
                PROVIDER_INIT_COUNTS[self.provider_id] += 1
                if domain in PROVIDER_DOMAIN_COUNTS[self.provider_id]:
                    PROVIDER_DOMAIN_COUNTS[self.provider_id][domain] += 1

        enqueue_post(f"http://127.0.0.1:{AUDITOR_PORT}/audit", {
            "provider": self.provider_id,
            "request_repr": rr,
            "initiated": initiated,
            "signature": sign(self.provider_id, rr),
        })

        self.send_response(204); self.end_headers()

def make_provider(pid: str, port: int) -> HTTPServer:
    handler = type(pid, (ProviderHandler,), {"provider_id": pid})
    return HTTPServer(("0.0.0.0", port), handler)

# ============================================================
# Hubs (conveyance only)
# ============================================================

HUB_RELAY_COUNTS = {"HUB_A": 0, "HUB_B": 0}
HUB_LOCK = threading.Lock()

class HubHandler(BaseHTTPRequestHandler):
    hub_id = "HUB_X"
    def log_message(self, *args): return

    def do_POST(self):
        if self.path != "/submit":
            self.send_response(404); self.end_headers(); return

        length = int(self.headers.get("Content-Length", 0))
        if length > MAX_REQUEST_BYTES:
            self.send_response(204); self.end_headers(); return

        try:
            msg = json.loads(self.rfile.read(length))
        except Exception:
            self.send_response(204); self.end_headers(); return

        # Fanout to providers (no semantics)
        for port in PROVIDER_PORTS.values():
            enqueue_post(f"http://127.0.0.1:{port}/ingest", msg)

        # Peer relay count (for “mesh feel”)
        with HUB_LOCK:
            HUB_RELAY_COUNTS[self.hub_id] += len(PROVIDER_PORTS)

        self.send_response(204); self.end_headers()

# ============================================================
# NUVL fronts (neutral): repr + opaque headers -> hub submit
# ============================================================

class NUVLHandler(BaseHTTPRequestHandler):
    hub_port = 0
    def log_message(self, *args): return

    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        rr = sha256_hex(raw)
        ctx = self.headers.get("X-Verification-Context", "")
        domain = self.headers.get("X-Domain", "payments")

        enqueue_post(f"http://127.0.0.1:{self.hub_port}/submit", {
            "request_repr": rr,
            "verification_context": ctx,
            "domain": domain
        })

        self.send_response(204); self.end_headers()

# ============================================================
# Requester with region failover
# ============================================================

def requester_send(port: int, payload: bytes, ctx: str, domain: str) -> None:
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}",
        data=payload,
        headers={
            "Connection": "close",
            "Content-Type": "application/octet-stream",
            "X-Verification-Context": ctx,
            "X-Domain": domain
        },
        method="POST"
    )
    urllib.request.urlopen(req, timeout=2)

def run_benchmark() -> float:
    global CURRENT_REQUEST_INDEX

    start = time.perf_counter()
    for i in range(TOTAL_REQUESTS):
        with CURRENT_LOCK:
            CURRENT_REQUEST_INDEX = i

        region_port = NUVL_A_PORT if i < FAILOVER_AT else NUVL_B_PORT
        ctx = EXPECTED_CONTEXT if random.random() > 0.1 else "SPOOF"
        domain = random.choice(DOMAINS)
        payload = f'{{"i":{i}}}'.encode()

        requester_send(region_port, payload, ctx, domain)

    elapsed = (time.perf_counter() - start) * 1000.0
    time.sleep(1.25)
    return elapsed

# ============================================================
# MAIN
# ============================================================

def start(server: HTTPServer) -> None:
    server.serve_forever()

def pick_byzantine() -> Tuple[str, int]:
    pid = BYZANTINE_PROVIDER.strip()
    if pid not in PROVIDER_PORTS:
        pid = random.choice(list(PROVIDER_PORTS.keys()))

    if BYZANTINE_AT.strip().isdigit():
        at = int(BYZANTINE_AT)
    else:
        lo = max(1, int(TOTAL_REQUESTS * 0.55))
        hi = max(lo + 1, int(TOTAL_REQUESTS * 0.90))
        at = random.randint(lo, hi)

    return pid, at

ACTIVE_BYZANTINE_PROVIDER, ACTIVE_BYZANTINE_AT = ("PROVIDER_C", 0)

def main():
    global ACTIVE_BYZANTINE_PROVIDER, ACTIVE_BYZANTINE_AT

    random.seed(SEED if SEED is not None else time.time_ns())
    start_workers()

    ACTIVE_BYZANTINE_PROVIDER, ACTIVE_BYZANTINE_AT = pick_byzantine()

    # Providers
    for pid, port in PROVIDER_PORTS.items():
        threading.Thread(target=start, args=(make_provider(pid, port),), daemon=True).start()

    # Hubs
    hubA = HTTPServer(("0.0.0.0", HUB_A_PORT), type("HUBA", (HubHandler,), {"hub_id": "HUB_A"}))
    hubB = HTTPServer(("0.0.0.0", HUB_B_PORT), type("HUBB", (HubHandler,), {"hub_id": "HUB_B"}))
    threading.Thread(target=start, args=(hubA,), daemon=True).start()
    threading.Thread(target=start, args=(hubB,), daemon=True).start()

    # NUVLs
    handlerA = type("NUVL_A", (NUVLHandler,), {"hub_port": HUB_A_PORT})
    handlerB = type("NUVL_B", (NUVLHandler,), {"hub_port": HUB_B_PORT})
    threading.Thread(target=start, args=(HTTPServer(("0.0.0.0", NUVL_A_PORT), handlerA),), daemon=True).start()
    threading.Thread(target=start, args=(HTTPServer(("0.0.0.0", NUVL_B_PORT), handlerB),), daemon=True).start()

    # Auditor
    threading.Thread(target=start, args=(HTTPServer(("0.0.0.0", AUDITOR_PORT), AuditorHandler),), daemon=True).start()

    time.sleep(0.9)

    elapsed = run_benchmark()

    print("\n===== MULTI-HUB + MULTI-DOMAIN (FAILOVER + BYZANTINE QUORUM) =====")
    print(f"Total requests: {TOTAL_REQUESTS}")
    print(f"Failover at index: {FAILOVER_AT} (NUVL_A -> NUVL_B)")
    print(f"Byzantine provider: {ACTIVE_BYZANTINE_PROVIDER} (flip at {ACTIVE_BYZANTINE_AT})")
    print(f"Total time: {elapsed:.2f} ms")
    print(f"Avg per request: {elapsed/TOTAL_REQUESTS:.4f} ms\n")

    print("Hub Relay Counts (fanout posts issued):")
    with HUB_LOCK:
        print(f"HUB_A relays: {HUB_RELAY_COUNTS['HUB_A']}")
        print(f"HUB_B relays: {HUB_RELAY_COUNTS['HUB_B']}")

    print("\nProvider Initiations (total):")
    with PROVIDER_LOCK:
        for k, v in PROVIDER_INIT_COUNTS.items():
            print(f"{k}: {v}")

    print("\nProvider Initiations (by domain):")
    with PROVIDER_LOCK:
        for pid in PROVIDER_DOMAIN_COUNTS:
            d = PROVIDER_DOMAIN_COUNTS[pid]
            print(f"{pid}: payments={d['payments']}, identity={d['identity']}, storage={d['storage']}")

    print("\nAuditor Results (non-authoritative aggregation):")
    with AUDIT_LOCK:
        print(f"Quorum successes: {QUORUM_SUCCESS}")
        print(f"Quorum failures: {QUORUM_FAIL}")

        # suspect scoring
        def rate(pid: str) -> float:
            tot = PROVIDER_TOTAL_IN_QUORUM[pid]
            bad = PROVIDER_DISAGREE[pid]
            return (bad / tot) if tot else 0.0

        scored = sorted(PROVIDER_PORTS.keys(), key=lambda p: rate(p), reverse=True)
        top = scored[0]
        print("\nSuspect scoring (provider vote vs quorum outcome):")
        for pid in scored:
            tot = PROVIDER_TOTAL_IN_QUORUM[pid]
            bad = PROVIDER_DISAGREE[pid]
            print(f"{pid}: disagree={bad}/{tot} ({rate(pid)*100:.2f}%)")
        print(f"Most inconsistent provider: {top}")

    print("==================================================================\n")

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
