#!/usr/bin/env python3
import hashlib
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

EXPECTED_CONTEXT = "field_led_demo"
PORT = 8089


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_request(payload):
    bounded = {
        "context": payload.get("context"),
        "device_id": payload.get("device_id"),
        "nonce": payload.get("nonce"),
        "requested_action": payload.get("requested_action"),
    }
    canonical = json.dumps(bounded, sort_keys=True, separators=(",", ":"))
    return canonical, sha256_hex(canonical.encode("utf-8"))


def decision_for(payload):
    for field in ("device_id", "context", "requested_action", "nonce"):
        value = payload.get(field)
        if not isinstance(value, str) or not value:
            return "denied", "missing_" + field

    if payload["context"] != EXPECTED_CONTEXT:
        return "denied", "wrong_context"

    action = payload["requested_action"]

    if action == "accept":
        return "accepted", "provider_admissible"

    if action == "deny":
        return "denied", "unauthorized_request"

    if action == "deny_stale_replay":
        return "denied", "stale_replay_malformed"

    return "denied", "unknown_action"


def display(path, payload, canonical, request_repr, decision, reason):
    os.system("clear" if os.name != "nt" else "cls")

    print("XER0TRUST NUVL LOCAL BOUNDARY HARNESS")
    print("=" * 56)
    print("REQUEST RECEIVED AT LOCAL NUVL BOUNDARY")
    print()
    print("path:", path)

    if isinstance(payload, dict):
        print("device_id:", payload.get("device_id"))
        print("context:", payload.get("context"))
        print("action:", payload.get("requested_action"))
        print("nonce:", payload.get("nonce"))
    else:
        print("payload:", "<malformed or non-object>")

    print()
    print("BOUNDED REQUEST REPRESENTATION")
    print("request_repr:", request_repr)
    print("canonical:", canonical)
    print()
    print("PROVIDER DECISION:", decision.upper())
    print("REASON:", reason)
    print()
    print("Model:")
    print("endpoint emits request")
    print("NUVL boundary derives bounded representation")
    print("provider validator decides")
    print("endpoint displays returned result")
    print()
    print("Waiting for next ESP32 field-node request...")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _send_json(self, status_code, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path not in ("/nuvl", "/request"):
            self.send_response(404)
            self.end_headers()
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except Exception:
            length = 0

        raw = self.rfile.read(length)

        payload = None
        parse_error = None

        try:
            parsed = json.loads(raw.decode("utf-8") if raw else "")
            if isinstance(parsed, dict):
                payload = parsed
            else:
                parse_error = "non_object_json"
        except Exception:
            parse_error = "malformed_json"

        if payload is None:
            canonical = "<{}>".format(parse_error or "malformed_request")
            request_repr = sha256_hex(raw)
            decision = "denied"
            reason = parse_error or "malformed_request"
        else:
            canonical, request_repr = canonical_request(payload)
            decision, reason = decision_for(payload)

        response = {
            "decision": decision,
            "reason": reason,
            "timestamp": int(time.time()),
            "request_repr": request_repr,
            "boundary": "nuvl_local_pi",
        }

        display(self.path, payload, canonical, request_repr, decision, reason)
        self._send_json(200, response)


def main():
    print("XER0TRUST NUVL LOCAL BOUNDARY HARNESS")
    print("Listening on port", PORT)
    print("Health:  GET  /health")
    print("NUVL:    POST /nuvl")
    print("Compat:  POST /request")
    print("Waiting for ESP32 field-node request...")
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
