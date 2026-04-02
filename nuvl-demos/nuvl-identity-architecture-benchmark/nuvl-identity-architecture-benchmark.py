#!/usr/bin/env python3
# Copyright 2026 Seth Brian Wells
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Identity Architecture Benchmark

Compares two request-path architectures under identical sustained load:

  Identity-first (traditional):
    client → IAM gateway
               ↓ token parse (base64 decode + JSON parse)
               ↓ HMAC signature verify
               ↓ policy lookup
               ↓ optional auth-server jitter
               ↓ synchronous provider forward (blocks until response)
             provider (on critical path)

  Identity-second (NUVL):
    client → NUVL layer
               ↓ SHA-256 request representation
               ↓ deterministic binding computation
               ↓ async artifact forward (off critical path)
             immediate HTTP 204 return
             provider (async, off critical path)

Metrics reported per architecture:
  - p50 / p95 / p99 / average / min / max latency (ms)
  - Throughput (req/sec), total wall time
  - Voluntary and involuntary context switch deltas

All four servers (IF gateway, IF provider, IS NUVL, IS provider) run
in-process as daemon threads. Load is generated with a fixed thread pool.
"""

import base64
import hashlib
import hmac as _hmac_mod
import json
import math
import os
import random
import resource
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

# -------------------------
# Benchmark parameters
# -------------------------
TOTAL_REQUESTS = 10_000
CONCURRENCY = 20

# Set to an int for repeatable runs, None for non-deterministic.
RANDOM_SEED = None

# Simulated auth-server jitter (models occasional slow OAuth/IAM backend).
# This is the primary driver of p99 inflation in identity-first stacks.
IAM_JITTER_P = 0.02       # 2 % of requests hit a slow auth path
IAM_JITTER_MS = 6.0       # +6 ms added when jitter fires

# -------------------------
# Ports
# -------------------------
IF_GATEWAY_PORT = 8181     # Identity-first: IAM gateway
IF_PROVIDER_PORT = 9191    # Identity-first: provider ingest

IS_NUVL_PORT = 8282        # Identity-second: NUVL layer
IS_PROVIDER_PORT = 9292    # Identity-second: provider ingest

# -------------------------
# Shared constants
# -------------------------
EXPECTED_CONTEXT = "CTX_ALPHA"
PROVIDER_HMAC_KEY = b"PROVIDER_ONLY_KEY_CHANGE_ME"
BIND_TAG = "NUVL_BIND_V1"
MAX_REQUEST_BYTES = 1024 * 64  # 64 KB

# Identity-first: IAM token signing key (held by gateway, not provider).
IAM_TOKEN_KEY = b"IAM_SIGNING_KEY_DEMO"
IAM_POLICY_TABLE = {
    "user_alice": ["transfer", "read"],
    "user_bob": ["read"],
}


# -------------------------
# Pre-built demo token
# -------------------------
def _make_demo_token(subject: str) -> str:
    payload = json.dumps({"sub": subject, "op": "transfer"}).encode("utf-8")
    b64 = base64.b64encode(payload).decode("ascii")
    sig = _hmac_mod.new(IAM_TOKEN_KEY, payload, hashlib.sha256).hexdigest()
    return b64 + "." + sig


DEMO_TOKEN = _make_demo_token("user_alice")

# -------------------------
# Utility
# -------------------------

def _percentile(sorted_data: list, p: float) -> float:
    if not sorted_data:
        return 0.0
    k = (len(sorted_data) - 1) * p / 100.0
    lo = int(math.floor(k))
    hi = int(math.ceil(k))
    if lo == hi:
        return sorted_data[lo]
    return sorted_data[lo] + (sorted_data[hi] - sorted_data[lo]) * (k - lo)


def _current_rss_kb() -> int:
    """Current RSS in KB. Reads /proc/self/status on Linux for accuracy."""
    try:
        with open("/proc/self/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])
    except Exception:
        pass
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def _csw() -> tuple:
    """Return (voluntary_csw, involuntary_csw) for current process."""
    u = resource.getrusage(resource.RUSAGE_SELF)
    return u.ru_nvcsw, u.ru_nivcsw


# ============================================================
# Identity-first: IAM Gateway + Provider
# ============================================================

_IF_LOCK = threading.Lock()
_IF_PROVIDER_TOTAL = 0


class _IFProviderHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def do_POST(self):
        global _IF_PROVIDER_TOTAL
        if self.path != "/ingest":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length > 0:
            self.rfile.read(length)
        with _IF_LOCK:
            _IF_PROVIDER_TOTAL += 1
        self.send_response(204)
        self.end_headers()


def _start_if_provider():
    HTTPServer(("0.0.0.0", IF_PROVIDER_PORT), _IFProviderHandler).serve_forever()


class _IFGatewayHandler(BaseHTTPRequestHandler):
    """
    Identity-first IAM gateway.

    All of the following steps are synchronous on the critical request path:
      1. Base64-decode and JSON-parse the Bearer token.
      2. HMAC-verify the token signature against the IAM signing key.
      3. Look up the subject's permitted operations in the policy table.
      4. Optionally inject latency (models a slow auth-server backend).
      5. Synchronously POST to the provider and wait for the response.
         The client is blocked until step 5 completes.
    """

    def log_message(self, fmt, *args):
        return

    def do_POST(self):
        if self.path != "/auth":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_REQUEST_BYTES:
            self.send_response(413)
            self.end_headers()
            return

        request_bytes = self.rfile.read(length) if length > 0 else b""

        # Step 1: Parse token — base64 decode + JSON parse (object allocation).
        auth_header = self.headers.get("Authorization", "")
        token = auth_header[len("Bearer "):].strip() if auth_header.startswith("Bearer ") else ""
        authorized = False
        try:
            parts = token.split(".", 1)
            if len(parts) == 2:
                b64_payload, received_sig = parts
                payload_bytes = base64.b64decode(b64_payload)
                payload_obj = json.loads(payload_bytes.decode("utf-8"))
                subject = payload_obj.get("sub", "")
                operation = payload_obj.get("op", "")

                # Step 2: HMAC verify.
                expected_sig = _hmac_mod.new(
                    IAM_TOKEN_KEY, payload_bytes, hashlib.sha256
                ).hexdigest()
                if _hmac_mod.compare_digest(received_sig, expected_sig):
                    # Step 3: Policy lookup.
                    if operation in IAM_POLICY_TABLE.get(subject, []):
                        authorized = True
        except Exception:
            pass

        if not authorized:
            self.send_response(403)
            self.end_headers()
            return

        # Step 4: Optional auth-server jitter.
        if random.random() < IAM_JITTER_P:
            time.sleep(IAM_JITTER_MS / 1000.0)

        # Step 5: Synchronous provider forward (blocks until provider responds).
        req_repr = hashlib.sha256(request_bytes).hexdigest()
        fwd_body = json.dumps(
            {"request_repr": req_repr, "context": EXPECTED_CONTEXT},
            separators=(",", ":"),
        ).encode("utf-8")
        fwd_req = urllib.request.Request(
            f"http://127.0.0.1:{IF_PROVIDER_PORT}/ingest",
            data=fwd_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(fwd_req, timeout=3):
                pass
        except Exception:
            self.send_response(502)
            self.end_headers()
            return

        self.send_response(204)
        self.end_headers()


def _start_if_gateway():
    HTTPServer(("0.0.0.0", IF_GATEWAY_PORT), _IFGatewayHandler).serve_forever()


# ============================================================
# Identity-second (NUVL): NUVL layer + Provider
# ============================================================

_IS_LOCK = threading.Lock()
_IS_PROVIDER_TOTAL = 0


class _ISProviderHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def do_POST(self):
        global _IS_PROVIDER_TOTAL
        if self.path != "/ingest":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length > 0:
            self.rfile.read(length)
        with _IS_LOCK:
            _IS_PROVIDER_TOTAL += 1
        self.send_response(204)
        self.end_headers()


def _start_is_provider():
    HTTPServer(("0.0.0.0", IS_PROVIDER_PORT), _ISProviderHandler).serve_forever()


def _nuvl_bind(request_repr_hex: str, verification_context: str) -> str:
    msg = (BIND_TAG + "|" + request_repr_hex + "|" + verification_context).encode("utf-8")
    return hashlib.sha256(msg).hexdigest()


def _forward_artifact_async(artifact: dict) -> None:
    def _send():
        try:
            data = json.dumps(artifact, separators=(",", ":")).encode("utf-8")
            req = urllib.request.Request(
                f"http://127.0.0.1:{IS_PROVIDER_PORT}/ingest",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=2):
                pass
        except Exception:
            return

    threading.Thread(target=_send, daemon=True).start()


class _ISNUVLHandler(BaseHTTPRequestHandler):
    """
    Identity-second NUVL layer.

    All critical-path operations are local and non-blocking:
      1. SHA-256 request representation (single hash, no I/O).
      2. Deterministic binding computation (second SHA-256).
      3. Artifact forward dispatched to a background daemon thread.
      4. HTTP 204 returned immediately — provider runs off the critical path.

    NUVL holds no signing material, evaluates no policy, and cannot relay
    provider authorization decisions. It is structurally incapable of
    acquiring execution authority.
    """

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

        # Step 1 + 2: Local hash + bind — no blocking I/O.
        request_repr = hashlib.sha256(request_bytes).hexdigest()
        binding = _nuvl_bind(request_repr, verification_context)

        # Step 3: Async forward — provider evaluation is off the critical path.
        _forward_artifact_async(
            {
                "request_repr": request_repr,
                "verification_context": verification_context,
                "binding": binding,
            }
        )

        # Step 4: Return immediately.
        self.send_response(204)
        self.end_headers()


def _start_is_nuvl():
    HTTPServer(("0.0.0.0", IS_NUVL_PORT), _ISNUVLHandler).serve_forever()


# ============================================================
# Load generation
# ============================================================

def _run_benchmark(n: int, concurrency: int, url: str, headers: dict, payload: bytes) -> list:
    """
    Send n POST requests to url using a fixed pool of concurrency threads.
    Returns a list of per-request latency samples in milliseconds.
    """
    samples = [0.0] * n
    lock = threading.Lock()
    counter = [0]

    def worker():
        while True:
            with lock:
                i = counter[0]
                if i >= n:
                    return
                counter[0] += 1
            t0 = time.perf_counter()
            req = urllib.request.Request(
                url,
                data=payload,
                headers=headers,
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=5):
                    pass
            except Exception:
                pass
            samples[i] = (time.perf_counter() - t0) * 1000.0

    threads = [threading.Thread(target=worker) for _ in range(concurrency)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return samples


# ============================================================
# Reporting
# ============================================================

def _stats(samples: list) -> dict:
    s = sorted(samples)
    n = len(s)
    avg = sum(s) / n if n else 0.0
    return {
        "p50": _percentile(s, 50),
        "p95": _percentile(s, 95),
        "p99": _percentile(s, 99),
        "avg": avg,
        "min": s[0] if s else 0.0,
        "max": s[-1] if s else 0.0,
    }


def _delta_pct(baseline: float, candidate: float) -> str:
    if baseline == 0:
        return "N/A"
    return f"{((candidate - baseline) / baseline * 100):+.1f}%"


def _print_results(
    if_stats: dict, if_elapsed: float, if_csw: tuple,
    is_stats: dict, is_elapsed: float, is_csw: tuple,
) -> None:
    if_tput = TOTAL_REQUESTS / if_elapsed if if_elapsed > 0 else 0.0
    is_tput = TOTAL_REQUESTS / is_elapsed if is_elapsed > 0 else 0.0

    W = 66
    print()
    print("=" * W)
    print("IDENTITY ARCHITECTURE BENCHMARK — RESULTS")
    print("=" * W)
    print(f"{'Metric':<30} {'Identity-first':>16} {'Identity-second':>16}")
    print("-" * W)

    rows = [
        ("p50 latency (ms)",          f"{if_stats['p50']:.3f}",    f"{is_stats['p50']:.3f}"),
        ("p95 latency (ms)",          f"{if_stats['p95']:.3f}",    f"{is_stats['p95']:.3f}"),
        ("p99 latency (ms)",          f"{if_stats['p99']:.3f}",    f"{is_stats['p99']:.3f}"),
        ("avg latency (ms)",          f"{if_stats['avg']:.3f}",    f"{is_stats['avg']:.3f}"),
        ("min latency (ms)",          f"{if_stats['min']:.3f}",    f"{is_stats['min']:.3f}"),
        ("max latency (ms)",          f"{if_stats['max']:.3f}",    f"{is_stats['max']:.3f}"),
        ("throughput (req/sec)",      f"{if_tput:.0f}",            f"{is_tput:.0f}"),
        ("total wall time (s)",       f"{if_elapsed:.3f}",         f"{is_elapsed:.3f}"),
        ("vol. context switches",     str(if_csw[0]),              str(is_csw[0])),
        ("invol. context switches",   str(if_csw[1]),              str(is_csw[1])),
    ]
    for label, v_if, v_is in rows:
        print(f"  {label:<28} {v_if:>16} {v_is:>16}")

    print("-" * W)
    print("  Deltas (identity-second vs identity-first baseline):")
    print(f"  {'p50 delta':<28} {'baseline':>16} {_delta_pct(if_stats['p50'], is_stats['p50']):>16}")
    print(f"  {'p95 delta':<28} {'baseline':>16} {_delta_pct(if_stats['p95'], is_stats['p95']):>16}")
    print(f"  {'p99 delta':<28} {'baseline':>16} {_delta_pct(if_stats['p99'], is_stats['p99']):>16}")
    print(f"  {'throughput delta':<28} {'baseline':>16} {_delta_pct(if_tput, is_tput):>16}")
    print("=" * W)
    print()
    print("  Configuration:")
    print(f"    Requests per architecture : {TOTAL_REQUESTS}")
    print(f"    Concurrent workers        : {CONCURRENCY}")
    print(f"    IAM jitter probability    : {IAM_JITTER_P:.0%}")
    print(f"    IAM jitter magnitude      : {IAM_JITTER_MS:.1f} ms")
    print()
    print("  Identity-first critical path per request:")
    print("    base64 decode → JSON parse → HMAC verify → policy lookup")
    print("    → [optional auth jitter] → synchronous provider round-trip")
    print()
    print("  Identity-second critical path per request:")
    print("    SHA-256 repr → binding compute → async forward dispatch")
    print("    → immediate HTTP 204 return (provider off critical path)")
    print()
    print(f"  Provider artifacts received — identity-first  : {_IF_PROVIDER_TOTAL}")
    print(f"  Provider artifacts received — identity-second : {_IS_PROVIDER_TOTAL}")
    print()


# ============================================================
# Main
# ============================================================

def main():
    if RANDOM_SEED is None:
        random.seed()
    else:
        random.seed(RANDOM_SEED)

    size_bytes = os.path.getsize(__file__)
    print(f"Reference size: {size_bytes} bytes ({size_bytes / 1024:.1f} KiB)")
    print()

    for fn in (_start_if_provider, _start_if_gateway, _start_is_provider, _start_is_nuvl):
        threading.Thread(target=fn, daemon=True).start()
    time.sleep(0.8)

    print(
        f"Servers ready. Running {TOTAL_REQUESTS:,} requests × 2 architectures "
        f"({CONCURRENCY} concurrent workers each)."
    )
    print()

    payload = b'{"op":"transfer","amount":100,"to":"acct_123"}'

    # ---- Identity-first ----
    print("[1/2] Running identity-first benchmark ...")
    csw0 = _csw()
    t0 = time.perf_counter()
    if_samples = _run_benchmark(
        TOTAL_REQUESTS,
        CONCURRENCY,
        url=f"http://127.0.0.1:{IF_GATEWAY_PORT}/auth",
        headers={
            "Content-Type": "application/octet-stream",
            "Authorization": f"Bearer {DEMO_TOKEN}",
        },
        payload=payload,
    )
    if_elapsed = time.perf_counter() - t0
    csw1 = _csw()
    if_csw = (csw1[0] - csw0[0], csw1[1] - csw0[1])
    print(f"      Done. Wall time: {if_elapsed:.3f} s")

    # Let async background threads settle before the next run.
    time.sleep(0.5)

    # ---- Identity-second (NUVL) ----
    print("[2/2] Running identity-second (NUVL) benchmark ...")
    csw2 = _csw()
    t1 = time.perf_counter()
    is_samples = _run_benchmark(
        TOTAL_REQUESTS,
        CONCURRENCY,
        url=f"http://127.0.0.1:{IS_NUVL_PORT}/nuvl",
        headers={
            "Content-Type": "application/octet-stream",
            "X-Verification-Context": EXPECTED_CONTEXT,
        },
        payload=payload,
    )
    is_elapsed = time.perf_counter() - t1
    csw3 = _csw()
    is_csw = (csw3[0] - csw2[0], csw3[1] - csw2[1])
    print(f"      Done. Wall time: {is_elapsed:.3f} s")

    # Allow any in-flight async forwards to complete before reporting.
    time.sleep(0.4)

    if_stats = _stats(if_samples)
    is_stats = _stats(is_samples)
    _print_results(if_stats, if_elapsed, if_csw, is_stats, is_elapsed, is_csw)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
