#!/usr/bin/env python3
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HOST = "0.0.0.0"
PORT = 19052

LOCK = threading.Lock()
CURRENT_RUN = None
RESULTS = {}


def canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def send_json(self, status, obj):
        body = canonical_bytes(obj)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        obj = json.loads(raw.decode("utf-8"))
        if not isinstance(obj, dict):
            raise ValueError("request_not_object")
        return obj

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/health":
            with LOCK:
                run_id = CURRENT_RUN["run_id"] if CURRENT_RUN else None
                result_count = len(RESULTS.get(run_id, {})) if run_id else 0
            self.send_json(
                200,
                {
                    "status": "ok",
                    "service": "multi_endpoint_coordinator",
                    "current_run_id": run_id,
                    "current_result_count": result_count,
                },
            )
            return

        if parsed.path == "/trigger":
            query = parse_qs(parsed.query)
            device_id = (query.get("device_id") or [""])[0]

            with LOCK:
                current = dict(CURRENT_RUN) if CURRENT_RUN else None

            if not current:
                self.send_json(200, {"armed": False})
                return

            mode = current["modes"].get(device_id)
            if mode is None:
                self.send_json(
                    200,
                    {
                        "armed": False,
                        "run_id": current["run_id"],
                    },
                )
                return

            self.send_json(
                200,
                {
                    "armed": True,
                    "run_id": current["run_id"],
                    "mode": mode,
                    "not_before_ms": current["not_before_ms"],
                },
            )
            return

        if parsed.path == "/summary":
            query = parse_qs(parsed.query)
            run_id = (query.get("run_id") or [""])[0]

            with LOCK:
                results = dict(RESULTS.get(run_id, {}))

            self.send_json(
                200,
                {
                    "run_id": run_id,
                    "results": results,
                    "result_count": len(results),
                },
            )
            return

        self.send_json(404, {"error": "not_found"})

    def do_POST(self):
        global CURRENT_RUN

        if self.path == "/start":
            try:
                payload = self.read_json()
                run_id = str(payload["run_id"])
                modes = payload["modes"]
                if not isinstance(modes, dict) or not modes:
                    raise ValueError("invalid_modes")

                delay_ms = int(payload.get("delay_ms", 1500))
                not_before_ms = int(time.time() * 1000) + delay_ms

                with LOCK:
                    CURRENT_RUN = {
                        "run_id": run_id,
                        "modes": dict(modes),
                        "not_before_ms": not_before_ms,
                    }
                    RESULTS[run_id] = {}

                print(
                    "START run_id={} devices={} not_before_ms={}".format(
                        run_id,
                        len(modes),
                        not_before_ms,
                    ),
                    flush=True,
                )

                self.send_json(
                    200,
                    {
                        "status": "armed",
                        "run_id": run_id,
                        "devices": len(modes),
                        "not_before_ms": not_before_ms,
                    },
                )
            except Exception as exc:
                self.send_json(
                    400,
                    {
                        "status": "error",
                        "reason": type(exc).__name__,
                    },
                )
            return

        if self.path == "/result":
            try:
                payload = self.read_json()
                run_id = str(payload["run_id"])
                device_id = str(payload["device_id"])

                with LOCK:
                    RESULTS.setdefault(run_id, {})[device_id] = payload

                print(
                    "RESULT run_id={} device_id={} decision={} reason={} elapsed_ms={}".format(
                        run_id,
                        device_id,
                        payload.get("decision"),
                        payload.get("reason"),
                        payload.get("elapsed_ms"),
                    ),
                    flush=True,
                )

                self.send_json(200, {"status": "recorded"})
            except Exception as exc:
                self.send_json(
                    400,
                    {
                        "status": "error",
                        "reason": type(exc).__name__,
                    },
                )
            return

        self.send_json(404, {"error": "not_found"})


def main():
    print("MULTI_ENDPOINT_COORDINATOR")
    print("Listening on {}:{}".format(HOST, PORT))
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
