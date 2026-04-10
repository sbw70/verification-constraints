from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import hashlib
import hmac
import json
import os
import psutil
import threading
import time
import collections

SECRET = b"FIGURE IT OUT"

used_nonces = {}
nonce_lock = threading.Lock()
stats_lock = threading.Lock()

_start_time = time.time()
_process = psutil.Process(os.getpid())
_process.cpu_percent(interval=None)

_request_timestamps = collections.deque()
_rps_lock = threading.Lock()

_history = collections.deque(maxlen=300)
_history_lock = threading.Lock()

_response_times = []
_response_lock = threading.Lock()

SAVE_INTERVAL = 60.0
_last_save = 0.0

stats = {
    "run_started": time.strftime("%Y-%m-%dT%H:%M:%S.000000Z", time.gmtime(_start_time)),
    "last_updated": "",
    "nuvl_status": "up",
    "provider_status": "up",
    "uptime_seconds": 0.0,
    "total_attempts": 0,
    "initiated": 0,
    "denied": 0,
    "timed_out": 0,
    "internal_errors": 0,
    "initiation_rate_pct": 0.0,
    "denial_rate_pct": 0.0,
    "timeout_rate_pct": 0.0,
    "current_rps": 0.0,
    "peak_rps": 0.0,
    "avg_response_ms": 0.0,
    "cpu_current_pct": 0.0,
    "cpu_peak_pct": 0.0,
    "ram_current_mb": 0.0,
    "ram_peak_mb": 0.0,
    "control_sent": 0,
    "control_completed": 0,
    "control_timed_out": 0,
    "control_success_pct": 0.0,
    "denied_breakdown": {
        "malformed": 0,
        "missing_fields": 0,
        "bad_expiry": 0,
        "expired": 0,
        "mismatch": 0,
        "replay": 0,
        "bad_signature": 0,
        "bad_context": 0,
    },
}


def register_attempt_timestamp():
    with _rps_lock:
        _request_timestamps.append(time.time())


def compute_rps():
    now = time.time()
    with _rps_lock:
        cutoff = now - 10.0
        while _request_timestamps and _request_timestamps[0] < cutoff:
            _request_timestamps.popleft()
        rps = len(_request_timestamps) / 10.0
    return round(rps, 2)


def compute_rates():
    total = stats["total_attempts"]
    if total > 0:
        stats["initiation_rate_pct"] = round((stats["initiated"] / total) * 100, 2)
        stats["denial_rate_pct"] = round((stats["denied"] / total) * 100, 2)
        stats["timeout_rate_pct"] = round((stats["timed_out"] / total) * 100, 2)
    else:
        stats["initiation_rate_pct"] = 0.0
        stats["denial_rate_pct"] = 0.0
        stats["timeout_rate_pct"] = 0.0

    control_sent = stats["control_sent"]
    if control_sent > 0:
        stats["control_success_pct"] = round(
            (stats["control_completed"] / control_sent) * 100, 2
        )
    else:
        stats["control_success_pct"] = 0.0


def update_system_stats():
    try:
        raw = _process.cpu_percent(interval=None)
        try:
            cores = len(_process.cpu_affinity())
        except Exception:
            cores = psutil.cpu_count(logical=True) or 1

        cpu = raw / max(cores, 1)
        cpu = min(max(cpu, 0.0), 100.0)

        mem = _process.memory_info()
        ram_mb = round(mem.rss / (1024 * 1024), 2)

        stats["cpu_current_pct"] = round(cpu, 2)
        stats["ram_current_mb"] = ram_mb

        if cpu > stats["cpu_peak_pct"]:
            stats["cpu_peak_pct"] = round(cpu, 2)
        if ram_mb > stats["ram_peak_mb"]:
            stats["ram_peak_mb"] = ram_mb
    except Exception:
        pass

    stats["uptime_seconds"] = round(time.time() - _start_time, 1)

    with _response_lock:
        if _response_times:
            stats["avg_response_ms"] = round(sum(_response_times) / len(_response_times), 3)
        else:
            stats["avg_response_ms"] = 0.0


