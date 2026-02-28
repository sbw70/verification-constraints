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
# Network
# -------------------------------------------------------------------
NUVL_HOST = "0.0.0.0"
NUVL_PORT = 8080

ASSOC_HOST = "0.0.0.0"
ASSOC_PORT = 9191
ASSOC_INGEST_URL = f"http://127.0.0.1:{ASSOC_PORT}/boundary"

PROVIDER_A_HOST = "0.0.0.0"
PROVIDER_A_PORT = 9090
PROVIDER_A_INGEST_URL = f"http://127.0.0.1:{PROVIDER_A_PORT}/ingest"

PROVIDER_B_HOST = "0.0.0.0"
PROVIDER_B_PORT = 9091
PROVIDER_B_INGEST_URL = f"http://127.0.0.1:{PROVIDER_B_PORT}/ingest"

PROVIDER_C_HOST = "0.0.0.0"
PROVIDER_C_PORT = 9092
PROVIDER_C_INGEST_URL = f"http://127.0.0.1:{PROVIDER_C_PORT}/ingest"

# -------------------------------------------------------------------
# Mechanical binding (NUVL: conveyance-only)
# -------------------------------------------------------------------
BIND_TAG = "NUVL_BIND_V1"
MAX_REQUEST_BYTES = 1024 * 64

EXPECTED_CONTEXT = "CTX_ALPHA"

PROVIDER_A_HMAC_KEY = b"PROVIDER_A_ONLY_KEY_CHANGE_ME"
PROVIDER_B_HMAC_KEY = b"PROVIDER_B_ONLY_KEY_CHANGE_ME"
PROVIDER_C_HMAC_KEY = b"PROVIDER_C_ONLY_KEY_CHANGE_ME"


def mechanical_binding(request_repr_hex: str, verification_context: str) -> str:
    msg = (BIND_TAG + "|" + request_repr_hex + "|" + verification_context).encode("utf-8")
    return hashlib.sha256(msg).hexdigest()


def provider_operation_id(request_repr_hex: str) -> str:
    return hashlib.sha256(request_repr_hex.encode("utf-8")).hexdigest()


def provider_generate_boundary_value(provider_id: str, operation_id: str, stage: str) -> str:
    entropy = str(time.time_ns())
    material = (provider_id + "|" + operation_id + "|" + stage + "|" + entropy).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def provider_boundary_signature(
    provider_hmac_key: bytes,
    operation_id: str,
    provider_id: str,
    stage: str,
    boundary_value: str,
) -> str:
    msg = (operation_id + "|" + provider_id + "|" + stage + "|" + boundary_value).encode("utf-8")
    return hmac.new(provider_hmac_key, msg, hashlib.sha256).hexdigest()


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
# Association (non-authoritative)
# -------------------------------------------------------------------
_ASSOC_LOCK = threading.Lock()
_ASSOC = {}
_ASSOC_CONFIRMED = set()


def assoc_record(operation_id: str, provider_id: str, stage: str, boundary_value: str) -> None:
    with _ASSOC_LOCK:
        op = _ASSOC.setdefault(operation_id, {})
        prov = op.setdefault(provider_id, {})
        prov[stage] = boundary_value


def assoc_completed_providers(operation_id: str) -> int:
    with _ASSOC_LOCK:
        op = _ASSOC.get(operation_id, {})
        return sum(1 for _, stages in op.items() if "COMPLETE" in stages)


class AssociationHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def do_POST(self):
        if self.path != "/boundary":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length > 0 else b""

        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            self.send_response(204)
            self.end_headers()
            return

        operation_id = payload.get("operation_id", "")
        provider_id = payload.get("provider_id", "")
        stage = payload.get("stage", "")
        boundary_value = payload.get("boundary_value", "")

        if not (operation_id and provider_id and stage and boundary_value):
            self.send_response(204)
            self.end_headers()
            return

        assoc_record(operation_id, provider_id, stage, boundary_value)

        if operation_id not in _ASSOC_CONFIRMED and assoc_completed_providers(operation_id) >= 3:
            _ASSOC_CONFIRMED.add(operation_id)
            print("ASSOCIATION: CONFIRMED (3 providers COMPLETE)")

        self.send_response(204)
        self.end_headers()


