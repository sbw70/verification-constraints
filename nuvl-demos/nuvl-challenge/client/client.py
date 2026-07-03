#!/usr/bin/env python3
import argparse
import json
import os
import time
from pathlib import Path

import requests

NUVL = "http://127.0.0.1:8080/"
TIMEOUT = 5

BODY = b'{"op":"initiate","target":"gate","mode":"standard"}'

# Must match the context inside the provider-issued token.
# mint_token.py defaults to ctx_demo, so the naive path works flag-free.
VERIFICATION_CONTEXT = "ctx_demo"

INTERVAL_SECONDS = 60


def load_provider_token(token_file: str | None, token_value: str | None) -> str:
    """
    Load a provider-issued token.

    Accepted formats:
      1. raw token string
      2. JSON object from mint_token.py containing "provider_token"

    This client does not mint, sign, hash, or create nonce material.
    """

    if token_value:
        return token_value.strip()

    if not token_file:
        raise RuntimeError("missing provider token: use --token or --token-file")

    raw = Path(token_file).read_text(encoding="utf-8").strip()

    try:
        obj = json.loads(raw)
        token = obj.get("provider_token")
        if isinstance(token, str) and token:
            return token
    except Exception:
        pass

    if not raw:
        raise RuntimeError(f"empty provider token file: {token_file}")

    return raw


def send_once(token_file: str | None, token_value: str | None) -> bool:
    try:
        provider_token = load_provider_token(token_file, token_value)
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] error={e}")
        return False

    headers = {
        "Content-Type": "application/octet-stream",
        "X-Verification-Context": VERIFICATION_CONTEXT,
        "X-Provider-Token": provider_token,
    }

    try:
        r = requests.post(NUVL, data=BODY, headers=headers, timeout=TIMEOUT)
        print(f"[{time.strftime('%H:%M:%S')}] status={r.status_code}")
        return True
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] error={e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Send a request to local NUVL using a provider-issued token."
    )

    parser.add_argument(
        "--token",
        default=os.environ.get("PROVIDER_TOKEN"),
        help="provider-issued token; useful for one request",
    )

    parser.add_argument(
        "--token-file",
        default=os.environ.get("PROVIDER_TOKEN_FILE"),
        help="file containing either a raw token or mint_token.py JSON output",
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="send one request and exit",
    )

    args = parser.parse_args()

    print(f"[{time.strftime('%H:%M:%S')}] client started — target {NUVL}")
    print(f"context={VERIFICATION_CONTEXT}")

    if args.once:
        return 0 if send_once(args.token_file, args.token) else 2

    if args.token and not args.token_file:
        print(
            "warning: static --token/PROVIDER_TOKEN will be replayed if looped; "
            "provider should issue a fresh token per request"
        )

    print(f"sending 1 request every {INTERVAL_SECONDS} seconds")
    print("token file is re-read before every request\n")

    try:
        while True:
            send_once(args.token_file, args.token)
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nstopped.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
