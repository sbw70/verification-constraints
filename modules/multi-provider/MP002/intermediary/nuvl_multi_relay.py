#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json
import threading
import urllib.request


HOST = "0.0.0.0"
PORT = 8080

MAX_REQUEST_BYTES = 1024 * 64
BIND_TAG = "NUVL_BIND_V1"

PROVIDERS = (
    {
        "url": "http://192.168.1.118:9090/ingest",
        "authorization_header": "X-Provider-A-Authorization",
    },
    {
        "url": "http://192.168.1.106:9090/ingest",
        "authorization_header": "X-Provider-B-Authorization",
    },
)


def mechanical_binding(
    request_repr_hex,
    verification_context,
):
    material = (
        BIND_TAG
        + "|"
        + request_repr_hex
        + "|"
        + verification_context
    ).encode("utf-8")

    return hashlib.sha256(
        material
    ).hexdigest()


def forward_async(
    url,
    artifact,
):
    def _send():
        try:
            body = json.dumps(
                artifact,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")

            req = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Content-Type": "application/json"
                },
                method="POST",
            )

            with urllib.request.urlopen(
                req,
                timeout=2,
            ):
                pass

        except Exception:
            pass

    threading.Thread(
        target=_send,
        daemon=True,
    ).start()


class NUVLHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        return

    def do_POST(self):

        if self.path != "/nuvl":
            self.send_response(404)
            self.end_headers()
            return

        try:
            length = int(
                self.headers.get(
                    "Content-Length",
                    "0",
                )
            )
        except Exception:
            length = 0

        if (
            length < 0
            or length > MAX_REQUEST_BYTES
        ):
            self.send_response(204)
            self.end_headers()
            return

        request_bytes = (
            self.rfile.read(length)
            if length > 0
            else b""
        )

        verification_context = (
            self.headers.get(
                "X-Verification-Context",
                "",
            )
        )

        request_repr = hashlib.sha256(
            request_bytes
        ).hexdigest()

        binding = mechanical_binding(
            request_repr,
            verification_context,
        )

        for provider in PROVIDERS:

            provider_authorization_b64 = (
                self.headers.get(
                    provider[
                        "authorization_header"
                    ],
                    "",
                )
            )

            artifact = {
                "request_repr": (
                    request_repr
                ),
                "verification_context": (
                    verification_context
                ),
                "binding": binding,
                "provider_authorization_b64": (
                    provider_authorization_b64
                ),
            }

            forward_async(
                provider["url"],
                artifact,
            )

        self.send_response(204)
        self.end_headers()


def main():
    print(
        "MP001_NUVL_MULTI_PROVIDER_RELAY"
    )
    print(
        "Listening on {}:{}".format(
            HOST,
            PORT,
        )
    )
    print(
        "Provider destinations:",
        len(PROVIDERS),
    )
    print(
        "Provider authorization verification: False"
    )
    print(
        "Provider secrets present: False"
    )

    ThreadingHTTPServer(
        (HOST, PORT),
        NUVLHandler,
    ).serve_forever()


if __name__ == "__main__":
    main()
