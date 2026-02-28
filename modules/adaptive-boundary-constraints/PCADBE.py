#!/usr/bin/env python3
# Copyright (c) 2026 Seth Brian Wells. All rights reserved.
# Proprietary. Commercial licensing available. Research licensing available.
# Use of this file is governed by the license terms in the module-license-notice folder.

from http.server import BaseHTTPRequestHandler, HTTPServer
import hashlib
import hmac
import json
import os
import threading
import time
import urllib.request

# -------------------------
# Network configuration
# -------------------------
PROVIDER_HOST = "0.0.0.0"
PROVIDER_PORT = 9090

INTERMEDIARY_HOST = "0.0.0.0"
INTERMEDIARY_PORT = 8080

PROVIDER_INGEST_URL = f"http://127.0.0.1:{PROVIDER_PORT}/ingest"

MAX_REQUEST_BYTES = 1024 * 64  # 64KB

# -------------------------
# Provider-only secrets / tags
# -------------------------
PROVIDER_BOUNDARY_KEY = b"PROVIDER_ONLY_BOUNDARY_KEY_CHANGE_ME"

BIND_TAG = "BIND_V1"
BOUNDARY_TAG = "BOUNDARY_V1"

# Provider-only model seed (demo only). Intermediary has no access.
PROVIDER_MODEL_SEED = b"PROVIDER_ONLY_MODEL_SEED_CHANGE_ME"

# Demo: keep this set so the single request is a working reference.
EXPECTED_CONTEXT = "CTX_ALPHA"


# -------------------------
# Mechanical binding (intermediary)
# -------------------------
def mechanical_bind(request_repr_hex: str, verification_context: str) -> str:
    msg = (BIND_TAG + "|" + request_repr_hex + "|" + verification_context).encode("utf-8")
    return hashlib.sha256(msg).hexdigest()


def forward_artifact_async(artifact: dict) -> None:
    def _send():
        try:
            data = json.dumps(artifact).encode("utf-8")
            req = urllib.request.Request(
                PROVIDER_INGEST_URL,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=2):
                pass
        except Exception:
            return

    threading.Thread(target=_send, daemon=True).start()


# -------------------------
# Provider-side adaptive evaluation
# -------------------------
def provider_adaptive_score(request_repr_hex: str, verification_context: str) -> float:
    material = (request_repr_hex + "|" + verification_context).encode("utf-8")
    digest = hmac.new(PROVIDER_MODEL_SEED, material, hashlib.sha256).digest()

    n = int.from_bytes(digest[:8], "big")
    score = (n % 10_000_000) / 10_000_000.0

    if verification_context == EXPECTED_CONTEXT:
        score = min(1.0, score + 0.25)

    return score


def provider_boundary_artifact(operation_id: str, stage: str, request_repr_hex: str) -> dict:
    ts = time.time_ns()
    payload = f"{BOUNDARY_TAG}|{operation_id}|{stage}|{request_repr_hex}|{ts}".encode("utf-8")
    sig = hmac.new(PROVIDER_BOUNDARY_KEY, payload, hashlib.sha256).hexdigest()

    return {
        "operation_id": operation_id,
        "stage": stage,
        "ts": ts,
        "sig": sig,
    }


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
            print("PROVIDER: NOT INITIATED")
            self.send_response(204)
            self.end_headers()
            return

        request_repr = artifact.get("request_repr", "")
        verification_context = artifact.get("verification_context", "")
        binding = artifact.get("binding", "")

        expected_binding = mechanical_bind(request_repr, verification_context)
        binding_ok = hmac.compare_digest(binding, expected_binding)

        score = provider_adaptive_score(request_repr, verification_context)

        initiated = bool(binding_ok and score >= 0.50)

        if initiated:
            operation_id = hashlib.sha256(
                (request_repr + "|" + verification_context).encode("utf-8")
            ).hexdigest()

            print("PROVIDER: INITIATED")

            start_b = provider_boundary_artifact(operation_id, "START", request_repr)
            complete_b = provider_boundary_artifact(operation_id, "COMPLETE", request_repr)

            print("PROVIDER_BOUNDARY_START:", start_b["sig"])
            print("PROVIDER_BOUNDARY_COMPLETE:", complete_b["sig"])
        else:
            print("PROVIDER: NOT INITIATED")

        self.send_response(204)
        self.end_headers()


def start_provider():
    HTTPServer((PROVIDER_HOST, PROVIDER_PORT), ProviderHandler).serve_forever()


# -------------------------
# Intermediary (conveyance only)
# -------------------------
class IntermediaryHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def do_POST(self):
        if self.path != "/relay":
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
        binding = mechanical_bind(request_repr, verification_context)

        artifact = {
            "request_repr": request_repr,
            "verification_context": verification_context,
            "binding": binding,
            "version": "REFERENCE_V1",
        }

        forward_artifact_async(artifact)

        self.send_response(204)
        self.end_headers()


def start_intermediary():
    HTTPServer((INTERMEDIARY_HOST, INTERMEDIARY_PORT), IntermediaryHandler).serve_forever()


# -------------------------
# Requester (single working request)
# -------------------------
def requester_send(payload: bytes, verification_context: str) -> int:
    url = f"http://127.0.0.1:{INTERMEDIARY_PORT}/relay"
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
    threading.Thread(target=start_provider, daemon=True).start()
    threading.Thread(target=start_intermediary, daemon=True).start()
    time.sleep(0.6)

    size_bytes = os.path.getsize(__file__)
    print(f"Reference size: {size_bytes} bytes ({size_bytes/1024:.1f} KiB)")

    payload = b'{"op":"transfer","amount":100,"to":"acct_123"}'

    print("Requester: sending request...")
    print("Requester saw status:", requester_send(payload, EXPECTED_CONTEXT))

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
