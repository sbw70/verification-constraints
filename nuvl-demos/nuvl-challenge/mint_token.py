#!/usr/bin/env python3
"""
Mint a provider-side test token for the local NUVL challenge harness.

This script mirrors the provider token format used by provider.py:

    token = base64url(json({
        "r": request_repr,
        "c": verification_context,
        "n": nonce,
        "e": expiry,
        "s": hmac_sha256(secret, f"{r}|{c}|{n}|{e}")
    }))

This is provider-side issuance logic for local validation and check-your-work
testing. The client does not mint, sign, hash, or create nonce material.
"""

import argparse
import base64
import hashlib
import hmac
import json
import secrets
import sys
import time
from pathlib import Path


DEFAULT_SECRET = "FIGURE IT OUT"
DEFAULT_CONTEXT = "ctx_demo"

# Must match the BODY used by client.py so the flag-free path works.
DEFAULT_BODY = b'{"op":"initiate","target":"gate","mode":"standard"}'


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sign(secret: bytes, request_repr: str, context: str, nonce: str, expiry: str) -> str:
    msg = f"{request_repr}|{context}|{nonce}|{expiry}".encode("utf-8")
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()


def encode_token(obj: dict) -> str:
    raw = json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def read_body(args: argparse.Namespace) -> bytes:
    if args.body is not None:
        return args.body.encode("utf-8")

    if args.body_file is not None:
        return Path(args.body_file).read_bytes()

    if not sys.stdin.isatty():
        incoming = sys.stdin.buffer.read()
        if incoming:
            return incoming

    return DEFAULT_BODY


def build_payload(args: argparse.Namespace) -> dict:
    body = read_body(args)

    request_repr = args.request_repr
    if request_repr is None:
        request_repr = sha256_hex(body)

    context = args.context
    nonce = args.nonce or secrets.token_hex(16)
    expiry = str(int(time.time()) + args.ttl)

    signature = sign(
        secret=args.secret.encode("utf-8"),
        request_repr=request_repr,
        context=context,
        nonce=nonce,
        expiry=expiry,
    )

    token_obj = {
        "r": request_repr,
        "c": context,
        "n": nonce,
        "e": expiry,
        "s": signature,
    }

    provider_token = encode_token(token_obj)

    return {
        "request_repr": request_repr,
        "verification_context": context,
        "provider_token": provider_token,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mint a provider-side test token for the local NUVL challenge harness."
    )

    parser.add_argument(
        "--secret",
        default=DEFAULT_SECRET,
        help="provider signing secret for local testing",
    )

    parser.add_argument(
        "--context",
        default=DEFAULT_CONTEXT,
        help="verification context; provider expects values beginning with ctx_",
    )

    parser.add_argument(
        "--ttl",
        type=int,
        default=60,
        help="token lifetime in seconds",
    )

    parser.add_argument(
        "--nonce",
        default=None,
        help="nonce value; generated automatically if omitted",
    )

    parser.add_argument(
        "--body",
        default=None,
        help="request body to hash into request_repr",
    )

    parser.add_argument(
        "--body-file",
        default=None,
        help="file containing request body bytes to hash into request_repr",
    )

    parser.add_argument(
        "--request-repr",
        default=None,
        help="explicit request_repr value; skips hashing body input",
    )

    parser.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output",
    )

    parser.add_argument(
        "--out",
        default=None,
        help="write token payload to this file instead of stdout",
    )

    args = parser.parse_args()

    if not args.context.startswith("ctx_"):
        print("error: context must start with ctx_", file=sys.stderr)
        return 2

    if args.ttl <= 0:
        print("error: ttl must be positive", file=sys.stderr)
        return 2

    if args.body is not None and args.body_file is not None:
        print("error: use --body or --body-file, not both", file=sys.stderr)
        return 2

    payload = build_payload(args)

    if args.pretty:
        output = json.dumps(payload, indent=2)
    else:
        output = json.dumps(payload, separators=(",", ":"))

    if args.out:
        Path(args.out).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
