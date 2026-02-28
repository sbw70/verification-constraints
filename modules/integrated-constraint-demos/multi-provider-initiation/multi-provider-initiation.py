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
import queue
import random
import threading
import time
import urllib.request
from typing import Dict, Any, Optional, Tuple

# -------------------------
# REPLIT-FRIENDLY CONTROLS
# -------------------------
TOTAL_REQUESTS = 750          # change to 100/250/500/750/1000
CONCURRENCY = 24              # requester parallelism (keep modest for Replit)
PROGRESS_EVERY = 100          # progress tick spacing

# Determinism controls
RANDOM_SEED = 1337            # set None for nondeterministic

# Fail/chaos knobs (transport-level; NUVL remains outcome-blind)
P_DROP_FORWARD = 0.02         # NUVL drops forward (provider never sees)
P_DELAY_FORWARD = 0.03        # NUVL delays forward (adds jitter)
DELAY_MS_RANGE = (10, 80)     # only used when delaying

# Byzantine controls (provider-side)
BYZANTINE_PROVIDER_ID = "PROVIDER_B"
BYZANTINE_AT = 400            # after this many provider requests seen, provider starts lying deterministically

# Quorum policy (auditor-side; not NUVL)
QUORUM_K = 2                  # 2-of-3 initiated signals required

# -------------------------
# NETWORK LAYOUT
# -------------------------
HOST = "0.0.0.0"

NUVL_PORT = 8080
AUDITOR_PORT = 7070

PROVIDER_A_PORT = 9090
PROVIDER_B_PORT = 9091
PROVIDER_C_PORT = 9092

NUVL_URL = f"http://127.0.0.1:{NUVL_PORT}/nuvl"
AUDITOR_URL = f"http://127.0.0.1:{AUDITOR_PORT}/outcome"

PROVIDER_URLS = {
    "PROVIDER_A": f"http://127.0.0.1:{PROVIDER_A_PORT}/ingest",
    "PROVIDER_B": f"http://127.0.0.1:{PROVIDER_B_PORT}/ingest",
    "PROVIDER_C": f"http://127.0.0.1:{PROVIDER_C_PORT}/ingest",
}

MAX_REQUEST_BYTES = 1024 * 64  # 64KB

# -------------------------
# SHARED TAGS
# -------------------------
BIND_TAG = "NUVL_BIND_V1"

# Requester context: treated as opaque by NUVL; provider interprets if it wants.
EXPECTED_CONTEXT = "CTX_ALPHA"

# Domains (simulates heterogeneous provider policy tables)
DOMAINS = ["payments", "identity", "storage", "compute"]

# ============================================================
# NUVL CORE (APACHE-2.0)
# ============================================================

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def nuvl_bind(request_repr_hex: str, verification_context: str) -> str:
    msg = (BIND_TAG + "|" + request_repr_hex + "|" + verification_context).encode("utf-8")
    return hashlib.sha256(msg).hexdigest()

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

# ---- bounded forwarder pool (prevents "thread per request" meltdown) ----
_FORWARD_Q: "queue.Queue[Tuple[str, bytes]]" = queue.Queue(maxsize=10_000)
_FORWARD_STOP = object()

def _forward_worker():
    while True:
        item = _FORWARD_Q.get()
        if item is _FORWARD_STOP:
            _FORWARD_Q.task_done()
            return
        url, raw = item
        try:
            req = urllib.request.Request(
                url,
                data=raw,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=2):
                pass
        except Exception:
            pass
        finally:
            _FORWARD_Q.task_done()

def start_forward_pool(workers: int = 12):
    for _ in range(workers):
        t = threading.Thread(target=_forward_worker, daemon=True)
        t.start()

def forward_json_best_effort(url: str, payload: Dict[str, Any]) -> None:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    try:
        _FORWARD_Q.put_nowait((url, raw))
    except queue.Full:
        # Fail-closed at transport: drop forward.
        return