def start_association():
    HTTPServer((ASSOC_HOST, ASSOC_PORT), AssociationHandler).serve_forever()


# -------------------------------------------------------------------
# Providers (authority)
# -------------------------------------------------------------------
def make_provider_handler(provider_id: str, provider_hmac_key: bytes):
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
                self.send_response(204)
                self.end_headers()
                return

            request_repr = artifact.get("request_repr", "")
            verification_context = artifact.get("verification_context", "")
            binding = artifact.get("binding", "")

            initiated = False
            if verification_context == EXPECTED_CONTEXT:
                expected = mechanical_binding(request_repr, verification_context)
                if binding == expected:
                    initiated = True

            if initiated:
                op_id = provider_operation_id(request_repr)

                start_val = provider_generate_boundary_value(provider_id, op_id, "START")
                complete_val = provider_generate_boundary_value(provider_id, op_id, "COMPLETE")

                _ = provider_boundary_signature(provider_hmac_key, op_id, provider_id, "START", start_val)
                _ = provider_boundary_signature(provider_hmac_key, op_id, provider_id, "COMPLETE", complete_val)

                post_json_async(ASSOC_INGEST_URL, {
                    "operation_id": op_id,
                    "provider_id": provider_id,
                    "stage": "START",
                    "boundary_value": start_val,
                })
                post_json_async(ASSOC_INGEST_URL, {
                    "operation_id": op_id,
                    "provider_id": provider_id,
                    "stage": "COMPLETE",
                    "boundary_value": complete_val,
                })

                print(f"{provider_id}: INITIATED")

            self.send_response(204)
            self.end_headers()

    return ProviderHandler


def start_provider(host: str, port: int, handler_cls):
    HTTPServer((host, port), handler_cls).serve_forever()


# -------------------------------------------------------------------
# NUVL (neutral intermediary)
# -------------------------------------------------------------------
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
        binding = mechanical_binding(request_repr, verification_context)

        artifact = {
            "request_repr": request_repr,
            "verification_context": verification_context,
            "binding": binding,
        }

        post_json_async(PROVIDER_A_INGEST_URL, artifact)
        post_json_async(PROVIDER_B_INGEST_URL, artifact)
        post_json_async(PROVIDER_C_INGEST_URL, artifact)

        self.send_response(204)
        self.end_headers()


def start_nuvl():
    HTTPServer((NUVL_HOST, NUVL_PORT), NUVLHandler).serve_forever()


# -------------------------------------------------------------------
# Requester
# -------------------------------------------------------------------
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
    print("Starting Multi-Provider Reference")

    threading.Thread(target=start_association, daemon=True).start()

    threading.Thread(
        target=start_provider,
        args=(PROVIDER_A_HOST, PROVIDER_A_PORT, make_provider_handler("PROVIDER_A", PROVIDER_A_HMAC_KEY)),
        daemon=True,
    ).start()
    threading.Thread(
        target=start_provider,
        args=(PROVIDER_B_HOST, PROVIDER_B_PORT, make_provider_handler("PROVIDER_B", PROVIDER_B_HMAC_KEY)),
        daemon=True,
    ).start()
    threading.Thread(
        target=start_provider,
        args=(PROVIDER_C_HOST, PROVIDER_C_PORT, make_provider_handler("PROVIDER_C", PROVIDER_C_HMAC_KEY)),
        daemon=True,
    ).start()

    threading.Thread(target=start_nuvl, daemon=True).start()
    time.sleep(1)

    payload = b'{"op":"transfer","amount":100,"to":"acct_123"}'

    print("Requester sending request...")
    print("Requester saw status:", requester_send(payload, EXPECTED_CONTEXT))

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
