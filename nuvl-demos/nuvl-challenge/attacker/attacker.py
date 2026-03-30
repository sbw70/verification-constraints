import base64
import hashlib
import json
import random
import string
import threading
import time

import requests

NUVL = "https://challenge.xer0trust.com/nuvl"
TIMEOUT = 5

stats = {
    "sent": 0,
    "errors": 0,
}

lock = threading.Lock()


def rand_str(n=12):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def rand_hex(n=64):
    return "".join(random.choices("0123456789abcdef", k=n))


def rand_ctx():
    pool = [
        "ctx_demo",
        "ctx_alpha",
        "ctx_beta",
        "ctx_gamma",
        "ctx_prod",
        "ctx_dev",
        "ctx_user",
        "ctx_api",
        "ctx_edge",
        "ctx_" + rand_str(6),
    ]
    return random.choice(pool)


def now():
    return int(time.time())


def body_bytes():
    templates = [
        {"op": "transfer", "amount": random.randint(1, 9999), "to": "acct_" + rand_str(8)},
        {"op": "auth", "user": rand_str(8), "pass": rand_str(12)},
        {"op": "query", "id": rand_str(16)},
        {"action": "initiate", "token": rand_str(32)},
        {"cmd": "run", "args": [rand_str(4), rand_str(4)]},
    ]
    return json.dumps(random.choice(templates), separators=(",", ":")).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def wrong_sig():
    attempts = [
        rand_hex(64),
        hashlib.sha256(rand_str(32).encode()).hexdigest(),
        hashlib.md5(rand_str(32).encode()).hexdigest(),
        "0" * 64,
        "f" * 64,
    ]
    return random.choice(attempts)


def token_b64(obj) -> str:
    raw = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def send(headers, body):
    try:
        requests.post(NUVL, data=body, headers=headers, timeout=TIMEOUT)
        with lock:
            stats["sent"] += 1
    except Exception:
        with lock:
            stats["errors"] += 1


def send_with_token(ctx, token, body, include_ctx=True, include_token=True):
    headers = {
        "Content-Type": "application/json",
    }
    if include_ctx:
        headers["X-Verification-Context"] = ctx
    if include_token:
        headers["X-Provider-Token"] = token
    send(headers, body)


def attack_bad_signature():
    while True:
        body = body_bytes()
        ctx = rand_ctx()
        r = sha256_hex(body)
        n = rand_str(16)
        e = str(now() + random.randint(60, 600))

        token = token_b64({
            "r": r,
            "c": ctx,
            "n": n,
            "e": e,
            "s": wrong_sig(),
        })

        send_with_token(ctx, token, body)
        time.sleep(random.uniform(0.01, 0.03))


def attack_expired():
    while True:
        body = body_bytes()
        ctx = rand_ctx()
        r = sha256_hex(body)
        n = rand_str(16)
        e = str(now() - random.randint(60, 7200))

        token = token_b64({
            "r": r,
            "c": ctx,
            "n": n,
            "e": e,
            "s": wrong_sig(),
        })

        send_with_token(ctx, token, body)
        time.sleep(random.uniform(0.04, 0.12))


def attack_bad_expiry():
    while True:
        body = body_bytes()
        ctx = rand_ctx()
        r = sha256_hex(body)
        n = rand_str(16)
        e = random.choice(["soon", "never", "3.14", "NaN", "abc123"])

        token = token_b64({
            "r": r,
            "c": ctx,
            "n": n,
            "e": e,
            "s": wrong_sig(),
        })

        send_with_token(ctx, token, body)
        time.sleep(random.uniform(0.04, 0.12))


def attack_mismatch():
    while True:
        body = body_bytes()
        ctx = rand_ctx()

        bad_r = rand_hex(64)
        while bad_r == sha256_hex(body):
            bad_r = rand_hex(64)

        n = rand_str(16)
        e = str(now() + random.randint(60, 600))

        token = token_b64({
            "r": bad_r,
            "c": ctx,
            "n": n,
            "e": e,
            "s": wrong_sig(),
        })

        send_with_token(ctx, token, body)
        time.sleep(random.uniform(0.04, 0.12))


def attack_missing_fields():
    while True:
        body = body_bytes()
        ctx = rand_ctx()

        mode = random.choice(["missing_ctx", "missing_token", "both"])
        if mode == "missing_ctx":
            send_with_token(ctx, "x", body, include_ctx=False, include_token=True)
        elif mode == "missing_token":
            send_with_token(ctx, "x", body, include_ctx=True, include_token=False)
        else:
            send_with_token(ctx, "x", body, include_ctx=False, include_token=False)

        time.sleep(random.uniform(0.05, 0.15))


def attack_malformed():
    bad_tokens = [
        "!!!notbase64!!!",
        "eyJ9",
        "not.valid.base64",
        base64.urlsafe_b64encode(b"{}").decode("utf-8"),
        base64.urlsafe_b64encode(b"[]").decode("utf-8"),
        base64.urlsafe_b64encode(b"null").decode("utf-8"),
        rand_hex(32),
        rand_str(48),
        "",
        "." * 30,
    ]

    while True:
        body = body_bytes()
        ctx = rand_ctx()
        token = random.choice(bad_tokens)
        send_with_token(ctx, token, body)
        time.sleep(random.uniform(0.05, 0.15))


def status_printer():
    while True:
        time.sleep(5)
        with lock:
            s = stats["sent"]
            e = stats["errors"]
        print(f"[{time.strftime('%H:%M:%S')}] sent={s} errors={e}")


if __name__ == "__main__":
    print(f"[{time.strftime('%H:%M:%S')}] attacker started — target {NUVL}")
    print("Ctrl+C to stop\n")

    workers = [
        threading.Thread(target=attack_bad_signature, daemon=True),
        threading.Thread(target=attack_expired, daemon=True),
        threading.Thread(target=attack_bad_expiry, daemon=True),
        threading.Thread(target=attack_mismatch, daemon=True),
        threading.Thread(target=attack_missing_fields, daemon=True),
        threading.Thread(target=attack_malformed, daemon=True),
        threading.Thread(target=status_printer, daemon=True),
    ]

    for w in workers:
        w.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nstopped.")
