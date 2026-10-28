#!/usr/bin/env python3

import base64
import hashlib
import json
import os
import secrets
import threading
import time
import urllib.request

from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


HOST = "0.0.0.0"
PORT = 9090

PROVIDER_ID = "PROVIDER_A"

BIND_TAG = "NUVL_BIND_V1"
AUTH_ID_TAG = b"NUVL-MP-AUTH-ID-v1|"
AUTH_SIG_TAG = b"NUVL-MP-AUTH-v1|"
BOUNDARY_SIG_TAG = b"NUVL-MP-BOUNDARY-v1|"
OP_TAG = "NUVL-MP-OP-v1"

MAX_REQUEST_BYTES = 1024 * 64

ASSOCIATION_URL = "http://192.168.1.102:9191/boundary"

BASE_DIR = Path(__file__).resolve().parent

ISSUANCE_PUBLIC_KEY_PATH = (
    BASE_DIR / "provider_a_issuance_public.pem"
)

BOUNDARY_PRIVATE_KEY_PATH = (
    BASE_DIR / "provider_a_private.pem"
)

BOUNDARY_PUBLIC_KEY_PATH = (
    BASE_DIR / "provider_a_public.pem"
)

SPENT_STATE_PATH = (
    BASE_DIR / "provider_a_spent_state.json"
)

EXECUTION_LOG_PATH = (
    BASE_DIR / "provider_a_execution.jsonl"
)

CONSUME_LEDGER_PATH = BASE_DIR / "provider_a_consume_ledger.jsonl"

STATE_LOCK = threading.Lock()
EXECUTION_LOCK = threading.Lock()

SPENT = {}
EXECUTION_SEQ = 0