class NUVLHandler(BaseHTTPRequestHandler):
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

        # NUVL only forms representations + binding (mechanical)
        request_repr = sha256_hex(request_bytes)
        binding = nuvl_bind(request_repr, verification_context)

        # Correlation is for tracking/relay only (not execution state).
        corr_seed = (request_repr + "|" + domain + "|" + str(time.time_ns())).encode("utf-8")
        correlation_id = "CORR_" + sha256_hex(corr_seed)[:20]

        # Chaos: NUVL may drop or delay forwards (still constant 204 to requester)
        r = random.random()
        if r < P_DROP_FORWARD:
            # drop (providers never see anything)
            self.send_response(204)
            self.end_headers()
            return
        if r < P_DROP_FORWARD + P_DELAY_FORWARD:
            lo, hi = DELAY_MS_RANGE
            time.sleep(random.randint(lo, hi) / 1000.0)

        artifact = {
            "correlation_id": correlation_id,
            "request_repr": request_repr,
            "verification_context": verification_context,
            "binding": binding,
            "domain": domain,
            # provider should POST outcomes to auditor, not to NUVL
            "return_outcome_url": AUDITOR_URL,
        }

        # fan-out to providers (NUVL does not interpret outcomes)
        for pid, url in PROVIDER_URLS.items():
            forward = dict(artifact)
            forward["provider_id"] = pid
            forward_json_best_effort(url, forward)

        # constant response; no outcome semantics
        self.send_response(204)
        self.end_headers()

def start_nuvl():
    srv = ThreadingHTTPServer((HOST, NUVL_PORT), NUVLHandler)
    srv.serve_forever()

# ============================================================
# PROPRIETARY EXTENSION: Provider AI + Domain Threshold Tables
# ============================================================

# Provider-only secrets (intermediary/NUVL never sees these)
PROVIDER_BOUNDARY_KEY = b"PROVIDER_ONLY_BOUNDARY_KEY_CHANGE_ME"
PROVIDER_MODEL_SEED = b"PROVIDER_ONLY_MODEL_SEED_CHANGE_ME"

# Provider-controlled threshold table (domain-specific)
# (tune these to change acceptance rates per domain)
DOMAIN_THRESHOLDS = {
    "payments": 0.62,
    "identity": 0.70,
    "storage":  0.55,
    "compute":  0.50,
}

def provider_expected_binding(request_repr_hex: str, verification_context: str) -> str:
    msg = (BIND_TAG + "|" + request_repr_hex + "|" + verification_context).encode("utf-8")
    return hashlib.sha256(msg).hexdigest()

def provider_ai_score(request_repr_hex: str, verification_context: str, domain: str) -> float:
    """
    Provider-controlled adaptive decision (demo stand-in for inference).
    Output in [0,1]. NUVL cannot compute or validate this.
    """
    material = (request_repr_hex + "|" + verification_context + "|" + domain).encode("utf-8")
    digest = hmac.new(PROVIDER_MODEL_SEED, material, hashlib.sha256).digest()
    n = int.from_bytes(digest[:8], "big")
    score = (n % 10_000_000) / 10_000_000.0
    # Provider can shape by context (demo)
    if verification_context == EXPECTED_CONTEXT:
        score = min(1.0, score + 0.18)
    return score

def provider_boundary_sig(provider_id: str, correlation_id: str, request_repr_hex: str, stage: str) -> str:
    payload = f"{provider_id}|{stage}|{correlation_id}|{request_repr_hex}|{time.time_ns()}".encode("utf-8")
    return hmac.new(PROVIDER_BOUNDARY_KEY, payload, hashlib.sha256).hexdigest()

# provider local counters (for deterministic byzantine switch)
_PROVIDER_SEEN_LOCK = threading.Lock()
_PROVIDER_SEEN: Dict[str, int] = {"PROVIDER_A": 0, "PROVIDER_B": 0, "PROVIDER_C": 0}

def provider_seen_inc(pid: str) -> int:
    with _PROVIDER_SEEN_LOCK:
        _PROVIDER_SEEN[pid] = _PROVIDER_SEEN.get(pid, 0) + 1
        return _PROVIDER_SEEN[pid]

