#!/usr/bin/env python3
import requests
import time

NUVL = "http://127.0.0.1:8080/"
TIMEOUT = 5

# Sample request body
BODY = b'{"op":"initiate","target":"gate","mode":"standard"}'

# Token must be supplied externally
PROVIDER_TOKEN = "PASTE_PROVIDER_TOKEN_HERE"

# Verification context used by provider
VERIFICATION_CONTEXT = "CTX_ALPHA"

INTERVAL_SECONDS = 60


def send_once():
    headers = {
        "Content-Type": "application/octet-stream",
        "X-Verification-Context": VERIFICATION_CONTEXT,
        "X-Provider-Token": PROVIDER_TOKEN,
    }

    try:
        r = requests.post(NUVL, data=BODY, headers=headers, timeout=TIMEOUT)
        print(f"[{time.strftime('%H:%M:%S')}] status={r.status_code}")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] error={e}")


if __name__ == "__main__":
    print(f"[{time.strftime('%H:%M:%S')}] client started — target {NUVL}")
    print(f"sending 1 request every {INTERVAL_SECONDS} seconds\n")

    try:
        while True:
            send_once()
            time.sleep(INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nstopped.")