def canonical_bytes(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def utc_now():
    return datetime.now(
        timezone.utc
    ).isoformat(timespec="microseconds")


def b64url_encode(raw):
    return base64.urlsafe_b64encode(
        raw
    ).rstrip(b"=").decode("ascii")


def b64url_decode(text):
    raw = text.encode("ascii")
    raw += b"=" * ((4 - len(raw) % 4) % 4)
    return base64.urlsafe_b64decode(raw)


def load_ed25519_public(path):
    key = serialization.load_pem_public_key(
        path.read_bytes()
    )

    if not isinstance(
        key,
        Ed25519PublicKey,
    ):
        raise RuntimeError(
            "non_ed25519_public_key"
        )

    return key


def load_boundary_private():
    return serialization.load_pem_private_key(
        BOUNDARY_PRIVATE_KEY_PATH.read_bytes(),
        password=None,
    )


def key_id(public_key):
    raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    return "sha256:" + sha256_bytes(raw)


ISSUANCE_PUBLIC_KEY = load_ed25519_public(
    ISSUANCE_PUBLIC_KEY_PATH
)

BOUNDARY_PUBLIC_KEY = load_ed25519_public(
    BOUNDARY_PUBLIC_KEY_PATH
)

BOUNDARY_PRIVATE_KEY = load_boundary_private()

if (
    BOUNDARY_PRIVATE_KEY.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    !=
    BOUNDARY_PUBLIC_KEY.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
):
    raise RuntimeError(
        "boundary_keypair_mismatch"
    )

BOUNDARY_KEY_ID = key_id(
    BOUNDARY_PUBLIC_KEY
)


def mechanical_binding(
    request_repr,
    verification_context,
):
    material = (
        BIND_TAG
        + "|"
        + request_repr
        + "|"
        + verification_context
    ).encode("utf-8")

    return sha256_bytes(material)


def operation_id(expected_binding):
    material = (
        OP_TAG
        + "|"
        + expected_binding
    ).encode("utf-8")

    return sha256_bytes(material)


def authorization_core(auth):
    return {
        "version": auth.get("version"),
        "provider_id": auth.get(
            "provider_id"
        ),
        "request_repr": auth.get(
            "request_repr"
        ),
        "verification_context": auth.get(
            "verification_context"
        ),
        "nonce": auth.get("nonce"),
    }


def expected_authorization_id(auth):
    core = authorization_core(auth)

    return sha256_bytes(
        AUTH_ID_TAG
        + canonical_bytes(core)
    )


def atomic_write_json(path, obj):
    temp_path = path.with_name(
        path.name + ".tmp"
    )

    data = canonical_bytes(obj)

    with open(temp_path, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())

    os.replace(
        temp_path,
        path,
    )

    dir_fd = os.open(
        str(path.parent),
        os.O_RDONLY,
    )

    try:
        os.fsync(dir_fd)
    finally:
        os.close(dir_fd)


LEDGER_TAG = b"NUVL-MP-CONSUME-LEDGER-v1|"
LEDGER_SEQ = 0
LEDGER_HEAD = None
LEDGER_FAILED = False


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def validate_ledger(raw):
    spent = {}
    head = None
    entries = []
    if raw and not raw.endswith(b"\n"):
        raise ValueError("ledger_partial_line")
    for index, line in enumerate(raw.splitlines(), 1):
        entry = json.loads(line.decode("utf-8"), object_pairs_hook=strict_object)
        if not isinstance(entry, dict):
            raise ValueError("ledger_entry_not_object")
        if type(entry.get("version")) is not int or entry["version"] != 1:
            raise ValueError("ledger_version")
        if entry.get("provider_id") != PROVIDER_ID:
            raise ValueError("ledger_provider")
        if type(entry.get("ledger_seq")) is not int or entry["ledger_seq"] != index:
            raise ValueError("ledger_sequence")
        for field in ("authorization_id", "authorization_nonce", "operation_id"):
            if not isinstance(entry.get(field), str) or not entry[field]:
                raise ValueError("ledger_identity")
        if "previous_entry_hash" not in entry or entry["previous_entry_hash"] != head:
            raise ValueError("ledger_previous_hash")
        core = {k: v for k, v in entry.items() if k != "entry_hash"}
        if entry.get("entry_hash") != sha256_bytes(LEDGER_TAG + canonical_bytes(core)):
            raise ValueError("ledger_entry_hash")
        if canonical_bytes(entry) != line:
            raise ValueError("ledger_noncanonical")
        aid = entry["authorization_id"]
        if aid in spent:
            raise ValueError("ledger_duplicate_authorization")
        spent[aid] = {"nonce": entry["authorization_nonce"]}
        head = entry["entry_hash"]
        entries.append(entry)
    return spent, len(entries), head


def snapshot_document(entries):
    return {"version": 1, "spent": entries,
            "ledger_seq": LEDGER_SEQ, "ledger_head": LEDGER_HEAD}


def load_spent_state():
    global LEDGER_SEQ, LEDGER_HEAD, LEDGER_FAILED
    if not CONSUME_LEDGER_PATH.is_file():
        raise RuntimeError("consume_ledger_missing")
    try:
        spent, LEDGER_SEQ, LEDGER_HEAD = validate_ledger(CONSUME_LEDGER_PATH.read_bytes())
    except Exception as exc:
        raise RuntimeError("consume_ledger_invalid") from exc
    expected = snapshot_document(spent)
    recovery = None
    try:
        actual = json.loads(SPENT_STATE_PATH.read_text(encoding="utf-8"), object_pairs_hook=strict_object)
        if canonical_bytes(actual) != canonical_bytes(expected):
            recovery = "mismatch_or_stale"
    except FileNotFoundError:
        recovery = "missing"
    except Exception:
        recovery = "malformed_or_unreadable"
    if recovery:
        # Failure here aborts startup, before a request server exists.
        atomic_write_json(SPENT_STATE_PATH, expected)
        print(json.dumps({"event": "SNAPSHOT_RECOVERED_FROM_LEDGER",
                          "provider_id": PROVIDER_ID, "reason": recovery,
                          "ledger_seq": LEDGER_SEQ, "ledger_head": LEDGER_HEAD}, sort_keys=True), flush=True)
    LEDGER_FAILED = False
    return spent


def persist_spent(entries):
    atomic_write_json(SPENT_STATE_PATH, snapshot_document(entries))


def consume_authorization(auth_id, auth_nonce, op_id):
    global LEDGER_SEQ, LEDGER_HEAD, LEDGER_FAILED
    with STATE_LOCK:
        if auth_id in SPENT:
            return False, "auth_spent"
        if LEDGER_FAILED:
            return False, "auth_ledger_error"
        entry = {"version": 1, "provider_id": PROVIDER_ID,
                 "ledger_seq": LEDGER_SEQ + 1, "authorization_id": auth_id,
                 "authorization_nonce": auth_nonce, "operation_id": op_id,
                 "previous_entry_hash": LEDGER_HEAD}
        entry["entry_hash"] = sha256_bytes(LEDGER_TAG + canonical_bytes(entry))
        line = canonical_bytes(entry) + b"\n"
        try:
            # Deliberately no O_CREAT: ordinary consumes never initialize history.
            fd = os.open(str(CONSUME_LEDGER_PATH), os.O_WRONLY | os.O_APPEND)
            with os.fdopen(fd, "ab") as ledger:
                if ledger.write(line) != len(line):
                    raise OSError("short_ledger_write")
                ledger.flush()
                os.fsync(ledger.fileno())
        except Exception:
            # A partial write or failed fsync has uncertain durability. Never retry
            # a consume in this process, and never truncate/repair the history.
            LEDGER_FAILED = True
            return False, "auth_ledger_error"
        LEDGER_SEQ = entry["ledger_seq"]
        LEDGER_HEAD = entry["entry_hash"]
        SPENT[auth_id] = {"nonce": auth_nonce}
        try:
            persist_spent(SPENT)
        except Exception:
            # Durable ledger is authoritative even though this request cannot execute.
            return False, "auth_snapshot_error_consumed"
        return True, None


def append_execution(
    op_id,
    auth_id,
):
    global EXECUTION_SEQ

    with EXECUTION_LOCK:
        EXECUTION_SEQ += 1

        record = {
            "version": 1,
            "provider_id": PROVIDER_ID,
            "local_execution_seq": (
                EXECUTION_SEQ
            ),
            "local_utc": utc_now(),
            "local_monotonic_ns": (
                time.monotonic_ns()
            ),
            "operation_id": op_id,
            "authorization_id": auth_id,
            "result": "executed",
        }

        line = (
            canonical_bytes(record)
            + b"\n"
        )

        with open(
            EXECUTION_LOG_PATH,
            "ab",
        ) as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())

        return record


