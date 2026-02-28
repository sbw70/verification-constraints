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

from http.server import BaseHTTPRequestHandler, HTTPServer
import hashlib
import hmac
import json
import os
import random
import threading
import time
import urllib.request

# -------------------------
# Network
# -------------------------
PROVIDER_HOST = "0.0.0.0"
PROVIDER_PORT = 9090

NUVL_HOST = "0.0.0.0"
NUVL_PORT = 8080

PROVIDER_INGEST_URL = f"http://127.0.0.1:{PROVIDER_PORT}/ingest"

# Provider-expected context value (neutral naming).
EXPECTED_CONTEXT = "CTX_ALPHA"

# Provider-only secret. NUVL has no access to this.
PROVIDER_HMAC_KEY = b"PROVIDER_ONLY_KEY_CHANGE_ME"

BIND_TAG = "NUVL_BIND_V1"
MAX_REQUEST_BYTES = 1024 * 64  # 64KB

# -------------------------
# Benchmark controls
# -------------------------
TOTAL_REQUESTS = 10000

# Mix of behaviors (must sum to 1.0)
P_GOOD = 0.85
P_BINDING_FAIL = 0.10
P_MALFORMED_JSON = 0.03
P_DROP_FORWARD = 0.02

# Set to an int for repeatable runs (e.g., 1234). Set to None for true randomness.
RANDOM_SEED = None

# Print frequency for requester-side progress (0 disables)
REQUESTER_PROGRESS_EVERY = 1000

# Provider prints only summary (never per-request)
PROVIDER_PRINT_PER_REQUEST = False


def provider_expected_binding(request_repr_hex: str, verification_context: str) -> str:
    msg = (BIND_TAG + "|" + request_repr_hex + "|" + verification_context).encode("utf-8")
    return hashlib.sha256(msg).hexdigest()


def provider_boundary_signature(request_repr_hex: str, verification_context: str, binding: str) -> str:
    msg = (request_repr_hex + "|" + verification_context + "|" + binding).encode("utf-8")
    return hmac.new(PROVIDER_HMAC_KEY, msg, hashlib.sha256).hexdigest()


# -------------------------
# Provider-side counters (provider-controlled; NUVL remains outcome-blind)
# -------------------------
_PROVIDER_LOCK = threading.Lock()
_PROVIDER_TOTAL_SEEN = 0
_PROVIDER_INITIATED = 0
_PROVIDER_PARSE_FAIL = 0
_PROVIDER_BINDING_FAIL = 0
_PROVIDER_OTHER_FAIL = 0
_PROVIDER_FIRST_SEEN_TS = None
_PROVIDER_LAST_SEEN_TS = None


def provider_record_seen(outcome: str) -> None:
    global _PROVIDER_TOTAL_SEEN, _PROVIDER_INITIATED, _PROVIDER_PARSE_FAIL, _PROVIDER_BINDING_FAIL, _PROVIDER_OTHER_FAIL
    global _PROVIDER_FIRST_SEEN_TS, _PROVIDER_LAST_SEEN_TS

    now = time.perf_counter()
    with _PROVIDER_LOCK:
        _PROVIDER_TOTAL_SEEN += 1
        if _PROVIDER_FIRST_SEEN_TS is None:
            _PROVIDER_FIRST_SEEN_TS = now
        _PROVIDER_LAST_SEEN_TS = now

        if outcome == "INITIATED":
            _PROVIDER_INITIATED += 1
        elif outcome == "PARSE_FAIL":
            _PROVIDER_PARSE_FAIL += 1
        elif outcome == "BINDING_FAIL":
            _PROVIDER_BINDING_FAIL += 1
        else:
            _PROVIDER_OTHER_FAIL += 1


def provider_summary() -> str:
    with _PROVIDER_LOCK:
        total = _PROVIDER_TOTAL_SEEN
        initiated = _PROVIDER_INITIATED
        parse_fail = _PROVIDER_PARSE_FAIL
        binding_fail = _PROVIDER_BINDING_FAIL
        other_fail = _PROVIDER_OTHER_FAIL
        t0 = _PROVIDER_FIRST_SEEN_TS
        t1 = _PROVIDER_LAST_SEEN_TS

    window_ms = 0.0 if (t0 is None or t1 is None) else (t1 - t0) * 1000.0
    avg_ms_valid = (window_ms / initiated) if initiated > 0 else 0.0

    lines = []
    lines.append("")
    lines.append("=" * 58)
    lines.append("PROVIDER SUMMARY (provider boundary observability)")
    lines.append("=" * 58)
    lines.append(f"Total artifacts received:        {total}")
    lines.append(f"Valid initiations:               {initiated}")
    lines.append(f"Rejected (binding mismatch):     {binding_fail}")
    lines.append(f"Rejected (malformed JSON):       {parse_fail}")
    lines.append(f"Rejected (other):                {other_fail}")
    lines.append(f"Provider timing window:          {window_ms:.2f} ms")
    lines.append(f"Avg per VALID initiation:        {avg_ms_valid:.4f} ms")
    lines.append("=" * 58)
    return "\n".join(lines)


class ProviderHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def do_POST(self):
        if self.path != "/ingest":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length > 0 else b""

        try:
            artifact = json.loads(body.decode("utf-8"))
        except Exception:
            provider_record_seen("PARSE_FAIL")
            if PROVIDER_PRINT_PER_REQUEST:
                print("PROVIDER: NOT INITIATED (parse fail)")
            self.send_response(204)
            self.end_headers()
            return

        request_repr = artifact.get("request_repr", "")
        verification_context = artifact.get("verification_context", "")
        binding = artifact.get("binding", "")

        initiated = False
        if verification_context == EXPECTED_CONTEXT:
            expected = provider_expected_binding(request_repr, verification_context)
            if hmac.compare_digest(binding, expected):
                initiated = True

        # Provider-only boundary signature computed inside provider boundary.
        _ = provider_boundary_signature(request_repr, verification_context, binding)

        if initiated:
            provider_record_seen("INITIATED")
            if PROVIDER_PRINT_PER_REQUEST:
                print("PROVIDER: INITIATED")
        else:
            provider_record_seen("BINDING_FAIL")
            if PROVIDER_PRINT_PER_REQUEST:
                print("PROVIDER: NOT INITIATED")

        self.send_response(204)
        self.end_headers()


def start_provider():
    HTTPServer((PROVIDER_HOST, PROVIDER_PORT), ProviderHandler).serve_forever()


def nuvl_bind(request_repr_hex: str, verification_context: str) -> str:
    msg = (BIND_TAG + "|" + request_repr_hex + "|" + verification_context).encode("utf-8")
    return hashlib.sha256(msg).hexdigest()


def forward_bytes_async(raw: bytes) -> None:
    def _send():
        try:
            req = urllib.request.Request(
                PROVIDER_INGEST_URL,
                data=raw,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=2):
                pass
        except Exception:
            return

    threading.Thread(target=_send, daemon=True).start()


def forward_artifact_async(artifact: dict) -> None:
    raw = json.dumps(artifact, separators=(",", ":")).encode("utf-8")
    forward_bytes_async(raw)


def pick_mode() -> str:
    r = random.random()
    if r < P_GOOD:
        return "GOOD"
    r -= P_GOOD
    if r < P_BINDING_FAIL:
        return "BINDING_FAIL"
    r -= P_BINDING_FAIL
    if r < P_MALFORMED_JSON:
        return "MALFORMED_JSON"
    return "DROP_FORWARD"


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

        request_repr = hashlib.sha256(request_bytes).hexdigest()
        mode = pick_mode()

        if mode == "DROP_FORWARD":
            # FAILURE: drop forward (provider never sees anything)
            pass

        elif mode == "MALFORMED_JSON":
            # FAILURE: intentionally malformed JSON
            forward_bytes_async(b'{"request_repr":')

        else:
            # Build artifact (binding either correct or deliberately wrong)
            if mode == "GOOD":
                binding = nuvl_bind(request_repr, verification_context)
            else:
                # FAILURE: deliberately wrong binding
                binding = "00" * 32

            artifact = {
                "request_repr": request_repr,
                "verification_context": verification_context,
                "binding": binding,
            }
            forward_artifact_async(artifact)

        self.send_response(204)
        self.end_headers()


def start_nuvl():
    HTTPServer((NUVL_HOST, NUVL_PORT), NUVLHandler).serve_forever()


def requester_send(payload: bytes, verification_context: str) -> int:
    url = f"http://127.0.0.1:{NUVL_PORT}/nuvl"
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/octet-stream",
            "X-Verification-Context": verification_context,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=2) as resp:
        return resp.status


def main():
    if RANDOM_SEED is None:
        random.seed()
    else:
        random.seed(RANDOM_SEED)

    threading.Thread(target=start_provider, daemon=True).start()
    threading.Thread(target=start_nuvl, daemon=True).start()
    time.sleep(0.6)

    size_bytes = os.path.getsize(__file__)
    print(f"Reference size: {size_bytes} bytes ({size_bytes/1024:.1f} KiB)")
    print("")
    print("=" * 58)
    print("REQUESTER BENCHMARK (transport + forward + provider ingest)")
    print("=" * 58)
    print(f"Total requests: {TOTAL_REQUESTS}")
    print(f"Mix: GOOD={P_GOOD:.2f}, BIND_FAIL={P_BINDING_FAIL:.2f}, MAL_JSON={P_MALFORMED_JSON:.2f}, DROP={P_DROP_FORWARD:.2f}")
    print("")

    payload = b'{"op":"transfer","amount":100,"to":"acct_123"}'

    start = time.perf_counter()
    for i in range(1, TOTAL_REQUESTS + 1):
        requester_send(payload, EXPECTED_CONTEXT)
        if REQUESTER_PROGRESS_EVERY and (i % REQUESTER_PROGRESS_EVERY == 0):
            print(f"Requester progress: {i}/{TOTAL_REQUESTS}")
    end = time.perf_counter()

    total_ms = (end - start) * 1000.0
    avg_ms = total_ms / float(TOTAL_REQUESTS)
    throughput = 1000.0 / avg_ms if avg_ms > 0 else 0.0

    print("")
    print(f"Total time:            {total_ms:.2f} ms")
    print(f"Average per request:   {avg_ms:.4f} ms")
    print(f"Approx throughput:     {throughput:.0f} req/sec")

    # Let async forwards land before summarizing.
    time.sleep(0.4)
    print(provider_summary())

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