def save_stats():
    global _last_save
    now = time.time()
    if now - _last_save < SAVE_INTERVAL:
        return
    _last_save = now
    with open("/root/stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f)

    rps = compute_rps()
    stats["current_rps"] = rps
    if rps > stats["peak_rps"]:
        stats["peak_rps"] = rps

    update_system_stats()
    compute_rates()

    with open("/root/stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)


def record_history():
    while True:
        time.sleep(5)
        with stats_lock:
            snap = {
                "ts": round(time.time() - _start_time, 0),
                "rps": stats["current_rps"],
                "initiated": stats["initiated"],
                "denied": stats["denied"],
                "timed_out": stats["timed_out"],
                "cpu": stats["cpu_current_pct"],
                "ram": stats["ram_current_mb"],
                "control_success_pct": stats["control_success_pct"],
            }
        with _history_lock:
            _history.append(snap)


def bump_denial(reason):
    with stats_lock:
        stats["total_attempts"] += 1
        stats["denied"] += 1
        key = reason if reason in stats["denied_breakdown"] else "malformed"
        stats["denied_breakdown"][key] += 1
        save_stats()


def bump_initiated():
    with stats_lock:
        stats["total_attempts"] += 1
        stats["initiated"] += 1
        stats["control_sent"] += 1
        stats["control_completed"] += 1
        save_stats()


def bump_timed_out():
    with stats_lock:
        stats["total_attempts"] += 1
        stats["timed_out"] += 1
        stats["control_sent"] += 1
        stats["control_timed_out"] += 1
        save_stats()


def bump_internal_error():
    with stats_lock:
        stats["total_attempts"] += 1
        stats["internal_errors"] += 1
        save_stats()


def sign(r, c, n, e):
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

    if not all(isinstance(x, str) for x in (rr, cc, n, e, s)):
        raise ValueError("bad token fields")

    return rr, cc, n, e, s


class Provider(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        t0 = time.time()
        register_attempt_timestamp()

        try:
            if self.path != "/ingest":
                self.send_response(404)
                self.end_headers()
                return

            size = int(self.headers.get("Content-Length", 0))

            try:
                data = json.loads(self.rfile.read(size))
            except Exception:
                bump_denial("malformed")
                self.send_response(400)
                self.end_headers()
                return

            r = data.get("request_repr")
            c = data.get("verification_context")
            token = data.get("provider_token")

            if not all(isinstance(x, str) and x for x in (r, c, token)):
                bump_denial("missing_fields")
                self.send_response(403)
                self.end_headers()
                return

            if not c.startswith("ctx_"):
                bump_denial("bad_context")
                self.send_response(403)
                self.end_headers()
                return

            try:
                rr, cc, n, e, s = decode_token(token)
            except Exception:
                bump_denial("malformed")
                self.send_response(403)
                self.end_headers()
                return

            try:
                exp = int(e)
            except Exception:
                bump_denial("bad_expiry")
                self.send_response(403)
                self.end_headers()
                return

            now = int(time.time())

            if rr != r or cc != c:
                bump_denial("mismatch")
                self.send_response(403)
                self.end_headers()
                return

            if now > exp:
                bump_denial("expired")
                self.send_response(403)
                self.end_headers()
                return

            if s != sign(rr, cc, n, e):
                bump_denial("bad_signature")
                self.send_response(403)
                self.end_headers()
                return

            with nonce_lock:
                expired_nonces = [k for k, v in used_nonces.items() if int(v) <= now]
                for k in expired_nonces:
                    del used_nonces[k]

                if n in used_nonces:
                    bump_denial("replay")
                    self.send_response(403)
                    self.end_headers()
                    return

                used_nonces[n] = e

            elapsed = round((time.time() - t0) * 1000, 3)
            with _response_lock:
                _response_times.append(elapsed)
                if len(_response_times) > 10000:
                    del _response_times[:5000]

            bump_initiated()
            self.send_response(200)
            self.end_headers()

        except BrokenPipeError:
            bump_timed_out()
        except TimeoutError:
            bump_timed_out()
        except Exception:
            bump_internal_error()
            try:
                self.send_response(500)
                self.end_headers()
            except Exception:
                pass


class StatsHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/stats":
            with stats_lock:
                payload = json.dumps(stats, indent=2).encode()
            self._json(payload)
            return

        if self.path == "/history":
            with _history_lock:
                payload = json.dumps(list(_history)).encode()
            self._json(payload)
            return

        if self.path == "/health":
            self._json(json.dumps({"status": "ok"}).encode())
            return

        self.send_response(404)
        self.end_headers()

    def _json(self, payload):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def start_stats_server():
    ThreadingHTTPServer(("0.0.0.0", 8000), StatsHandler).serve_forever()


threading.Thread(target=start_stats_server, daemon=True).start()
threading.Thread(target=record_history, daemon=True).start()

print("Provider listening on 127.0.0.1:9090")
print("Stats serving on 0.0.0.0:8000")

save_stats()
ThreadingHTTPServer(("127.0.0.1", 9090), Provider).serve_forever()
root@ubuntu-s-2vcpu-2gb-nyc1-01:~# 
