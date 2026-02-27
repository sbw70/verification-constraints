#!/usr/bin/env python3
# Copyright (c) 2026 Seth Brian Wells
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
import threading
import time
import urllib.request

PROVIDER_HOST = "0.0.0.0"
PROVIDER_PORT = 9090

NUVL_HOST = "0.0.0.0"
NUVL_PORT = 8080

PROVIDER_INGEST_URL = f"http://127.0.0.1:{PROVIDER_PORT}/ingest"

EXPECTED_CONTEXT = "CTX_ALPHA"
PROVIDER_HMAC_KEY = b"PROVIDER_ONLY_KEY_CHANGE_ME"

BIND_TAG = "NUVL_BIND_V1"
MAX_REQUEST_BYTES = 1024 * 64  # 64KB


def provider_expected_binding(request_repr_hex: str, verification_context: str) -> str:
    msg = (BIND_TAG + "|" + request_repr_hex + "|" + verification_context).encode("utf-8")
    return hashlib.sha256(msg).hexdigest()


def provider_boundary_signature(request_repr_hex: str, verification_context: str, binding: str) -> str:
    msg = (request_repr_hex + "|" + verification_context + "|" + binding).encode("utf-8")
    return hmac.new(PROVIDER_HMAC_KEY, msg, hashlib.sha256).hexdigest()


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

        initiated = False
        if verification_context == EXPECTED_CONTEXT:
            expected = provider_expected_binding(request_repr, verification_context)
            if binding == expected:
                initiated = True

        _ = provider_boundary_signature(request_repr, verification_context, binding)
        print("PROVIDER: INITIATED" if initiated else "PROVIDER: NOT INITIATED")

        self.send_response(204)
        self.end_headers()


def start_provider():
    HTTPServer((PROVIDER_HOST, PROVIDER_PORT), ProviderHandler).serve_forever()


def nuvl_bind(request_repr_hex: str, verification_context: str) -> str:
    msg = (BIND_TAG + "|" + request_repr_hex + "|" + verification_context).encode("utf-8")
    return hashlib.sha256(msg).hexdigest()


def forward_artifact_async(_artifact: dict) -> None:
    # FAILURE: drop forward (provider never sees anything)
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

        request_repr = hashlib.sha256(request_bytes).hexdigest()
        binding = nuvl_bind(request_repr, verification_context)

        artifact = {
            "request_repr": request_repr,
            "verification_context": verification_context,
            "binding": binding,
        }

        forward_artifact_async(artifact)

        # Requester sees constant 204 with blank body.
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
    threading.Thread(target=start_provider, daemon=True).start()
    threading.Thread(target=start_nuvl, daemon=True).start()
    time.sleep(0.6)

    size_bytes = os.path.getsize(__file__)
    print(f"Reference size: {size_bytes} bytes ({size_bytes/1024:.1f} KiB)")

    payload = b'{"op":"transfer","amount":100,"to":"acct_123"}'

    print("Requester: sending request 1...")
    print("Requester saw status:", requester_send(payload, EXPECTED_CONTEXT))

    print("Requester: sending request 2...")
    print("Requester saw status:", requester_send(payload, "CTX_SPOOFED"))

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
