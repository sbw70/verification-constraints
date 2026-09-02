#!/usr/bin/env python3
import argparse
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SECRET = os.environ.get("DDIL_SECRET", "dev_ddil_lab_secret_change_me").encode()
DEFAULT_CONTEXT = os.environ.get("DDIL_CONTEXT", "ctx_demo")
DEFAULT_ACTION = os.environ.get("DDIL_ACTION", "initiate")


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def b64url_decode(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


def canonical(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def request_repr(action: str, context: str) -> str:
    return hashlib.sha256(f"{action}|{context}".encode()).hexdigest()


def sign(payload: dict) -> str:
    unsigned = dict(payload)
    unsigned.pop("sig", None)
    return hmac.new(SECRET, canonical(unsigned), hashlib.sha256).hexdigest()


def mint_artifact(action: str, context: str, window_seconds: int) -> str:
    now = int(time.time())
    payload = {
        "action": action,
        "context": context,
        "nonce": secrets.token_urlsafe(16),
        "issued_at": now,
        "expires_at": now + int(window_seconds),
        "max_uses": 1,
        "request_repr": request_repr(action, context),
    }
    payload["sig"] = sign(payload)
    return b64url(canonical(payload))


class Handler(BaseHTTPRequestHandler):
    server_version = "DDILProviderPOC/0.1"

    def _send(self, code: int, obj: dict):
        body = json.dumps(obj, separators=(",", ":")).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        n = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(n) if n else b"{}"
        return json.loads(raw.decode() or "{}")

    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"ok": True, "service": "provider"})
        return self._send(404, {"ok": False, "error": "not_found"})

    def do_POST(self):
        try:
            data = self._read_json()
        except Exception as e:
            return self._send(400, {"decision": "denied", "reason": "malformed_json", "error": str(e)})

        if self.path == "/issue":
            action = data.get("action", DEFAULT_ACTION)
            context = data.get("context", DEFAULT_CONTEXT)
            window_seconds = int(data.get("window_seconds", 60))

            if action != DEFAULT_ACTION or context != DEFAULT_CONTEXT:
                return self._send(403, {
                    "decision": "denied",
                    "reason": "issuer_wrong_action_or_context",
                })

            artifact = mint_artifact(action, context, window_seconds)
            return self._send(200, {
                "decision": "issued",
                "artifact": artifact,
                "action": action,
                "context": context,
                "window_seconds": window_seconds,
            })

        if self.path == "/validate":
            action = data.get("action")
            context = data.get("context")

            if action == DEFAULT_ACTION and context == DEFAULT_CONTEXT:
                return self._send(200, {
                    "decision": "accepted",
                    "reason": "provider_admissible",
                    "source": "provider",
                })

            return self._send(200, {
                "decision": "denied",
                "reason": "provider_wrong_action_or_context",
                "source": "provider",
            })

        return self._send(404, {"ok": False, "error": "not_found"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8091)
    args = ap.parse_args()

    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"DDIL provider POC listening on http://{args.host}:{args.port}")
    print(f"action={DEFAULT_ACTION} context={DEFAULT_CONTEXT}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