def boundary_value(
    op_id,
    stage,
):
    material = (
        PROVIDER_ID
        + "|"
        + op_id
        + "|"
        + stage
        + "|"
        + secrets.token_hex(16)
    ).encode("utf-8")

    return sha256_bytes(
        material
    )


def make_boundary_package(
    op_id,
    binding,
    stage,
    auth_id=None,
    auth_nonce=None,
    reason_code=None,
):
    event = {
        "version": 1,
        "operation_id": op_id,
        "binding": binding,
        "provider_id": PROVIDER_ID,
        "key_id": BOUNDARY_KEY_ID,
        "stage": stage,
        "boundary_value": boundary_value(
            op_id,
            stage,
        ),
        "authorization_id": auth_id,
        "authorization_nonce": auth_nonce,
        "reason_code": reason_code,
    }

    with STATE_LOCK:
        event["ledger_seq"] = LEDGER_SEQ
        event["ledger_head"] = LEDGER_HEAD

    signature = BOUNDARY_PRIVATE_KEY.sign(
        BOUNDARY_SIG_TAG
        + canonical_bytes(event)
    )

    return {
        "alg": "Ed25519",
        "event": event,
        "signature": b64url_encode(
            signature
        ),
    }


def send_boundary(package):
    try:
        body = canonical_bytes(
            package
        )

        req = urllib.request.Request(
            ASSOCIATION_URL,
            data=body,
            headers={
                "Content-Type": "application/json"
            },
            method="POST",
        )

        with urllib.request.urlopen(
            req,
            timeout=2,
        ):
            pass

        return True

    except Exception:
        return False


