#!/usr/bin/env python3
import base64
import json
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization

HOST = "0.0.0.0"
PORT = 8089
PROVIDER_BASE = "http://YOUR PC IP:8091"
PROVIDER_ISSUE_URL = PROVIDER_BASE + "/issue-offline"
PROVIDER_HEALTH_URL = PROVIDER_BASE + "/health"
PUBLIC_KEY_PATH = Path("/home/seth/poc002_ed25519_public.pem")
PROVIDER_TIMEOUT_S = 3
EXPECTED_PROVIDER_ID = "laptop-ed25519-provider-01"

PUBLIC_KEY = serialization.load_pem_public_key(PUBLIC_KEY_PATH.read_bytes())
SPENT_IDS = set()


def canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def b64url_decode(text):
    raw = text.encode("ascii")
    raw += b"=" * ((4 - len(raw) % 4) % 4)
    return base64.urlsafe_b64decode(raw)


def send_provider_request(url, payload=None, timeout=PROVIDER_TIMEOUT_S):
    if payload is None:
        req = urllib.request.Request(url, method="GET")
    else:
        req = urllib.request.Request(
            url,
            data=canonical_bytes(payload),
            method="POST",
            headers={"Content-Type": "application/json"},
        )

    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def provider_available():
    try:
        response = send_provider_request(PROVIDER_HEALTH_URL, timeout=1.5)
        return response.get("status") == "ok"
    except Exception:
        return False


def verify_signature(package):
    if not isinstance(package, dict):
        return False, None, "package_not_object"

    artifact = package.get("artifact")
    signature_text = package.get("signature")

    if not isinstance(artifact, dict):
        return False, None, "missing_artifact"

    if not isinstance(signature_text, str) or not signature_text:
        return False, artifact, "missing_signature"

    try:
        PUBLIC_KEY.verify(
            b64url_decode(signature_text),
            canonical_bytes(artifact),
        )
    except (InvalidSignature, ValueError, TypeError):
        return False, artifact, "invalid_provider_signature"

    if artifact.get("alg") != "Ed25519":
        return False, artifact, "wrong_algorithm"

    if artifact.get("provider_id") != EXPECTED_PROVIDER_ID:
        return False, artifact, "wrong_provider_id"

    return True, artifact, None


def deny(reason, verified=False, artifact_id=None):
    return {
        "decision": "denied",
        "reason": reason,
        "provider_verified": verified,
        "artifact_id": artifact_id,
        "boundary": "poc003_ed25519_offline_pi",
        "provider_contacted_for_spend": False,
    }


def verify_issuance_binding(issue_request, package):
    verified, artifact, reason = verify_signature(package)
    artifact_id = artifact.get("artifact_id") if isinstance(artifact, dict) else None

    if not verified:
        return deny(reason, False, artifact_id)

    for field in ("device_id", "context", "requested_action", "nonce"):
        if artifact.get(field) != issue_request.get(field):
            return deny(
                "issuance_binding_mismatch_" + field,
                True,
                artifact_id,
            )

    if artifact.get("decision") != "accepted":
        return deny("issuance_not_accepted", True, artifact_id)

    if artifact.get("offline_allowed") is not True:
        return deny("offline_not_allowed", True, artifact_id)

    if artifact.get("max_uses") != 1:
        return deny("invalid_max_uses", True, artifact_id)

    return {
        "decision": "issued",
        "reason": "provider_signed_bounded_artifact",
        "provider_verified": True,
        "artifact_id": artifact_id,
        "package": package,
        "boundary": "poc003_ed25519_offline_pi",
    }


def spend(package, spend_request):
    verified, artifact, reason = verify_signature(package)
    artifact_id = artifact.get("artifact_id") if isinstance(artifact, dict) else None

    if not verified:
        return deny(reason, False, artifact_id)

    try:
        expiry = int(artifact.get("expiry"))
    except Exception:
        return deny("invalid_expiry", True, artifact_id)

    if expiry < int(time.time()):
        return deny("stale_artifact", True, artifact_id)

    if artifact.get("decision") != "accepted":
        return deny("artifact_not_accepted", True, artifact_id)

    if artifact.get("offline_allowed") is not True:
        return deny("offline_not_allowed", True, artifact_id)

    if artifact.get("max_uses") != 1:
        return deny("invalid_max_uses", True, artifact_id)

    for field in ("device_id", "context", "requested_action", "nonce"):
        if artifact.get(field) != spend_request.get(field):
            return deny(
                "spend_binding_mismatch_" + field,
                True,
                artifact_id,
            )

    if artifact_id in SPENT_IDS:
        return deny("replay_detected", True, artifact_id)

    SPENT_IDS.add(artifact_id)

    return {
        "decision": "accepted",
        "reason": "offline_artifact_admissible",
        "provider_verified": True,
        "artifact_id": artifact_id,
        "boundary": "poc003_ed25519_offline_pi",
        "provider_contacted_for_spend": False,
        "uses_consumed": 1,
        "max_uses": 1,
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

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("request_not_object")
        return payload

    def do_GET(self):
        if self.path == "/health":
            self.send_json(
                200,
                {
                    "status": "ok",
                    "boundary": "poc003_ed25519_offline_pi",
                    "public_key_loaded": True,
                    "spent_count": len(SPENT_IDS),
                },
            )
            return

        if self.path == "/provider-status":
            available = provider_available()
            self.send_json(
                200,
                {
                    "provider_available": available,
                    "provider_url": PROVIDER_BASE,
                },
            )
            return

        self.send_json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path == "/issue":
            try:
                payload = self.read_json()
                provider_package = send_provider_request(
                    PROVIDER_ISSUE_URL,
                    payload,
                )
                response = verify_issuance_binding(payload, provider_package)
            except urllib.error.URLError:
                response = deny("provider_unavailable", False)
            except Exception as exc:
                response = deny(
                    "issuance_error_" + type(exc).__name__,
                    False,
                )

            print(
                "ISSUE decision={} reason={} verified={} artifact_id={}".format(
                    response.get("decision"),
                    response.get("reason"),
                    response.get("provider_verified"),
                    response.get("artifact_id"),
                ),
                flush=True,
            )
            self.send_json(200, response)
            return

        if self.path == "/spend":
            try:
                payload = self.read_json()
                response = spend(
                    payload.get("package"),
                    payload.get("spend_request") or {},
                )
            except Exception as exc:
                response = deny(
                    "spend_error_" + type(exc).__name__,
                    False,
                )

            print(
                "SPEND decision={} reason={} verified={} artifact_id={} spent_count={}".format(
                    response.get("decision"),
                    response.get("reason"),
                    response.get("provider_verified"),
                    response.get("artifact_id"),
                    len(SPENT_IDS),
                ),
                flush=True,
            )
            self.send_json(200, response)
            return

        self.send_json(404, {"error": "not_found"})


def main():
    print("POC003_ED25519_OFFLINE_PI_BOUNDARY")
    print("Listening on {}:{}".format(HOST, PORT))
    print("Provider:", PROVIDER_BASE)
    print("Public key:", PUBLIC_KEY_PATH)
    print("Private key present on Pi: False")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
