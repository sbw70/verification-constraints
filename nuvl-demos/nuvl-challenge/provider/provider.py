# provider.py (challenge version)

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import hashlib
import hmac
import json
import time
import threading
import psutil
import os

# NOTE:
# Secret is intentionally NOT exposed elsewhere in the demo.
SECRET = b"provider-secret-key"

used_nonces = {}
nonce_lock = threading.Lock()
stats_lock = threading.Lock()

_start_time = time.time()
_process = psutil.Process(os.getpid())
_process.cpu_percent(interval=None)

_total_response_ms = 0.0
_stop_writer = threading.Event()

stats = {
    "total_attempts": 0,
    "initiated": 0,
    "denied": 0,
    "denied_breakdown": {
        "bad_json": 0,
        "missing_fields": 0,
        "malformed_token": 0,
        "bad_expiry": 0,
        "mismatch": 0,
        "expired": 0,
        "bad_signature": 0,
        "replay": 0,
    },
    "peak_cpu_pct": 0.0,
    "peak_ram_mb": 0.0,
    "avg_response_ms": 0.0,
    "requests_per_second": 0.0,
    "uptime_seconds": 0.0,
}

def update_system_stats_locked():
    global _total_response_ms

    try:
        cpu = _process.cpu_percent(interval=None)
        ram_mb = _process.memory_info().rss / (1024 * 1024)

        if cpu > stats["peak_cpu_pct"]:
            stats["peak_cpu_pct"] = round(cpu, 2)
        if ram_mb > stats["peak_ram_mb"]:
            stats["peak_ram_mb"] = round(ram_mb, 2)
    except:
        pass

    uptime = time.time() - _start_time
    stats["uptime_seconds"] = round(uptime, 1)

    if stats["total_attempts"] > 0:
        stats["avg_response_ms"] = round(_total_response_ms / stats["total_attempts"], 3)

    if uptime > 0:
        stats["requests_per_second"] = round(stats["total_attempts"] / uptime, 2)

def write_stats_snapshot():
    with stats_lock:
        update_system_stats_locked()
        snapshot = json.dumps(stats, indent=2)

    with open("stats.json", "w") as f:
        f.write(snapshot)

def stats_writer():
    while not _stop_writer.is_set():
        write_stats_snapshot()
        _stop_writer.wait(1.0)

def record_attempt(elapsed_ms, initiated=False, denial_reason=None):
    global _total_response_ms

    with stats_lock:
        stats["total_attempts"] += 1
        _total_response_ms += elapsed_ms

        if initiated:
            stats["initiated"] += 1
        else:
            stats["denied"] += 1
            if denial_reason in stats["denied_breakdown"]:
                stats["denied_breakdown"][denial_reason] += 1

def sign(r, c, n, e):
    # verification only
    msg = f"{r}|{c}|{n}|{e}".encode()
    return hmac.new(SECRET, msg, hashlib.sha256).hexdigest()

def decode_token(token):
    raw = base64.urlsafe_b64decode(token.encode())
    obj = json.loads(raw.decode())

    rr = obj["r"]
    cc = obj["c"]
    n = obj["n"]
    e = obj["e"]
    s = obj["s"]

    return rr, cc, n, e, s

class Provider(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def _finish(self, code, t0, initiated=False, reason=None):
        elapsed_ms = (time.time() - t0) * 1000.0
        record_attempt(elapsed_ms, initiated, reason)
        self.send_response(code)
        self.end_headers()

    def do_POST(self):
        t0 = time.time()

        if self.path != "/ingest":
            self._finish(404, t0, False, "missing_fields")
            return

        try:
            size = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(size)
            data = json.loads(raw)
        except:
            self._finish(400, t0, False, "bad_json")
            return

        r = data.get("request_repr")
        c = data.get("verification_context")
        token = data.get("provider_token")

        if not all(isinstance(x, str) and x for x in (r, c, token)):
            self._finish(403, t0, False, "missing_fields")
            return

        try:
            rr, cc, n, e, s = decode_token(token)
            exp = int(e)
        except:
            self._finish(403, t0, False, "malformed_token")
            return

        now = int(time.time())

        if rr != r or cc != c:
            self._finish(403, t0, False, "mismatch")
            return

        if now > exp:
            self._finish(403, t0, False, "expired")
            return

        if s != sign(rr, cc, n, e):
            self._finish(403, t0, False, "bad_signature")
            return

        with nonce_lock:
            if n in used_nonces:
                self._finish(403, t0, False, "replay")
                return
            used_nonces[n] = e

        self._finish(200, t0, True)

# background stats writer
threading.Thread(target=stats_writer, daemon=True).start()

print("Provider listening on 127.0.0.1:9090")

ThreadingHTTPServer(("127.0.0.1", 9090), Provider).serve_forever()