def emit_deny(
    op_id,
    binding,
    reason,
    auth_id=None,
    auth_nonce=None,
):
    package = make_boundary_package(
        op_id,
        binding,
        "DENY",
        auth_id,
        auth_nonce,
        reason,
    )

    sent = send_boundary(
        package
    )

    print(
        "{} DENY operation_id={} reason={} "
        "authorization_id={} sent={}".format(
            PROVIDER_ID,
            op_id,
            reason,
            auth_id,
            sent,
        ),
        flush=True,
    )


def decode_authorization(
    encoded,
):
    raw = b64url_decode(
        encoded
    )

    package = json.loads(
        raw.decode("utf-8")
    )

    if not isinstance(
        package,
        dict,
    ):
        raise ValueError(
            "authorization_package_not_object"
        )

    if (
        package.get("alg")
        != "Ed25519"
    ):
        raise ValueError(
            "authorization_wrong_algorithm"
        )

    auth = package.get(
        "authorization"
    )

    signature = package.get(
        "signature"
    )

    if (
        not isinstance(auth, dict)
        or not isinstance(
            signature,
            str,
        )
        or not signature
    ):
        raise ValueError(
            "authorization_envelope_invalid"
        )

    return package, auth, signature


def process_artifact(
    artifact,
):
    request_repr = artifact.get(
        "request_repr",
        "",
    )

    verification_context = artifact.get(
        "verification_context",
        "",
    )

    supplied_binding = artifact.get(
        "binding",
        "",
    )

    expected_binding = mechanical_binding(
        request_repr,
        verification_context,
    )

    op_id = operation_id(
        expected_binding
    )

    if supplied_binding != expected_binding:
        emit_deny(
            op_id,
            expected_binding,
            "binding_mismatch",
        )
        return

    encoded_auth = artifact.get(
        "provider_authorization_b64",
        "",
    )

    if (
        not isinstance(
            encoded_auth,
            str,
        )
        or not encoded_auth
    ):
        emit_deny(
            op_id,
            expected_binding,
            "auth_missing",
        )
        return

    try:
        _, auth, signature_text = (
            decode_authorization(
                encoded_auth
            )
        )
    except Exception:
        emit_deny(
            op_id,
            expected_binding,
            "auth_malformed",
        )
        return

    auth_id = auth.get(
        "authorization_id"
    )

    auth_nonce = auth.get(
        "nonce"
    )

    if (
        auth.get("provider_id")
        != PROVIDER_ID
    ):
        emit_deny(
            op_id,
            expected_binding,
            "auth_provider_mismatch",
            auth_id,
            auth_nonce,
        )
        return

    recomputed_auth_id = (
        expected_authorization_id(
            auth
        )
    )

    if (
        auth_id
        != recomputed_auth_id
    ):
        emit_deny(
            op_id,
            expected_binding,
            "auth_id_mismatch",
            auth_id,
            auth_nonce,
        )
        return

    try:
        ISSUANCE_PUBLIC_KEY.verify(
            b64url_decode(
                signature_text
            ),
            AUTH_SIG_TAG
            + canonical_bytes(auth),
        )

    except InvalidSignature:
        emit_deny(
            op_id,
            expected_binding,
            "auth_bad_sig",
            auth_id,
            auth_nonce,
        )
        return

    except Exception:
        emit_deny(
            op_id,
            expected_binding,
            "auth_bad_sig",
            auth_id,
            auth_nonce,
        )
        return

    if (
        auth.get("request_repr")
        != request_repr
    ):
        emit_deny(
            op_id,
            expected_binding,
            "auth_request_mismatch",
            auth_id,
            auth_nonce,
        )
        return

    if (
        auth.get(
            "verification_context"
        )
        != verification_context
    ):
        emit_deny(
            op_id,
            expected_binding,
            "auth_context_mismatch",
            auth_id,
            auth_nonce,
        )
        return

    consumed, reason = (
        consume_authorization(
            auth_id,
            auth_nonce,
            op_id,
        )
    )

    if not consumed:
        emit_deny(
            op_id,
            expected_binding,
            reason,
            auth_id,
            auth_nonce,
        )
        return

    start_package = (
        make_boundary_package(
            op_id,
            expected_binding,
            "START",
            auth_id,
            auth_nonce,
            None,
        )
    )

    start_sent = send_boundary(
        start_package
    )

    print(
        "{} START operation_id={} "
        "authorization_id={} sent={}".format(
            PROVIDER_ID,
            op_id,
            auth_id,
            start_sent,
        ),
        flush=True,
    )

    execution_record = append_execution(
        op_id,
        auth_id,
    )

    print(
        "{} EXECUTED operation_id={} "
        "authorization_id={} local_seq={}".format(
            PROVIDER_ID,
            op_id,
            auth_id,
            execution_record[
                "local_execution_seq"
            ],
        ),
        flush=True,
    )

    complete_package = (
        make_boundary_package(
            op_id,
            expected_binding,
            "COMPLETE",
            auth_id,
            auth_nonce,
            None,
        )
    )

    complete_sent = send_boundary(
        complete_package
    )

    print(
        "{} COMPLETE operation_id={} "
        "authorization_id={} sent={}".format(
            PROVIDER_ID,
            op_id,
            auth_id,
            complete_sent,
        ),
        flush=True,
    )