class ProviderHandler(BaseHTTPRequestHandler):
    provider_id = "PROVIDER_X"

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

        pid = self.provider_id
        seen_n = provider_seen_inc(pid)

        correlation_id = msg.get("correlation_id", "")
        request_repr = msg.get("request_repr", "")
        verification_context = msg.get("verification_context", "")
        binding = msg.get("binding", "")
        domain = msg.get("domain", "") or "unknown"
        return_outcome_url = msg.get("return_outcome_url", "")

        # integrity constraint: verify intermediary binding (mechanical)
        expected_binding = provider_expected_binding(request_repr, verification_context)
        binding_ok = hmac.compare_digest(binding, expected_binding)

        # provider-only AI decision
        score = provider_ai_score(request_repr, verification_context, domain)
        threshold = DOMAIN_THRESHOLDS.get(domain, 0.75)

        initiated = bool(binding_ok and score >= threshold)

        # deterministic byzantine: one provider flips the initiated bit after BYZANTINE_AT
        byzantine_active = (pid == BYZANTINE_PROVIDER_ID and seen_n >= BYZANTINE_AT)
        if byzantine_active:
            # deterministic lie: invert (but keep signature structure consistent)
            initiated = not initiated

        # provider boundary signals (signed under provider authority)
        boundary = None
        if initiated:
            boundary = {
                "start": provider_boundary_sig(pid, correlation_id, request_repr, "START"),
                "complete": provider_boundary_sig(pid, correlation_id, request_repr, "COMPLETE"),
            }

        outcome = {
            "provider_id": pid,
            "correlation_id": correlation_id,
            "domain": domain,
            "provider_initiated": initiated,
            "byzantine_active": byzantine_active,
            "boundary": boundary,
        }

        # provider reports outcomes to auditor; NUVL remains outcome-blind
        if isinstance(return_outcome_url, str) and return_outcome_url.startswith("http"):
            forward_json_best_effort(return_outcome_url, outcome)

        self.send_response(204)
        self.end_headers()

def make_provider_server(provider_id: str, port: int) -> ThreadingHTTPServer:
    handler_cls = type(f"{provider_id}Handler", (ProviderHandler,), {"provider_id": provider_id})
    return ThreadingHTTPServer((HOST, port), handler_cls)

# ============================================================
# PROPRIETARY EXTENSION: Quorum Auditor (2-of-3)
# ============================================================

_AUD_LOCK = threading.Lock()
# corr -> provider_id -> initiated
_AUD: Dict[str, Dict[str, bool]] = {}
# corr -> domain
_AUD_DOMAIN: Dict[str, str] = {}

# stats
_AUD_QUORUM_OK = 0
_AUD_QUORUM_FAIL = 0
_AUD_BY_DOMAIN: Dict[str, Dict[str, int]] = {d: {"ok": 0, "fail": 0} for d in DOMAINS}

class AuditorHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def do_POST(self):
        if self.path != "/outcome":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length > 0 else b""
        if not body:
            self.send_response(204)
            self.end_headers()
            return

        try:
            msg = json.loads(body.decode("utf-8"))
        except Exception:
            self.send_response(204)
            self.end_headers()
            return

        corr = msg.get("correlation_id", "")
        pid = msg.get("provider_id", "")
        domain = msg.get("domain", "") or "unknown"
        initiated = bool(msg.get("provider_initiated", False))

        if not isinstance(corr, str) or not corr.startswith("CORR_"):
            self.send_response(204)
            self.end_headers()
            return
        if not isinstance(pid, str) or not pid.startswith("PROVIDER_"):
            self.send_response(204)
            self.end_headers()
            return

        with _AUD_LOCK:
            _AUD_DOMAIN[corr] = domain
            prov_map = _AUD.setdefault(corr, {})
            # de-dupe provider outcome
            if pid in prov_map:
                self.send_response(204)
                self.end_headers()
                return
            prov_map[pid] = initiated

            # if we have all 3 providers, evaluate quorum immediately
            if len(prov_map) == 3:
                trues = sum(1 for v in prov_map.values() if v)
                ok = (trues >= QUORUM_K)
                global _AUD_QUORUM_OK, _AUD_QUORUM_FAIL
                if ok:
                    _AUD_QUORUM_OK += 1
                    if domain in _AUD_BY_DOMAIN:
                        _AUD_BY_DOMAIN[domain]["ok"] += 1
                else:
                    _AUD_QUORUM_FAIL += 1
                    if domain in _AUD_BY_DOMAIN:
                        _AUD_BY_DOMAIN[domain]["fail"] += 1
                # free memory
                _AUD.pop(corr, None)
                _AUD_DOMAIN.pop(corr, None)

        self.send_response(204)
        self.end_headers()

def start_auditor():
    srv = ThreadingHTTPServer((HOST, AUDITOR_PORT), AuditorHandler)
    srv.serve_forever()

# ============================================================
# REQUESTER (STRESS DRIVER)
# ============================================================

