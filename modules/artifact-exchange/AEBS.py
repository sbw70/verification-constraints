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

PROVIDER_HOST = "0.0.0.0"
PROVIDER_PORT = 19090

INTERMEDIARY_HOST = "0.0.0.0"
INTERMEDIARY_PORT = 18080

PROVIDER_INGEST_URL = f"http://127.0.0.1:{PROVIDER_PORT}/ingest"

EXPECTED_CONTEXT = "CTX_ALPHA"
PROVIDER_HMAC_KEY = b"PROVIDER_ONLY_KEY_CHANGE_ME"

BIND_TAG = "BIND_V1"
MAX_REQUEST_BYTES = 1024 * 64  # 64KB

VALID_ARTIFACT_TOKEN = "valid-provider-token"


def provider_expected_binding(request_repr_hex: str, verification_context: str) -> str:
    msg = (BIND_TAG + "|" + request_repr_hex + "|" + verification_context).encode("utf-8")
    return hashlib.sha256(msg).hexdigest()


def provider_boundary_signature(
    request_repr_hex: str,
    verification_context: str,
    binding: str,
    artifact_token: str,
) -> str:
    msg = (request_repr_hex + "|" + verification_context + "|" + binding + "|" + artifact_token).encode("utf-8")
    return hmac.new(PROVIDER_HMAC_KEY, msg, hashlib.sha256).hexdigest()


def provider_generate_boundary(stage: str, operation_id: str) -> str:
    payload = f"{stage}|{operation_id}|{time.time_ns()}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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
            # Provider stays silent to the sender; only emits its own local outcome.
            print("PROVIDER: NOT INITIATED")
            self.send_response(204)
            self.end_headers()
            return

        request_repr = artifact.get("request_repr", "")
        verification_context = artifact.get("verification_context", "")
        binding = artifact.get("binding", "")
        artifact_token = artifact.get("artifact_token", "")

        initiated = False
        if verification_context == EXPECTED_CONTEXT:
            expected = provider_expected_binding(request_repr, verification_context)
            if binding == expected and artifact_token == VALID_ARTIFACT_TOKEN:
                initiated = True

        # Provider-only signature computed inside provider boundary; not returned.
        _ = provider_boundary_signature(request_repr, verification_context, binding, artifact_token)

        if initiated:
            operation_id = hashlib.sha256((request_repr + "|" + verification_context).encode("utf-8")).hexdigest()
            boundary_start = provider_generate_boundary("START", operation_id)
            boundary_complete = provider_generate_boundary("COMPLETE", operation_id)

            print("PROVIDER: INITIATED")
            print("PROVIDER_BOUNDARY_START:", boundary_start)
            print("PROVIDER_BOUNDARY_COMPLETE:", boundary_complete)
        else:
            print("PROVIDER: NOT INITIATED")

        self.send_response(204)
        self.end_headers()


def start_provider():
    try:
        HTTPServer((PROVIDER_HOST, PROVIDER_PORT), ProviderHandler).serve_forever()
    except Exception as e:
        print("PROVIDER: SERVER ERROR:", repr(e))


def intermediary_bind(request_repr_hex: str, verification_context: str) -> str:
    msg = (BIND_TAG + "|" + request_repr_hex + "|" + verification_context).encode("utf-8")
    return hashlib.sha256(msg).hexdigest()


def forward_artifact_async(artifact: dict) -> None:
    def _send():
        try:
            data = json.dumps(artifact, separators=(",", ":")).encode("utf-8")
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


class IntermediaryHandler(BaseHTTPRequestHandler):
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

        request_bytes = self.rfile.read(length) if length > 0 else b""

        verification_context = self.headers.get("X-Verification-Context", "")
        artifact_token = self.headers.get("X-Artifact-Token", "")

        request_repr = hashlib.sha256(request_bytes).hexdigest()
        binding = intermediary_bind(request_repr, verification_context)

        artifact = {
            "request_repr": request_repr,
            "verification_context": verification_context,
            "binding": binding,
            "artifact_token": artifact_token,
        }

        forward_artifact_async(artifact)

        # Constant response; intermediary does not report provider outcome.
        self.send_response(204)
        self.end_headers()


def start_intermediary():
    try:
        HTTPServer((INTERMEDIARY_HOST, INTERMEDIARY_PORT), IntermediaryHandler).serve_forever()
    except Exception as e:
        print("INTERMEDIARY: SERVER ERROR:", repr(e))


def requester_send(payload: bytes, verification_context: str, artifact_token: str) -> int:
    url = f"http://127.0.0.1:{INTERMEDIARY_PORT}/ingest"
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/octet-stream",
            "X-Verification-Context": verification_context,
            "X-Artifact-Token": artifact_token,
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

    payload = b'{"operation":"transfer_funds","amount":100,"to":"acct_123"}'

    print("Requester: sending request...")
    print("Requester saw status:", requester_send(payload, EXPECTED_CONTEXT, VALID_ARTIFACT_TOKEN))

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
