#!/usr/bin/env python3

import argparse
import base64
import hashlib
import json
import os
import socket
import threading
import time

from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


SCHEMA_VERSION = 1
HOST = "0.0.0.0"
PORT = 9191

GENESIS_HASH = "0" * 64

LOG_LOCK = threading.RLock()
RECORD_SEQ = 0
RECV_SEQ = 0
PREV_RECORD_HASH = GENESIS_HASH

LOG_PATH = None
REGISTRY = {}
REGISTRY_SHA256 = None
MANIFEST_SHA256 = None
CONTRACT_SHA256 = None
RECORDER_SHA256 = None
SESSION_ID = None

SEEN_SIGNED_EVENTS = {}


def canonical_bytes(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            block = f.read(65536)
            if not block:
                break
            h.update(block)

    return h.hexdigest()


def utc_now():
    return datetime.now(
        timezone.utc
    ).isoformat(timespec="microseconds")


def b64url_decode(text):
    raw = text.encode("ascii")
    raw += b"=" * ((4 - len(raw) % 4) % 4)
    return base64.urlsafe_b64decode(raw)


def next_recv_seq():
    global RECV_SEQ

    RECV_SEQ += 1
    return RECV_SEQ


def append_record(record):
    global RECORD_SEQ
    global PREV_RECORD_HASH

    with LOG_LOCK:
        RECORD_SEQ += 1

        entry = dict(record)

        entry["schema_version"] = SCHEMA_VERSION
        entry["record_seq"] = RECORD_SEQ
        entry["prev_record_hash"] = PREV_RECORD_HASH

        record_hash = sha256_bytes(
            canonical_bytes(entry)
        )

        entry["record_hash"] = record_hash

        line = canonical_bytes(entry) + b"\n"

        with open(LOG_PATH, "ab") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())

        PREV_RECORD_HASH = record_hash

        return entry


def public_key_id(public_key):
    raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    return "sha256:" + sha256_bytes(raw)


def load_registry(path):
    registry_path = Path(path).resolve()

    raw = registry_path.read_bytes()
    document = json.loads(raw.decode("utf-8"))

    if not isinstance(document, dict):
        raise ValueError("registry_not_object")

    providers = document.get("providers")

    if not isinstance(providers, dict):
        raise ValueError("registry_missing_providers")

    loaded = {}

    for provider_id, item in providers.items():

        if not isinstance(provider_id, str) or not provider_id:
            raise ValueError("invalid_provider_id")

        if not isinstance(item, dict):
            raise ValueError(
                "invalid_registry_entry_" + provider_id
            )

        expected_key_id = item.get("key_id")
        public_key_file = item.get("public_key_file")

        if not isinstance(expected_key_id, str):
            raise ValueError(
                "missing_key_id_" + provider_id
            )

        if not isinstance(public_key_file, str):
            raise ValueError(
                "missing_public_key_file_" + provider_id
            )

        public_key_path = (
            registry_path.parent
            / public_key_file
        ).resolve()

        public_key = serialization.load_pem_public_key(
            public_key_path.read_bytes()
        )

        if not isinstance(
            public_key,
            Ed25519PublicKey,
        ):
            raise ValueError(
                "non_ed25519_key_" + provider_id
            )

        actual_key_id = public_key_id(
            public_key
        )

        if actual_key_id != expected_key_id:
            raise ValueError(
                "key_id_mismatch_" + provider_id
            )

        loaded[provider_id] = {
            "key_id": actual_key_id,
            "public_key": public_key,
            "public_key_path": str(
                public_key_path
            ),
        }

    return loaded, sha256_bytes(raw)


def extract_unknown_fields(payload, event):
    known_top = {
        "alg",
        "event",
        "signature",
    }

    known_event = {
        "version",
        "operation_id",
        "binding",
        "provider_id",
        "key_id",
        "stage",
        "boundary_value",
        "authorization_id",
        "authorization_nonce",
        "reason_code",
    }

    top_extra = {}

    if isinstance(payload, dict):
        top_extra = {
            key: value
            for key, value in payload.items()
            if key not in known_top
        }

    event_extra = {}

    if isinstance(event, dict):
        event_extra = {
            key: value
            for key, value in event.items()
            if key not in known_event
        }

    return {
        "top_level": top_extra,
        "event": event_extra,
    }


