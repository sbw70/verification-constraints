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

# -------------------------------------------------------------------
# Network (single intermediary, two independent provider domains)
# -------------------------------------------------------------------
INTERMEDIARY_HOST = "0.0.0.0"
INTERMEDIARY_PORT = 8080

PROVIDER_A_HOST = "0.0.0.0"
PROVIDER_A_PORT = 9090
PROVIDER_A_INGEST_URL = f"http://127.0.0.1:{PROVIDER_A_PORT}/ingest"

PROVIDER_B_HOST = "0.0.0.0"
PROVIDER_B_PORT = 9091
PROVIDER_B_INGEST_URL = f"http://127.0.0.1:{PROVIDER_B_PORT}/ingest"

# -------------------------------------------------------------------
# Mechanical binding (intermediary: no secrets, no policy, no outcome)
# -------------------------------------------------------------------
BIND_TAG = "BIND_V1"
MAX_REQUEST_BYTES = 1024 * 64  # 64KB

# Demo-only: expected context per domain (neutral naming)
EXPECTED_CONTEXT_A = "CTX_ALPHA"
EXPECTED_CONTEXT_B = "CTX_BRAVO"

# Provider-only secrets (intermediary has no access)
PROVIDER_A_HMAC_KEY = b"PROVIDER_A_ONLY_KEY_CHANGE_ME"
PROVIDER_B_HMAC_KEY = b"PROVIDER_B_ONLY_KEY_CHANGE_ME"


def mechanical_binding(request_repr_hex: str, verification_context: str, domain: str) -> str:
    # Purely mechanical, deterministic binding (no secrets).
    msg = (BIND_TAG + "|" + domain + "|" + request_repr_hex + "|" + verification_context).encode("utf-8")
    return hashlib.sha256(msg).hexdigest()


def provider_expected_binding(request_repr_hex: str, verification_context: str, domain: str) -> str:
    return mechanical_binding(request_repr_hex, verification_context, domain)


def provider_boundary_signature(provider_key: bytes, request_repr_hex: str, verification_context: str, binding: str) -> str:
    # Provider-side-only signature (not returned to intermediary).
    msg = (request_repr_hex + "|" + verification_context + "|" + binding).encode("utf-8")
    return hmac.new(provider_key, msg, hashlib.sha256).hexdigest()


def post_json_async(url: str, payload: dict) -> None:
    def _send():
        try:
            data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=2):
                pass
        except Exception:
            return

    threading.Thread(target=_send, daemon=True).start()


# -------------------------------------------------------------------
# Providers (authority): domain-local evaluation + initiation
# -------------------------------------------------------------------
def make_provider_handler(domain: str, expected_context: str, provider_key: bytes):
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
                print(f"{domain}: NOT INITIATED")
                self.send_response(204)
                self.end_headers()
                return

            request_repr = artifact.get("request_repr", "")
            verification_context = artifact.get("verification_context", "")
            binding = artifact.get("binding", "")
            artifact_domain = artifact.get("domain", "")

            initiated = False

            # Domain must match (no cross-domain inference).
            if artifact_domain == domain:
                if verification_context == expected_context:
                    expected = provider_expected_binding(request_repr, verification_context, domain)
                    if binding == expected:
                        initiated = True

            # Provider-only signature computed inside provider boundary; not returned.
            _ = provider_boundary_signature(provider_key, request_repr, verification_context, binding)

            print(f"{domain}: INITIATED" if initiated else f"{domain}: NOT INITIATED")

            self.send_response(204)
            self.end_headers()

    return ProviderHandler


def start_provider(host: str, port: int, handler_cls):
    HTTPServer((host, port), handler_cls).serve_forever()


# -------------------------------------------------------------------
# Intermediary (conveyance-only): routes by X-Domain, forwards artifact, disengages
# -------------------------------------------------------------------
DOMAIN_ROUTE = {
    "DOMAIN_A": PROVIDER_A_INGEST_URL,
    "DOMAIN_B": PROVIDER_B_INGEST_URL,
}


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

        # Domain routing is transport-level selection only (no semantics).
        domain = self.headers.get("X-Domain", "")
        verification_context = self.headers.get("X-Verification-Context", "")

        target = DOMAIN_ROUTE.get(domain)
        if not target:
            # Constant response; intermediary does not emit error semantics.
            self.send_response(204)
            self.end_headers()
            return

        request_repr = hashlib.sha256(request_bytes).hexdigest()
        binding = mechanical_binding(request_repr, verification_context, domain)

        artifact = {
            "domain": domain,
            "request_repr": request_repr,
            "verification_context": verification_context,
            "binding": binding,
        }

        post_json_async(target, artifact)

        # Constant response: no receipt semantics, no provider outcome.
        self.send_response(204)
        self.end_headers()


def start_intermediary():
    HTTPServer((INTERMEDIARY_HOST, INTERMEDIARY_PORT), IntermediaryHandler).serve_forever()


# -------------------------------------------------------------------
# Requester (demo): send one request to each domain
# -------------------------------------------------------------------
def requester_send(payload: bytes, domain: str, verification_context: str) -> int:
    url = f"http://127.0.0.1:{INTERMEDIARY_PORT}/ingest"
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/octet-stream",
            "X-Domain": domain,
            "X-Verification-Context": verification_context,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=2) as resp:
        return resp.status


def main():
    # Start providers (two independent domains)
    threading.Thread(
        target=start_provider,
        args=(PROVIDER_A_HOST, PROVIDER_A_PORT, make_provider_handler("DOMAIN_A", EXPECTED_CONTEXT_A, PROVIDER_A_HMAC_KEY)),
        daemon=True,
    ).start()

    threading.Thread(
        target=start_provider,
        args=(PROVIDER_B_HOST, PROVIDER_B_PORT, make_provider_handler("DOMAIN_B", EXPECTED_CONTEXT_B, PROVIDER_B_HMAC_KEY)),
        daemon=True,
    ).start()

    # Start intermediary
    threading.Thread(target=start_intermediary, daemon=True).start()
    time.sleep(0.6)

    size_bytes = os.path.getsize(__file__)
    print(f"Reference size: {size_bytes} bytes ({size_bytes/1024:.1f} KiB)")

    payload = b'{"op":"transfer","amount":100,"to":"acct_123"}'

    # Working references (one per domain)
    print("Requester: sending DOMAIN_A request...")
    print("Requester saw status:", requester_send(payload, "DOMAIN_A", EXPECTED_CONTEXT_A))

    print("Requester: sending DOMAIN_B request...")
    print("Requester saw status:", requester_send(payload, "DOMAIN_B", EXPECTED_CONTEXT_B))

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
