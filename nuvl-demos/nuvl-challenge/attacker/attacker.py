import requests
import threading
import time
import random
import string
import json
import base64
import hashlib
import hmac
from collections import deque

NUVL = "http://127.0.0.1:8080/nuvl"
TIMEOUT = 3
token_pool = deque(maxlen=1000)
stats = {"sent": 0, "errors": 0, "pool": 0}
lock = threading.Lock()

def rand_str(n=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def rand_hex(n=64):
    return ''.join(random.choices('0123456789abcdef', k=n))

def rand_b64():
    return base64.urlsafe_b64encode(bytes(random.getrandbits(8) for _ in range(48))).decode().rstrip('=')

def rand_ctx():
    pool = [
        "CTX_ALPHA","CTX_BETA","CTX_GAMMA","CTX_PROD","CTX_DEV",
        "CTX_ADMIN","CTX_USER","CTX_1","CTX_0","CTX_A","CTX_B",
        "ALPHA","BETA","DEFAULT","ADMIN","ROOT","PROD","DEV","TEST",
        "ctx_alpha","ctx_beta","auth","verify","provider","user",
        rand_str(6), rand_str(10), rand_str(4),
    ]
    return random.choice(pool)

def rand_nonce():
    return random.randint(100000, 999999999)

def now():
    return int(time.time())

def rand_expiry(expired=False):
    return now() - random.randint(60, 7200) if expired else now() + random.randint(60, 7200)

def guess_sig(r, c, n, e):
    # smart attacker tries plausible signing approaches
    attempts = [
        lambda: hashlib.sha256(f"{r}|{c}|{n}|{e}".encode()).hexdigest(),
        lambda: hashlib.sha256(f"{c}|{r}|{n}|{e}".encode()).hexdigest(),
        lambda: hashlib.sha256(f"{r}{c}{n}{e}".encode()).hexdigest(),
        lambda: hashlib.md5(f"{r}|{c}|{n}|{e}".encode()).hexdigest(),
        lambda: hmac.new(c.encode(), f"{r}|{n}|{e}".encode(), hashlib.sha256).hexdigest(),
        lambda: hmac.new(b"secret", f"{r}|{c}|{n}|{e}".encode(), hashlib.sha256).hexdigest(),
        lambda: hmac.new(b"provider", f"{r}|{c}|{n}|{e}".encode(), hashlib.sha256).hexdigest(),
        lambda: hmac.new(b"nuvl", f"{r}|{c}|{n}|{e}".encode(), hashlib.sha256).hexdigest(),
        lambda: hmac.new(b"NUVL_BIND_V1", f"{r}|{c}|{n}|{e}".encode(), hashlib.sha256).hexdigest(),
        lambda: hmac.new(r.encode()[:32], f"{c}|{n}|{e}".encode(), hashlib.sha256).hexdigest(),
        lambda: rand_hex(64),
    ]
    return random.choice(attempts)()

def make_token(ctx, expired=False, missing=None, wrong_types=False, bad_r=False):
    r = rand_hex(64) if not bad_r else rand_str(64)
    c = ctx
    n = rand_nonce()
    e = rand_expiry(expired=expired)
    s = guess_sig(r, c, n, e)
    payload = {"r": r, "c": c, "n": n, "e": e, "s": s}
    if wrong_types:
        field = random.choice(["r", "c", "n", "e", "s"])
        payload[field] = random.choice([None, 0, [], {}, True, "", -1, 3.14])
    if missing:
        for f in missing:
            payload.pop(f, None)
    raw = json.dumps(payload).encode()
    return base64.urlsafe_b64encode(raw).decode()

def store(ctx, token):
    with lock:
        token_pool.append((ctx, token))
        stats["pool"] = len(token_pool)

def send(ctx, token, body):
    headers = {
        "Content-Type": "application/octet-stream",
        "X-Verification-Context": ctx,
        "X-Provider-Token": token,
    }
    try:
        requests.post(NUVL, data=body, headers=headers, timeout=TIMEOUT)
        with lock:
            stats["sent"] += 1
        store(ctx, token)
    except Exception:
        with lock:
            stats["errors"] += 1

def std_body():
    templates = [
        {"op": "transfer", "amount": random.randint(1, 9999), "to": "acct_" + rand_str(8)},
        {"op": "auth", "user": rand_str(8), "pass": rand_str(12)},
        {"op": "query", "id": rand_str(16)},
        {"action": "initiate", "token": rand_str(32)},
        {"cmd": "run", "args": [rand_str(4), rand_str(4)]},
    ]
    return json.dumps(random.choice(templates)).encode()

def attack_valid_shape():
    while True:
        ctx = rand_ctx()
        token = make_token(ctx)
        send(ctx, token, std_body())
        time.sleep(random.uniform(0.005, 0.02))

def attack_expired():
    while True:
        ctx = rand_ctx()
        token = make_token(ctx, expired=True)
        send(ctx, token, std_body())
        time.sleep(random.uniform(0.05, 0.15))

def attack_missing_fields():
    combos = [
        ["s"], ["r"], ["c"], ["n"], ["e"],
        ["r", "s"], ["c", "s"], ["n", "e"],
        ["r", "c", "n"], ["e", "s"], ["s", "n", "e"],
    ]
    while True:
        ctx = rand_ctx()
        token = make_token(ctx, missing=random.choice(combos))
        send(ctx, token, std_body())
        time.sleep(random.uniform(0.05, 0.15))

def attack_wrong_types():
    while True:
        ctx = rand_ctx()
        token = make_token(ctx, wrong_types=True)
        send(ctx, token, std_body())
        time.sleep(random.uniform(0.05, 0.15))

def attack_ctx_swap():
    while True:
        if token_pool:
            orig_ctx, token = random.choice(list(token_pool))
            new_ctx = rand_ctx()
            send(new_ctx, token, std_body())
        time.sleep(random.uniform(0.02, 0.08))

def attack_replay():
    while True:
        if token_pool:
            ctx, token = random.choice(list(token_pool))
            send(ctx, token, std_body())
        time.sleep(random.uniform(0.01, 0.05))

def attack_body_mutation():
    mutations = [
        b'{"op":"transfer","amount":}',
        b'{"op":null}',
        b'{}{}',
        b'null',
        b'[]',
        b'',
        b'\x00' * 64,
        b'{"op":"transfer","amount":100,"to":"acct_123"}' + b'\x00' * 10,
        b'true',
        b'<xml><op>transfer</op></xml>',
        b'op=transfer&amount=100&to=acct_123',
    ]
    while True:
        if token_pool:
            ctx, token = random.choice(list(token_pool))
            send(ctx, token, random.choice(mutations))
        time.sleep(random.uniform(0.02, 0.08))

def attack_malformed_base64():
    bad = [
        "!!!notbase64!!!",
        "eyJ==",
        "not.valid.base64",
        base64.urlsafe_b64encode(b"not json").decode(),
        base64.urlsafe_b64encode(b"{}").decode(),
        base64.urlsafe_b64encode(b"[]").decode(),
        base64.urlsafe_b64encode(b"null").decode(),
        rand_hex(32),
        rand_str(48),
        "",
        "Bearer " + rand_str(32),
        "." * 30,
        rand_b64(),
        base64.urlsafe_b64encode(json.dumps({"x": rand_str()}).encode()).decode(),
    ]
    while True:
        ctx = rand_ctx()
        token = random.choice(bad)
        send(ctx, token, std_body())
        time.sleep(random.uniform(0.05, 0.15))

def attack_oversized():
    while True:
        ctx = rand_ctx()
        token = make_token(ctx)
        size = random.choice([65537, 131072, 262144, 512000])
        body = ('X' * size).encode()
        send(ctx, token, body)
        time.sleep(random.uniform(1.0, 4.0))

def attack_burst():
    while True:
        ctx = rand_ctx()
        token = make_token(ctx)
        body = std_body()
        threads = []
        count = random.randint(15, 40)
        for _ in range(count):
            t = threading.Thread(target=send, args=(ctx, token, body), daemon=True)
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        time.sleep(random.uniform(3.0, 8.0))

def attack_sig_guessing():
    # dedicated thread trying every known signing pattern systematically
    patterns = [
        lambda r,c,n,e: hashlib.sha256(f"{r}|{c}|{n}|{e}".encode()).hexdigest(),
        lambda r,c,n,e: hashlib.sha256(f"{c}|{r}|{n}|{e}".encode()).hexdigest(),
        lambda r,c,n,e: hashlib.sha256(f"{r}|{c}|{e}|{n}".encode()).hexdigest(),
        lambda r,c,n,e: hashlib.sha256(f"{n}|{r}|{c}|{e}".encode()).hexdigest(),
        lambda r,c,n,e: hmac.new(b"secret", f"{r}|{c}|{n}|{e}".encode(), hashlib.sha256).hexdigest(),
        lambda r,c,n,e: hmac.new(b"provider", f"{r}|{c}|{n}|{e}".encode(), hashlib.sha256).hexdigest(),
        lambda r,c,n,e: hmac.new(b"nuvl", f"{r}|{c}|{n}|{e}".encode(), hashlib.sha256).hexdigest(),
        lambda r,c,n,e: hmac.new(b"NUVL_BIND_V1", f"{r}|{c}|{n}|{e}".encode(), hashlib.sha256).hexdigest(),
        lambda r,c,n,e: hmac.new(b"PROVIDER_ONLY_KEY_CHANGE_ME", f"{r}|{c}|{n}|{e}".encode(), hashlib.sha256).hexdigest(),
        lambda r,c,n,e: hmac.new(b"CHANGE_ME", f"{r}|{c}|{n}|{e}".encode(), hashlib.sha256).hexdigest(),
        lambda r,c,n,e: hmac.new(c.encode(), f"{r}|{n}|{e}".encode(), hashlib.sha256).hexdigest(),
        lambda r,c,n,e: hmac.new(r.encode()[:32], f"{c}|{n}|{e}".encode(), hashlib.sha256).hexdigest(),
        lambda r,c,n,e: hashlib.sha256((r+c+str(n)+str(e)).encode()).hexdigest(),
        lambda r,c,n,e: hashlib.sha256(json.dumps({"r":r,"c":c,"n":n,"e":e}).encode()).hexdigest(),
    ]
    while True:
        ctx = rand_ctx()
        r = rand_hex(64)
        n = rand_nonce()
        e = rand_expiry()
        for fn in patterns:
            s = fn(r, ctx, n, e)
            payload = {"r": r, "c": ctx, "n": n, "e": e, "s": s}
            token = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
            send(ctx, token, std_body())
            time.sleep(random.uniform(0.01, 0.03))

def status_printer():
    while True:
        time.sleep(5)
        with lock:
            s = stats["sent"]
            e = stats["errors"]
            p = stats["pool"]
        print(f"[{time.strftime('%H:%M:%S')}] sent={s} errors={e} pool={p}")

if __name__ == "__main__":
    print(f"[{time.strftime('%H:%M:%S')}] attacker started — target {NUVL}")
    print("Ctrl+C to stop\n")

    workers = [
        threading.Thread(target=attack_valid_shape, daemon=True),
        threading.Thread(target=attack_expired, daemon=True),
        threading.Thread(target=attack_missing_fields, daemon=True),
        threading.Thread(target=attack_wrong_types, daemon=True),
        threading.Thread(target=attack_ctx_swap, daemon=True),
        threading.Thread(target=attack_replay, daemon=True),
        threading.Thread(target=attack_body_mutation, daemon=True),
        threading.Thread(target=attack_malformed_base64, daemon=True),
        threading.Thread(target=attack_oversized, daemon=True),
        threading.Thread(target=attack_burst, daemon=True),
        threading.Thread(target=attack_sig_guessing, daemon=True),
        threading.Thread(target=status_printer, daemon=True),
    ]

    for w in workers:
        w.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nstopped.")
