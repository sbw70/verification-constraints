from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import hashlib
import hmac
import json
import time
import threading
import psutil
import os
from datetime import datetime, timezone

_secret_str = os.environ.get("PROVIDER_SECRET")
if not _secret_str:
    raise RuntimeError("PROVIDER_SECRET env var not set")
SECRET = _secret_str.encode()

used_nonces = {}
nonce_lock = threading.Lock()
stats_lock = threading.Lock()

_start_time = time.time()
_run_started_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

_process = psutil.Process(os.getpid())
_process.cpu_percent(interval=None)

_total_response_ms = 0.0
_stop_writer = threading.Event()

LOOPBACK_ONLY = {"127.0.0.1", "::1"}

stats = {
    "run_started": _run_started_iso,
    "last_updated": "",
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
        "non_local_source": 0,
    },
    "avg_response_ms": 0.0,
    "requests_per_second": 0.0,
    "uptime_seconds": 0.0,
    "peak_cpu_pct": 0.0,
    "peak_ram_mb": 0.0,
}

def now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def update_system_stats_locked():
    global _total_response_ms

    try:
        cpu = _process.cpu_percent(interval=None)
        ram_mb = _process.memory_info().rss / (1024 * 1024)

        if cpu > stats["peak_cpu_pct"]:
            stats["peak_cpu_pct"] = round(cpu, 2)
        if ram_mb > stats["peak_ram_mb"]:
            stats["peak_ram_mb"] = round(ram_mb, 2)
    except Exception:
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
        stats["last_updated"] = now_iso()
        snapshot = json.dumps(stats, indent=2)

    with open("stats.json", "w", encoding="utf-8") as f:
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
            else:
                stats["denied_breakdown"]["bad_json"] += 1

def sign(r, c, n, e):
    msg = f"{r}|{c}|{n}|{e}".encode()
    return hmac.new(SECRET, msg, hashlib.sha256).hexdigest()

def make_token(r, c, n, e):
    s = sign(r, c, n, e)
    payload = json.dumps({"r": r, "c": c, "n": n, "e": e, "s": s}).encode()
    return base64.urlsafe_b64encode(payload).decode()

def decode_token(token):
    raw = base64.urlsafe_b64decode(token.encode())
    obj = json.loads(raw.decode())

    rr = obj["r"]
    cc = obj["c"]
    n = obj["n"]
    e = obj["e"]
    s = obj["s"]

    if not all(isinstance(x, str) for x in (rr, cc, n, e, s)):
        raise ValueError("bad token fields")

    return rr, cc, n, e, s

class Provider(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _finish_request(self, status_code, t0, initiated=False, denial_reason=None):
        elapsed_ms = (time.time() - t0) * 1000.0
        record_attempt(elapsed_ms, initiated=initiated, denial_reason=denial_reason)
        self.send_response(status_code)
        self.end_headers()

    def _reject_non_local(self, t0):
        source_ip = self.client_address[0]
        if source_ip not in LOOPBACK_ONLY:
            self._finish_request(403, t0, initiated=False, denial_reason="non_local_source")
            return True
        return False

    def do_POST(self):
        t0 = time.time()

        if self._reject_non_local(t0):
            return

        if self.path == "/sign":
            size = int(self.headers.get("Content-Length", 0))
            try:
                data = json.loads(self.rfile.read(size))
                r = data["request_repr"]
                c = data["context"]
                n = data["nonce"]
                e = data["expiry"]
                if not all(isinstance(x, str) and x for x in (r, c, n, e)):
                    raise ValueError("bad fields")
                int(e)
            except Exception:
                self.send_response(400)
                self.end_headers()
                return
            token = make_token(r, c, n, e)
            body = json.dumps({"token": token}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path != "/ingest":
            self._finish_request(404, t0, initiated=False, denial_reason="missing_fields")
            return

        size = int(self.headers.get("Content-Length", 0))

        try:
            raw = self.rfile.read(size)
            data = json.loads(raw)
        except Exception:
            self._finish_request(400, t0, initiated=False, denial_reason="bad_json")
            return

        r = data.get("request_repr")
        c = data.get("verification_context")
        token = data.get("provider_token")

        if not all(isinstance(x, str) and x for x in (r, c, token)):
            self._finish_request(403, t0, initiated=False, denial_reason="missing_fields")
            return

        try:
            rr, cc, n, e, s = decode_token(token)
        except Exception:
            self._finish_request(403, t0, initiated=False, denial_reason="malformed_token")
            return

        try:
            exp = int(e)
        except Exception:
            self._finish_request(403, t0, initiated=False, denial_reason="bad_expiry")
            return

        now = int(time.time())

        if rr != r or cc != c:
            self._finish_request(403, t0, initiated=False, denial_reason="mismatch")
            return

        if now > exp:
            self._finish_request(403, t0, initiated=False, denial_reason="expired")
            return

        if s != sign(rr, cc, n, e):
            self._finish_request(403, t0, initiated=False, denial_reason="bad_signature")
            return

        with nonce_lock:
            expired_nonces = [k for k, v in used_nonces.items() if int(v) <= now]
            for k in expired_nonces:
                del used_nonces[k]

            if n in used_nonces:
                self._finish_request(403, t0, initiated=False, denial_reason="replay")
                return

            used_nonces[n] = e

        print(f"INITIATED r={r[:16]}... ctx={c}")
        self._finish_request(200, t0, initiated=True)

writer_thread = threading.Thread(target=stats_writer, daemon=True)
writer_thread.start()

print("Provider listening on 127.0.0.1:9090")
write_stats_snapshot()

try:
    ThreadingHTTPServer(("127.0.0.1", 9090), Provider).serve_forever()
finally:
    _stop_writer.set()
    write_stats_snapshot()
