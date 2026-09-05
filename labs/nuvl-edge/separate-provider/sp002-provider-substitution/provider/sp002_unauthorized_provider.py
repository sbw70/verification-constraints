#!/usr/bin/env python3
import base64
import json
import secrets
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from cryptography.hazmat.primitives import serialization

HOST = "0.0.0.0"
PORT = 8091
PROVIDER_ID = "laptop-ed25519-provider-01"
EXPECTED_CONTEXT = "field_led_demo"
TTL_SECONDS = 3600

BASE_DIR = Path(__file__).resolve().parent
PRIVATE_KEY_PATH = BASE_DIR / "sp002_unauthorized_private.pem"


def canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def b64url_encode(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def load_private_key():
    if not PRIVATE_KEY_PATH.exists():
        raise FileNotFoundError(
            "Missing existing Ed25519 private key: {}".format(PRIVATE_KEY_PATH)
        )
    return serialization.load_pem_private_key(
        PRIVATE_KEY_PATH.read_bytes(),
        password=None,
    )


PRIVATE_KEY = load_private_key()


def issue_artifact(payload):
    for field in ("device_id", "context", "requested_action", "nonce"):
        value = payload.get(field)
        if not isinstance(value, str) or not value:
            raise ValueError("missing_" + field)

    if payload["context"] != EXPECTED_CONTEXT:
        raise ValueError("wrong_context")

    if payload["requested_action"] != "accept":
        raise ValueError("unsupported_action")

    now = int(time.time())
    expiry = now + TTL_SECONDS
    if payload.get("test_mode") == "stale":
        expiry = now - 5

    artifact = {
        "alg": "Ed25519",
        "artifact_id": secrets.token_hex(12),
        "context": payload["context"],
        "decision": "accepted",
        "device_id": payload["device_id"],
        "expiry": expiry,
        "issued_at": now,
        "max_uses": 1,
        "nonce": payload["nonce"],
        "offline_allowed": True,
        "provider_id": PROVIDER_ID,
        "requested_action": payload["requested_action"],
        "version": 1,
    }

    signature = PRIVATE_KEY.sign(canonical_bytes(artifact))
    return {
        "artifact": artifact,
        "signature": b64url_encode(signature),
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def send_json(self, status, obj):
        body = canonical_bytes(obj)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(
                200,
                {
                    "status": "ok",
                    "provider": PROVIDER_ID,
                    "algorithm": "Ed25519",
                    "private_key_present": True,
                },
            )
            return
        self.send_json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path != "/issue-offline":
            self.send_json(404, {"error": "not_found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("request_not_object")

            package = issue_artifact(payload)
            artifact = package["artifact"]
            print(
                "ISSUED artifact_id={} mode={} device={} context={} action={} expiry={}".format(
                    artifact["artifact_id"],
                    payload.get("test_mode", "valid"),
                    artifact["device_id"],
                    artifact["context"],
                    artifact["requested_action"],
                    artifact["expiry"],
                ),
                flush=True,
            )
            self.send_json(200, package)
        except Exception as exc:
            self.send_json(400, {"error": repr(exc)})


def main():
    print("POC003_ED25519_OFFLINE_PROVIDER")
    print("Listening on {}:{}".format(HOST, PORT))
    print("Issue: POST /issue-offline")
    print("Private key:", PRIVATE_KEY_PATH)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
