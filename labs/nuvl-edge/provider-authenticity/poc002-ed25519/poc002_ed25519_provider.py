#!/usr/bin/env python3
import argparse
import base64
import hashlib
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

HOST = "203.0.113.10"
PORT = 8091
EXPECTED_CONTEXT = "field_led_demo"
PROVIDER_ID = "laptop-ed25519-provider-01"

BASE_DIR = Path(__file__).resolve().parent
PRIVATE_KEY_PATH = BASE_DIR / "poc002_ed25519_private.pem"
PUBLIC_KEY_PATH = BASE_DIR / "poc002_ed25519_public.pem"


def canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def b64url_encode(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def bounded_request(payload):
    return {
        "context": payload.get("context"),
        "device_id": payload.get("device_id"),
        "nonce": payload.get("nonce"),
        "requested_action": payload.get("requested_action"),
    }


def request_repr(payload):
    return hashlib.sha256(canonical_bytes(bounded_request(payload))).hexdigest()


def ensure_keypair():
    if PRIVATE_KEY_PATH.exists():
        private_key = serialization.load_pem_private_key(
            PRIVATE_KEY_PATH.read_bytes(),
            password=None,
        )
    else:
        private_key = Ed25519PrivateKey.generate()
        PRIVATE_KEY_PATH.write_bytes(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    PUBLIC_KEY_PATH.write_bytes(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    return private_key


PRIVATE_KEY = None


def provider_decision(payload):
    if payload.get("context") != EXPECTED_CONTEXT:
        return "denied", "wrong_context"

    action = payload.get("requested_action")
    if action == "accept":
        return "accepted", "provider_admissible"
    if action == "deny":
        return "denied", "unauthorized_request"
    if action == "deny_stale_replay":
        return "denied", "stale_replay_malformed"
    return "denied", "unknown_action"


def issue_artifact(payload):
    now = int(time.time())
    mode = payload.get("test_mode", "valid")
    decision, reason = provider_decision(payload)

    artifact = {
        "alg": "Ed25519",
        "context": payload.get("context"),
        "decision": decision,
        "device_id": payload.get("device_id"),
        "expiry": now + 30,
        "issued_at": now,
        "nonce": payload.get("nonce"),
        "provider_id": PROVIDER_ID,
        "reason": reason,
        "request_repr": request_repr(payload),
        "requested_action": payload.get("requested_action"),
        "version": 1,
    }

    if mode == "stale":
        artifact["expiry"] = now - 5
    elif mode == "context_mismatch":
        artifact["context"] = "artifact_wrong_context"
    elif mode == "nonce_mismatch":
        artifact["nonce"] = "artifact_wrong_nonce"

    signature = PRIVATE_KEY.sign(canonical_bytes(artifact))

    if mode == "tampered":
        artifact["decision"] = (
            "denied" if artifact["decision"] == "accepted" else "accepted"
        )

    return {
        "artifact": artifact,
        "signature": None if mode == "unsigned" else b64url_encode(signature),
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
                },
            )
            return
        self.send_json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path != "/issue":
            self.send_json(404, {"error": "not_found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("request must be an object")

            for field in ("device_id", "context", "requested_action", "nonce"):
                if not isinstance(payload.get(field), str) or not payload[field]:
                    raise ValueError("missing_" + field)

            response = issue_artifact(payload)
            print(
                "ISSUED mode={} device={} context={} action={} nonce={}".format(
                    payload.get("test_mode", "valid"),
                    payload["device_id"],
                    payload["context"],
                    payload["requested_action"],
                    payload["nonce"],
                ),
                flush=True,
            )
            self.send_json(200, response)
        except Exception as exc:
            self.send_json(400, {"error": repr(exc)})


def main():
    global PRIVATE_KEY
    parser = argparse.ArgumentParser()
    parser.add_argument("--init-only", action="store_true")
    args = parser.parse_args()

    PRIVATE_KEY = ensure_keypair()

    print("PRIVATE_KEY", PRIVATE_KEY_PATH)
    print("PUBLIC_KEY", PUBLIC_KEY_PATH)

    if args.init_only:
        print("POC002_KEYPAIR_READY")
        return

    print("POC002_ED25519_PROVIDER")
    print("Listening on {}:{}".format(HOST, PORT))
    print("Health: GET /health")
    print("Issue:  POST /issue")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
