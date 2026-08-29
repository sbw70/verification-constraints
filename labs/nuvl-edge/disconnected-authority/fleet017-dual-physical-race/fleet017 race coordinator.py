#!/usr/bin/env python3
"""
FLEET-017 race coordinator.

Purpose:
    Arm two physically distinct XIAO endpoints that intentionally present the
    SAME logical authority identity, release them together, and collect their
    results keyed by PHYSICAL id so neither can overwrite the other.

This is deliberately separate from the normal fleet coordinator:
    - normal fleet coordinator keys results by device_id
    - FLEET-017 endpoints share one device_id, so that would collide
    - this coordinator keys everything by physical_id

Endpoints:
    GET  /arm?physical_id=<id>       -> {"armed": bool, "run_id": str|null, "wait_ms": int}
    POST /result                     -> body: JSON result dict incl. physical_id
    GET  /status                     -> current run + collected results
    POST /start                      -> operator arms a new run
    POST /reset                      -> clear run + results

Operator flow:
    1. start this coordinator
    2. POST /start   (arms a new run_id, both boards will see it on next poll)
    3. both boards poll /arm, receive same run_id, wait for their wait_ms, fire
    4. GET /status   to read both results

Release model:
    Each board polls /arm. The first poll after a run is armed returns the
    run_id plus a relative wait_ms computed so that both boards aim at the same
    absolute release instant. Relative wait is used because MicroPython and
    CPython do not share an epoch representation.
"""

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 19053

# How long after the first board polls we schedule the release.
# Long enough that the second board is expected to have polled and armed.
RELEASE_WINDOW_MS = 3000

_lock = threading.Lock()

_state = {
    "run_id": None,
    "release_at_ns": None,   # monotonic ns on this host
    "armed_physical": {},    # physical_id -> poll timestamp ns
    "results": {},           # physical_id -> result dict
}


def _now_ns():
    return time.monotonic_ns()


def _json_response(handler, obj, code=200):
    body = json.dumps(obj, sort_keys=True).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Connection", "close")
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        # Quieter default logging; we print our own lines.
        return

    def do_GET(self):
        if self.path.startswith("/arm"):
            self._handle_arm()
        elif self.path.startswith("/status"):
            self._handle_status()
        else:
            _json_response(self, {"error": "not_found"}, 404)

    def do_POST(self):
        if self.path.startswith("/result"):
            self._handle_result()
        elif self.path.startswith("/start"):
            self._handle_start()
        elif self.path.startswith("/reset"):
            self._handle_reset()
        else:
            _json_response(self, {"error": "not_found"}, 404)

    # ---- handlers ----

    def _query(self, key):
        if "?" not in self.path:
            return None
        query = self.path.split("?", 1)[1]
        for pair in query.split("&"):
            if "=" in pair:
                k, v = pair.split("=", 1)
                if k == key:
                    return v
        return None

    def _handle_arm(self):
        physical_id = self._query("physical_id")
        if not physical_id:
            _json_response(self, {"error": "missing_physical_id"}, 400)
            return

        with _lock:
            run_id = _state["run_id"]
            if run_id is None:
                _json_response(self, {"armed": False, "run_id": None, "wait_ms": 0})
                return

            now = _now_ns()

            if physical_id not in _state["armed_physical"]:
                _state["armed_physical"][physical_id] = now
                print("ARMED physical_id={} run_id={}".format(physical_id, run_id))

            if _state["release_at_ns"] is None:
                _state["release_at_ns"] = now + (RELEASE_WINDOW_MS * 1_000_000)
                print("RELEASE_SCHEDULED run_id={} in_ms={}".format(
                    run_id, RELEASE_WINDOW_MS))

            wait_ns = _state["release_at_ns"] - now
            wait_ms = int(wait_ns // 1_000_000)
            if wait_ms < 0:
                wait_ms = 0

            _json_response(self, {
                "armed": True,
                "run_id": run_id,
                "wait_ms": wait_ms,
            })

    def _handle_result(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            result = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            _json_response(self, {"error": "bad_json", "detail": str(exc)}, 400)
            return

        physical_id = result.get("physical_id")
        if not physical_id:
            _json_response(self, {"error": "missing_physical_id"}, 400)
            return

        with _lock:
            result["coordinator_received_ns"] = _now_ns()
            _state["results"][physical_id] = result
            print("RESULT physical_id={} decision={} reason={} artifact_id={}".format(
                physical_id,
                result.get("decision"),
                result.get("reason"),
                result.get("artifact_id"),
            ))
            _json_response(self, {"stored": True})

    def _handle_status(self):
        with _lock:
            _json_response(self, {
                "run_id": _state["run_id"],
                "armed_physical": sorted(_state["armed_physical"].keys()),
                "results": _state["results"],
            })

    def _handle_start(self):
        with _lock:
            run_id = "fleet017-{}".format(int(time.time()))
            _state["run_id"] = run_id
            _state["release_at_ns"] = None
            _state["armed_physical"] = {}
            _state["results"] = {}
            print("RUN_STARTED run_id={}".format(run_id))
            _json_response(self, {"run_id": run_id})

    def _handle_reset(self):
        with _lock:
            _state["run_id"] = None
            _state["release_at_ns"] = None
            _state["armed_physical"] = {}
            _state["results"] = {}
            print("RUN_RESET")
            _json_response(self, {"reset": True})


def main():
    server = ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), Handler)
    print("FLEET017_COORDINATOR_START host={} port={}".format(LISTEN_HOST, LISTEN_PORT))
    print("RELEASE_WINDOW_MS={}".format(RELEASE_WINDOW_MS))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("FLEET017_COORDINATOR_STOP")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
