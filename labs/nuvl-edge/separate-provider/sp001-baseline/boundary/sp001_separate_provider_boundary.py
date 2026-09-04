#!/usr/bin/env python3
import base64
import json
import os
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization

HOST = "0.0.0.0"
PORT = 8089
PROVIDER_BASE = "http://192.168.0.240:8091"
PROVIDER_ISSUE_URL = PROVIDER_BASE + "/issue-offline"
PROVIDER_HEALTH_URL = PROVIDER_BASE + "/health"
PUBLIC_KEY_PATH = Path("/home/seth/poc002_ed25519_public.pem")
SPENT_STATE_PATH = Path("/home/seth/poc004_spent_state_archer.json")
PROVIDER_TIMEOUT_S = 3
EXPECTED_PROVIDER_ID = "laptop-ed25519-provider-01"

PUBLIC_KEY = serialization.load_pem_public_key(PUBLIC_KEY_PATH.read_bytes())
STATE_LOCK = threading.Lock()
SPENT = {}


def canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def b64url_decode(text):
    raw = text.encode("ascii")
    raw += b"=" * ((4 - len(raw) % 4) % 4)
    return base64.urlsafe_b64decode(raw)


def atomic_write_json(path, obj):
    temp_path = path.with_name(path.name + ".tmp")
    data = canonical_bytes(obj)

    with open(temp_path, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())

    os.replace(temp_path, path)

    dir_fd = os.open(str(path.parent), os.O_RDONLY)
    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)


def state_document(entries):
    return {
        "version": 1,
        "spent": entries,
    }


def persist_state(entries):
    atomic_write_json(SPENT_STATE_PATH, state_document(entries))


def load_state():
    if not SPENT_STATE_PATH.exists():
        return {}

    raw = json.loads(SPENT_STATE_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("version") != 1:
        raise ValueError("invalid_replay_state_document")

    stored = raw.get("spent")
    if not isinstance(stored, dict):
        raise ValueError("invalid_replay_state_entries")

    now = int(time.time())
    loaded = {}

    for artifact_id, expiry in stored.items():
        if not isinstance(artifact_id, str) or not artifact_id:
            continue
        try:
            expiry_int = int(expiry)
        except Exception:
            continue
        if expiry_int >= now:
            loaded[artifact_id] = expiry_int

    if loaded != stored:
        persist_state(loaded)

    return loaded


def prune_expired(entries, now):
    return {
        artifact_id: expiry
        for artifact_id, expiry in entries.items()
        if int(expiry) >= now
    }


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
        "boundary": "poc004_persistent_replay_pi",
        "provider_contacted_for_spend": False,
    }


def verify_issuance_binding(issue_request, package):
    verified, artifact, reason = verify_signature(package)
    artifact_id = artifact.get("artifact_id") if isinstance(artifact, dict) else None

    if not verified:
        return deny(reason, False, artifact_id)

    for field in ("device_id", "context", "requested_action", "nonce"):
        if artifact.get(field) != issue_request.get(field):
            return deny("issuance_binding_mismatch_" + field, True, artifact_id)

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
        "boundary": "poc004_persistent_replay_pi",
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

    now = int(time.time())

    if expiry < now:
        return deny("stale_artifact", True, artifact_id)

    if artifact.get("decision") != "accepted":
        return deny("artifact_not_accepted", True, artifact_id)

    if artifact.get("offline_allowed") is not True:
        return deny("offline_not_allowed", True, artifact_id)

    if artifact.get("max_uses") != 1:
        return deny("invalid_max_uses", True, artifact_id)

    for field in ("device_id", "context", "requested_action", "nonce"):
        if artifact.get(field) != spend_request.get(field):
            return deny("spend_binding_mismatch_" + field, True, artifact_id)

    with STATE_LOCK:
        current = prune_expired(SPENT, now)

        if artifact_id in current:
            if current != SPENT:
                try:
                    persist_state(current)
                    SPENT.clear()
                    SPENT.update(current)
                except Exception:
                    pass
            return deny("replay_detected", True, artifact_id)

        candidate = dict(current)
        candidate[artifact_id] = expiry

        try:
            persist_state(candidate)
        except Exception:
            return deny("replay_state_persist_failed", True, artifact_id)

        SPENT.clear()
        SPENT.update(candidate)

    return {
        "decision": "accepted",
        "reason": "offline_artifact_admissible",
        "provider_verified": True,
        "artifact_id": artifact_id,
        "boundary": "poc004_persistent_replay_pi",
        "provider_contacted_for_spend": False,
        "uses_consumed": 1,
        "max_uses": 1,
        "replay_state_persisted_before_accept": True,
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
            with STATE_LOCK:
                spent_count = len(SPENT)
            self.send_json(
                200,
                {
                    "status": "ok",
                    "boundary": "poc004_persistent_replay_pi",
                    "public_key_loaded": True,
                    "spent_count": spent_count,
                    "replay_state_persistent": True,
                    "replay_state_path": str(SPENT_STATE_PATH),
                },
            )
            return

        if self.path == "/provider-status":
            self.send_json(
                200,
                {
                    "provider_available": provider_available(),
                    "provider_url": PROVIDER_BASE,
                },
            )
            return

        self.send_json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path == "/issue":
            try:
                payload = self.read_json()
                provider_package = send_provider_request(PROVIDER_ISSUE_URL, payload)
                response = verify_issuance_binding(payload, provider_package)
            except urllib.error.URLError:
                response = deny("provider_unavailable", False)
            except Exception as exc:
                response = deny("issuance_error_" + type(exc).__name__, False)

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
                response = deny("spend_error_" + type(exc).__name__, False)

            with STATE_LOCK:
                spent_count = len(SPENT)

            print(
                "SPEND decision={} reason={} verified={} artifact_id={} spent_count={} persisted={}".format(
                    response.get("decision"),
                    response.get("reason"),
                    response.get("provider_verified"),
                    response.get("artifact_id"),
                    spent_count,
                    response.get("replay_state_persisted_before_accept"),
                ),
                flush=True,
            )
            self.send_json(200, response)
            return

        self.send_json(404, {"error": "not_found"})


def main():
    global SPENT

    SPENT = load_state()

    print("POC004_PERSISTENT_REPLAY_PI_BOUNDARY")
    print("Listening on {}:{}".format(HOST, PORT))
    print("Provider:", PROVIDER_BASE)
    print("Public key:", PUBLIC_KEY_PATH)
    print("Private key present on Pi: False")
    print("Replay state:", SPENT_STATE_PATH)
    print("Persistent replay entries loaded:", len(SPENT))

    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