def inspect_submission(raw):
    result = {
        "claimed_provider_id": None,
        "claimed_operation_id": None,
        "claimed_stage": None,
        "claimed_key_id": None,
        "claimed_binding": None,
        "claimed_boundary_value": None,
        "claimed_authorization_id": None,
        "claimed_authorization_nonce": None,
        "claimed_reason_code": None,
        "registry_match": None,
        "sig_valid": None,
        "verification_code": None,
        "signed_event_sha256": None,
        "duplicate_of_seq": None,
        "unknown_fields": {
            "top_level": {},
            "event": {},
        },
    }

    try:
        payload = json.loads(
            raw.decode("utf-8")
        )
    except Exception:
        result["verification_code"] = (
            "malformed_json"
        )
        return result

    if not isinstance(payload, dict):
        result["verification_code"] = (
            "malformed_envelope"
        )
        return result

    event = payload.get("event")

    if isinstance(event, dict):
        result["claimed_provider_id"] = (
            event.get("provider_id")
        )
        result["claimed_operation_id"] = (
            event.get("operation_id")
        )
        result["claimed_stage"] = (
            event.get("stage")
        )
        result["claimed_key_id"] = (
            event.get("key_id")
        )
        result["claimed_binding"] = (
            event.get("binding")
        )
        result["claimed_boundary_value"] = (
            event.get("boundary_value")
        )
        result["claimed_authorization_id"] = (
            event.get("authorization_id")
        )
        result["claimed_authorization_nonce"] = (
            event.get("authorization_nonce")
        )
        result["claimed_reason_code"] = (
            event.get("reason_code")
        )

    result["unknown_fields"] = (
        extract_unknown_fields(
            payload,
            event,
        )
    )

    alg = payload.get("alg")
    signature_text = payload.get("signature")

    if not isinstance(event, dict):
        result["verification_code"] = (
            "malformed_envelope"
        )
        return result

    if (
        not isinstance(signature_text, str)
        or not signature_text
    ):
        result["verification_code"] = (
            "malformed_envelope"
        )
        return result

    if alg != "Ed25519":
        result["sig_valid"] = False
        result["verification_code"] = (
            "wrong_algorithm"
        )
        return result

    provider_id = result[
        "claimed_provider_id"
    ]

    key_id = result[
        "claimed_key_id"
    ]

    if (
        not isinstance(provider_id, str)
        or not provider_id
    ):
        result["verification_code"] = (
            "malformed_envelope"
        )
        return result

    registry_entry = REGISTRY.get(
        provider_id
    )

    if registry_entry is None:
        result["registry_match"] = False
        result["sig_valid"] = False
        result["verification_code"] = (
            "unknown_provider"
        )
        return result

    if (
        not isinstance(key_id, str)
        or key_id
        != registry_entry["key_id"]
    ):
        result["registry_match"] = False
        result["sig_valid"] = False
        result["verification_code"] = (
            "provider_key_mismatch"
        )
        return result

    result["registry_match"] = True

    try:
        signature = b64url_decode(
            signature_text
        )

        registry_entry["public_key"].verify(
            signature,
            b"NUVL-MP-BOUNDARY-v1|"
            + canonical_bytes(event),
        )

    except InvalidSignature:
        result["sig_valid"] = False
        result["verification_code"] = (
            "bad_sig"
        )
        return result

    except Exception as exc:
        result["sig_valid"] = False
        result["verification_code"] = (
            "verification_error:"
            + type(exc).__name__
        )
        return result

    result["sig_valid"] = True
    result["verification_code"] = "ok"

    signed_event_sha256 = sha256_bytes(
        canonical_bytes(
            {
                "event": event,
                "signature": signature_text,
            }
        )
    )

    result["signed_event_sha256"] = (
        signed_event_sha256
    )

    first_seq = SEEN_SIGNED_EVENTS.get(
        signed_event_sha256
    )

    if first_seq is not None:
        result["duplicate_of_seq"] = (
            first_seq
        )

    return result


