"""Separate desktop launch adapters; binds loopback only during local validation."""
import argparse
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone
from artifact import canonical_bytes, verify, produce
from cryptography.hazmat.primitives import serialization

ROOT = Path(__file__).resolve().parents[1]


def utc():
    return datetime.now(timezone.utc).isoformat()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("role", choices=["producer", "verifier", "relay", "tap", "tamper"])
    p.add_argument("--port", type=int, default=0)
    p.add_argument("--target", type=int)
    p.add_argument("--directory", type=Path, required=True)
    p.add_argument("--trust", type=Path)
    p.add_argument("--key", type=Path)
    args = p.parse_args()
    d = args.directory
    d.mkdir(parents=True, exist_ok=True)
    if args.role == "producer":
        key = serialization.load_pem_private_key(args.key.read_bytes(), password=None)
        observed = sorted([9, 1, 4, 2])
        if observed != [1, 2, 4, 9]:
            raise RuntimeError("local_operation_failed")
        (d / "operation.json").write_bytes(canonical_bytes(dict(utc=utc(), event_id="LOCAL_SORT_V1",
            input=[9, 1, 4, 2], observed=observed, outcome="SUCCESS", boundary="sort_completed")))
        with (d / "artifact.json").open("xb") as f:
            f.write(produce(key))
    if args.role == "relay":
        sys.path.insert(0, str(ROOT / "reference" / "MH001_R43"))
        import hub
        config = {"hub_id": "HUB_B", "listen": {"host": "127.0.0.1", "port": args.port},
                  "timeout_seconds": 10, "routes": {
                      "PROVIDER_A": {"next_hop": "PROVIDER_A", "endpoint": {"host": "127.0.0.1", "port": 1}},
                      "PROVIDER_B": {"next_hop": "PROVIDER_B", "endpoint": {"host": "127.0.0.1", "port": args.target}}}}
        # Hub alone is reused; the two-hub CLI/pair validation is inapplicable.
        (d / "config.json").write_bytes(canonical_bytes(config))
        with (d / "relay.jsonl").open("x", encoding="utf-8") as log, hub.Hub(config, log) as server:
            ready(server.server_address[1], args.role)
            server.serve_forever()
        return
    trust = json.loads(args.trust.read_bytes()) if args.role == "verifier" else None
    sequence = 0

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *_):
            pass

        def do_POST(self):
            nonlocal sequence
            sequence += 1
            count = self.headers.get_all("Content-Length", [])
            if len(count) != 1 or not count[0].isdigit() or not 0 <= int(count[0]) <= 65536:
                self.send_error(400)
                return
            raw = self.rfile.read(int(count[0]))
            (d / f"{sequence:03d}-ingress.bin").write_bytes(raw)
            if args.role == "verifier":
                decision = verify(raw, trust)
                decision.update(pid=os.getpid(), process_instance=instance, utc=utc())
                response = canonical_bytes(decision)
                (d / f"{sequence:03d}-decision.json").write_bytes(response)
                status = 200 if decision["accepted"] else 422
            elif args.role in {"tap", "tamper"}:
                if args.role == "tamper":
                    obj = json.loads(raw)
                    obj["event"]["outcome"] = "FAILURE"
                    raw = canonical_bytes(obj)
                    (d / f"{sequence:03d}-mutation.json").write_bytes(canonical_bytes({
                        "field": "event.outcome", "before": "SUCCESS", "after": "FAILURE",
                        "signature_replaced": False}))
                (d / f"{sequence:03d}-egress.bin").write_bytes(raw)
                c = http.client.HTTPConnection("127.0.0.1", args.target, timeout=10)
                c.request("POST", "/verify", raw, {"Content-Type": "application/json", "X-MH-Destination": "PROVIDER_B"})
                r = c.getresponse()
                status, response = r.status, r.read()
                c.close()
            else:
                status, response = 405, b"{}"
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(response)
            self.close_connection = True

    instance = os.urandom(16).hex()
    server = HTTPServer(("127.0.0.1", args.port), Handler)
    ready(server.server_address[1], args.role, instance)
    server.serve_forever()


def ready(port, role, instance=None):
    print(json.dumps(dict(port=port, role=role, pid=os.getpid(), process_instance=instance, started_utc=utc())), flush=True)


if __name__ == "__main__":
    main()