class ProviderHandler(
    BaseHTTPRequestHandler
):

    def log_message(
        self,
        fmt,
        *args,
    ):
        return

    def do_GET(self):
        if self.path != "/health":
            self.send_response(404)
            self.end_headers()
            return

        body = canonical_bytes(
            {
                "status": "ok",
                "provider_id": PROVIDER_ID,
                "boundary_key_id": (
                    BOUNDARY_KEY_ID
                ),
                "spent_count": len(
                    SPENT
                ),
            }
        )

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json",
        )
        self.send_header(
            "Content-Length",
            str(len(body)),
        )
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):

        if self.path != "/ingest":
            self.send_response(404)
            self.end_headers()
            return

        try:
            length = int(
                self.headers.get(
                    "Content-Length",
                    "0",
                )
            )
        except Exception:
            length = 0

        if (
            length < 0
            or length > MAX_REQUEST_BYTES
        ):
            self.send_response(204)
            self.end_headers()
            return

        body = (
            self.rfile.read(length)
            if length > 0
            else b""
        )

        try:
            artifact = json.loads(
                body.decode("utf-8")
            )

            if not isinstance(
                artifact,
                dict,
            ):
                raise ValueError(
                    "artifact_not_object"
                )

            process_artifact(
                artifact
            )

        except Exception as exc:
            print(
                "{} ARTIFACT_ERROR {}".format(
                    PROVIDER_ID,
                    type(exc).__name__,
                ),
                flush=True,
            )

        self.send_response(204)
        self.end_headers()


def main():
    global SPENT

    SPENT = load_spent_state()

    print("MP001_PROVIDER_A")
    print(
        "Listening on {}:{}".format(
            HOST,
            PORT,
        )
    )
    print(
        "Provider ID:",
        PROVIDER_ID,
    )
    print(
        "Boundary key ID:",
        BOUNDARY_KEY_ID,
    )
    print(
        "Spent state:",
        SPENT_STATE_PATH,
    )
    print(
        "Spent entries loaded:",
        len(SPENT),
    )
    print(
        "Execution log:",
        EXECUTION_LOG_PATH,
    )

    ThreadingHTTPServer(
        (HOST, PORT),
        ProviderHandler,
    ).serve_forever()


if __name__ == "__main__":
    main()