_REQ_OK = 0
_REQ_ERR = 0
_REQ_LOCK = threading.Lock()

def requester_send_one(payload: bytes, ctx: str, domain: str) -> None:
    global _REQ_OK, _REQ_ERR
    req = urllib.request.Request(
        NUVL_URL,
        data=payload,
        headers={
            "Content-Type": "application/octet-stream",
            "X-Verification-Context": ctx,
            "X-Domain": domain,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=2) as resp:
            _ = resp.status
        with _REQ_LOCK:
            _REQ_OK += 1
    except Exception:
        with _REQ_LOCK:
            _REQ_ERR += 1

def run_benchmark():
    payload = b'{"op":"transfer","amount":100,"to":"acct_123"}'

    # contexts: mostly expected, some spoofed (provider will reject)
    contexts = [EXPECTED_CONTEXT, EXPECTED_CONTEXT, EXPECTED_CONTEXT, "CTX_SPOOFED", "", "CTX_BETA"]

    start = time.perf_counter()

    # concurrency via worker threads pulling from a queue
    q: "queue.Queue[int]" = queue.Queue()
    for i in range(TOTAL_REQUESTS):
        q.put(i)

    def worker():
        while True:
            try:
                i = q.get_nowait()
            except queue.Empty:
                return
            domain = random.choice(DOMAINS)
            ctx = random.choice(contexts)
            requester_send_one(payload, ctx, domain)
            if (i + 1) % PROGRESS_EVERY == 0:
                print(f"Requester progress: {i+1}/{TOTAL_REQUESTS}")
            q.task_done()

    threads = []
    for _ in range(CONCURRENCY):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    end = time.perf_counter()

    # allow in-flight forwards/outcomes to land
    time.sleep(0.6)

    total_ms = (end - start) * 1000.0
    avg_ms = total_ms / float(TOTAL_REQUESTS) if TOTAL_REQUESTS else 0.0

    with _REQ_LOCK:
        ok = _REQ_OK
        err = _REQ_ERR

    with _AUD_LOCK:
        q_ok = _AUD_QUORUM_OK
        q_fail = _AUD_QUORUM_FAIL
        by_domain = {k: dict(v) for k, v in _AUD_BY_DOMAIN.items()}

    print("")
    print("===== MULTI-PROVIDER STRESS (NUVL + Provider-AI + Quorum) =====")
    print(f"Total requests:        {TOTAL_REQUESTS}")
    print(f"HTTP ok:               {ok}, errors: {err}")
    print(f"Total time:            {total_ms:.2f} ms")
    print(f"Avg per request:       {avg_ms:.4f} ms")
    print(f"Byzantine at:          {BYZANTINE_AT} ({BYZANTINE_PROVIDER_ID} flips initiated)")
    print(f"Quorum policy:         {QUORUM_K}-of-3 on initiated signals")
    print("")
    print("Auditor results:")
    print(f"  Quorum successes:    {q_ok}")
    print(f"  Quorum failures:     {q_fail}")
    print("")
    print("By domain:")
    for d in DOMAINS:
        s = by_domain.get(d, {"ok": 0, "fail": 0})
        print(f"  {d:>9}: success={s['ok']:<4} fail={s['fail']:<4}")
    print("===============================================================")

def main():
    if RANDOM_SEED is None:
        random.seed()
    else:
        random.seed(RANDOM_SEED)

    # start bounded forward pool first (shared by NUVL/Providers/Auditor)
    start_forward_pool(workers=12)

    # start services
    threading.Thread(target=start_auditor, daemon=True).start()

    provider_a = make_provider_server("PROVIDER_A", PROVIDER_A_PORT)
    provider_b = make_provider_server("PROVIDER_B", PROVIDER_B_PORT)
    provider_c = make_provider_server("PROVIDER_C", PROVIDER_C_PORT)

    threading.Thread(target=provider_a.serve_forever, daemon=True).start()
    threading.Thread(target=provider_b.serve_forever, daemon=True).start()
    threading.Thread(target=provider_c.serve_forever, daemon=True).start()

    threading.Thread(target=start_nuvl, daemon=True).start()

    time.sleep(0.7)

    size_bytes = os.path.getsize(__file__)
    print(f"Reference size: {size_bytes} bytes ({size_bytes/1024:.1f} KiB)")
    print("")

    run_benchmark()

    # keep alive
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
