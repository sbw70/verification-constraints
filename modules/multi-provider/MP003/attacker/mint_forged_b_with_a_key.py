#!/usr/bin/env python3

import argparse
import base64
import hashlib
import json
import os
import secrets
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


PROVIDER_ID = "PROVIDER_B"

AUTH_ID_TAG = b"NUVL-MP-AUTH-ID-v1|"
AUTH_SIG_TAG = b"NUVL-MP-AUTH-v1|"

BASE_DIR = Path(__file__).resolve().parent

ISSUANCE_PRIVATE_KEY_PATH = (
    BASE_DIR / "compromised_provider_a_issuance_private.pem"
)

ISSUANCE_PUBLIC_KEY_PATH = (
    BASE_DIR / "provider_a_issuance_public.pem"
)


def canonical_bytes(obj):
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def b64url_encode(raw):
    return base64.urlsafe_b64encode(
        raw
    ).rstrip(b"=").decode("ascii")


def load_keypair():
    private_key = (
        serialization.load_pem_private_key(
            ISSUANCE_PRIVATE_KEY_PATH.read_bytes(),
            password=None,
        )
    )

    public_key = (
        serialization.load_pem_public_key(
            ISSUANCE_PUBLIC_KEY_PATH.read_bytes()
        )
    )

    if not isinstance(
        private_key,
        Ed25519PrivateKey,
    ):
        raise RuntimeError(
            "issuance_private_not_ed25519"
        )

    if not isinstance(
        public_key,
        Ed25519PublicKey,
    ):
        raise RuntimeError(
            "issuance_public_not_ed25519"
        )

    private_raw_public = (
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    )

    public_raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )

    if private_raw_public != public_raw:
        raise RuntimeError(
            "issuance_keypair_mismatch"
        )

    return private_key


def write_exclusive(path, data):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(path, "xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--request-file",
        required=True,
    )

    parser.add_argument(
        "--context",
        required=True,
    )

    parser.add_argument(
        "--output",
        required=True,
        help=(
            "Output authorization package JSON. "
            "A sibling .b64 file is also written."
        ),
    )

    args = parser.parse_args()

    request_path = Path(
        args.request_file
    ).resolve()

    output_path = Path(
        args.output
    ).resolve()

    b64_path = output_path.with_suffix(
        output_path.suffix + ".b64"
    )

    if output_path.exists():
        raise RuntimeError(
            "output_exists"
        )

    if b64_path.exists():
        raise RuntimeError(
            "b64_output_exists"
        )

    request_bytes = (
        request_path.read_bytes()
    )

    request_repr = sha256_bytes(
        request_bytes
    )

    nonce = secrets.token_hex(16)

    core = {
        "version": 1,
        "provider_id": PROVIDER_ID,
        "request_repr": request_repr,
        "verification_context": (
            args.context
        ),
        "nonce": nonce,
    }

    authorization_id = sha256_bytes(
        AUTH_ID_TAG
        + canonical_bytes(core)
    )

    authorization = dict(core)

    authorization[
        "authorization_id"
    ] = authorization_id

    private_key = load_keypair()

    signature = private_key.sign(
        AUTH_SIG_TAG
        + canonical_bytes(
            authorization
        )
    )

    package = {
        "alg": "Ed25519",
        "authorization": authorization,
        "signature": b64url_encode(
            signature
        ),
    }

    package_bytes = canonical_bytes(
        package
    )

    header_value = b64url_encode(
        package_bytes
    ).encode("ascii")

    write_exclusive(
        output_path,
        package_bytes,
    )

    write_exclusive(
        b64_path,
        header_value,
    )

    print(
        "PROVIDER_ID={}".format(
            PROVIDER_ID
        )
    )

    print(
        "REQUEST_REPR={}".format(
            request_repr
        )
    )

    print(
        "AUTHORIZATION_ID={}".format(
            authorization_id
        )
    )

    print(
        "AUTHORIZATION_NONCE={}".format(
            nonce
        )
    )

    print(
        "PACKAGE_SHA256={}".format(
            sha256_bytes(
                package_bytes
            )
        )
    )

    print(
        "PACKAGE_FILE={}".format(
            output_path
        )
    )

    print(
        "HEADER_B64_FILE={}".format(
            b64_path
        )
    )


if __name__ == "__main__":
    main()