class AssociationHandler(
    BaseHTTPRequestHandler
):

    def log_message(self, fmt, *args):
        return

    def do_GET(self):

        if self.path != "/health":
            self.send_response(404)
            self.end_headers()
            return

        body = canonical_bytes(
            {
                "status": "ok",
                "role": "evidence_recorder",
                "schema_version": (
                    SCHEMA_VERSION
                ),
                "session_id": SESSION_ID,
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

        if self.path != "/boundary":
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

        if length < 0:
            length = 0

        raw = self.rfile.read(length)

        with LOG_LOCK:
            recv_seq = next_recv_seq()

            recv_utc = utc_now()
            recv_monotonic_ns = (
                time.monotonic_ns()
            )

            inspected = inspect_submission(
                raw
            )

            record = {
                "record_type": "SUBMISSION",
                "session_id": SESSION_ID,
                "recv_seq": recv_seq,
                "recv_utc": recv_utc,
                "recv_monotonic_ns": (
                    recv_monotonic_ns
                ),
                "source_addr": (
                    self.client_address[0]
                ),
                "source_port": (
                    self.client_address[1]
                ),
                "raw_sha256": (
                    sha256_bytes(raw)
                ),
                "raw_body_b64": (
                    base64.b64encode(
                        raw
                    ).decode("ascii")
                ),
            }

            record.update(inspected)

            appended = append_record(
                record
            )

            signed_hash = appended.get(
                "signed_event_sha256"
            )

            if (
                appended.get("sig_valid")
                is True
                and signed_hash
                and appended.get(
                    "duplicate_of_seq"
                )
                is None
            ):
                SEEN_SIGNED_EVENTS[
                    signed_hash
                ] = recv_seq

        print(
            "OBSERVED "
            "seq={} "
            "provider={} "
            "stage={} "
            "sig_valid={} "
            "code={} "
            "duplicate_of={}".format(
                recv_seq,
                appended.get(
                    "claimed_provider_id"
                ),
                appended.get(
                    "claimed_stage"
                ),
                appended.get(
                    "sig_valid"
                ),
                appended.get(
                    "verification_code"
                ),
                appended.get(
                    "duplicate_of_seq"
                ),
            ),
            flush=True,
        )

        self.send_response(204)
        self.end_headers()


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--session-id",
        required=True,
    )

    parser.add_argument(
        "--registry",
        required=True,
    )

    parser.add_argument(
        "--manifest",
        required=True,
    )

    parser.add_argument(
        "--contract",
        required=True,
    )

    parser.add_argument(
        "--log",
        required=True,
    )

    return parser.parse_args()


def main():
    global LOG_PATH
    global REGISTRY
    global REGISTRY_SHA256
    global MANIFEST_SHA256
    global CONTRACT_SHA256
    global RECORDER_SHA256
    global SESSION_ID

    args = parse_args()

    SESSION_ID = args.session_id

    LOG_PATH = Path(
        args.log
    ).resolve()

    registry_path = Path(
        args.registry
    ).resolve()

    manifest_path = Path(
        args.manifest
    ).resolve()

    contract_path = Path(
        args.contract
    ).resolve()

    recorder_path = Path(
        __file__
    ).resolve()

    if LOG_PATH.exists():
        raise SystemExit(
            "REFUSING TO OVERWRITE EXISTING LOG: "
            + str(LOG_PATH)
        )

    LOG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    REGISTRY, REGISTRY_SHA256 = (
        load_registry(
            registry_path
        )
    )

    MANIFEST_SHA256 = sha256_file(
        manifest_path
    )

    CONTRACT_SHA256 = sha256_file(
        contract_path
    )

    RECORDER_SHA256 = sha256_file(
        recorder_path
    )

    append_record(
        {
            "record_type": (
                "SESSION_START"
            ),
            "session_id": SESSION_ID,
            "recv_utc": utc_now(),
            "recv_monotonic_ns": (
                time.monotonic_ns()
            ),
            "host": socket.gethostname(),
            "recorder_sha256": (
                RECORDER_SHA256
            ),
            "registry_sha256": (
                REGISTRY_SHA256
            ),
            "manifest_sha256": (
                MANIFEST_SHA256
            ),
            "contract_sha256": (
                CONTRACT_SHA256
            ),
            "registered_providers": (
                sorted(REGISTRY.keys())
            ),
        }
    )

    print(
        "MP001_ASSOCIATION_RECORDER"
    )
    print(
        "Session:",
        SESSION_ID,
    )
    print(
        "Listening on {}:{}".format(
            HOST,
            PORT,
        )
    )
    print(
        "Recorder SHA256:",
        RECORDER_SHA256,
    )
    print(
        "Registry SHA256:",
        REGISTRY_SHA256,
    )
    print(
        "Manifest SHA256:",
        MANIFEST_SHA256,
    )
    print(
        "Contract SHA256:",
        CONTRACT_SHA256,
    )
    print(
        "Registered providers:",
        ", ".join(
            sorted(REGISTRY.keys())
        ),
    )

    server = ThreadingHTTPServer(
        (HOST, PORT),
        AssociationHandler,
    )

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        pass

    finally:
        append_record(
            {
                "record_type": (
                    "SESSION_END"
                ),
                "session_id": (
                    SESSION_ID
                ),
                "recv_utc": utc_now(),
                "recv_monotonic_ns": (
                    time.monotonic_ns()
                ),
                "submission_count": (
                    RECV_SEQ
                ),
            }
        )

        server.server_close()

        print(
            "FINAL_RECORD_HASH:",
            PREV_RECORD_HASH,
        )


if __name__ == "__main__":
    main()



