"""MH001 mechanical single-threaded hub. No authorization or provider-state logic."""
import argparse
from datetime import datetime, timezone
import hashlib
from http import HTTPStatus
import json
from pathlib import Path
import socket
import socketserver

import routes
import wire


def digest(value):
    return hashlib.sha256(value).hexdigest()


class Hub(socketserver.TCPServer):
    allow_reuse_address = False

    def __init__(self, config, log):
        self.config, self.log, self.sequence = config, log, 0
        self.address_family = socket.AF_INET6 if ":" in config["listen"]["host"] else socket.AF_INET
        super().__init__((config["listen"]["host"], config["listen"]["port"]), Handler)

    def observe(self, record):
        self.log.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        self.log.flush()


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        server = self.server
        server.sequence += 1
        record = {"hub_id": server.config["hub_id"], "sequence": server.sequence,
                  "timestamp": datetime.now(timezone.utc).isoformat(),
                  "ingress_body_sha256": None, "egress_body_sha256": None,
                  "preserved_headers": [], "next_hop": None, "transport_result": "not_forwarded"}
        self.connection.settimeout(15)  # Client framing timeout, separate from downstream.
        response_started = False
        try:
            method, target, fields, count = wire.request_head(self.rfile)
            destinations = wire.values(fields, b"x-mh-destination")
            if len(destinations) != 1 or destinations[0] not in (b"PROVIDER_A", b"PROVIDER_B"):
                raise wire.WireError("invalid_destination")
            route = server.config["routes"][destinations[0].decode("ascii")]
            record["next_hop"] = route["next_hop"]
            body = wire.read_exact(self.rfile, count)
            record["ingress_body_sha256"] = digest(body)
            record["preserved_headers"] = [
                {"name": raw.partition(b":")[0].decode("ascii"),
                 "value_sha256": digest(value),
                 "wire_value_sha256": digest(raw.partition(b":")[2])}
                for _, value, raw in wire.kept(fields)]
            packet = wire.request_bytes(method, target, fields, body, route["endpoint"])
            # Flush ingress evidence BEFORE attempting any provider submission.
            server.observe(dict(record, observation="ingress"))
            record["transport_result"] = "downstream_connecting"
            try:
                with wire.connect(route["endpoint"], server.config["timeout_seconds"]) as downstream:
                    record["egress_body_sha256"] = digest(body)
                    record["transport_result"] = "downstream_send_attempted"
                    downstream.sendall(packet)  # Exactly one send attempt. Never retry.
                    with downstream.makefile("rb") as stream:
                        reply = wire.response(stream, method)
            except TimeoutError:
                raise wire.WireError("downstream_timeout", 504) from None
            except wire.WireError:
                raise wire.WireError("unsupported_downstream_response", 502) from None
            except OSError:
                raise wire.WireError("downstream_unreachable_or_io", 502) from None
            record["transport_result"] = "downstream_response_received"
            response_started = True
            self.wfile.write(reply)
            self.wfile.flush()
            record["transport_result"] = "response_forwarded"
        except wire.WireError as error:
            record["transport_result"] = error.identifier
            self.error(error.status, error.identifier)
        except (TimeoutError, OSError):
            record["transport_result"] = "client_io_or_observation_error"
            if not response_started:
                self.error(400, "client_io_or_observation_error")
        finally:
            server.observe(dict(record, observation="result"))

    def error(self, status, identifier):
        body = (f"MH_HUB_ERROR {self.server.config['hub_id']} {identifier}\n").encode("ascii")
        head = (f"HTTP/1.1 {status} {HTTPStatus(status).phrase}\r\n"
                f"Content-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n").encode("ascii")
        try:
            self.wfile.write(head + body)
            self.wfile.flush()
        except OSError:
            pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hub-a", type=Path, required=True)
    parser.add_argument("--hub-b", type=Path, required=True)
    parser.add_argument("--identity", choices=["HUB_A", "HUB_B"], required=True)
    parser.add_argument("--log", type=Path, required=True)
    args = parser.parse_args()
    a, b = routes.validate_pair(args.hub_a, args.hub_b)
    config = a if args.identity == "HUB_A" else b
    with args.log.open("x", encoding="utf-8", newline="\n") as log, Hub(config, log) as server:
        print(json.dumps({"hub_id": args.identity, "status": "LISTENING",
                          "config_sha256": digest((args.hub_a if args.identity == "HUB_A" else args.hub_b).read_bytes()),
                          "peer_config_sha256": digest((args.hub_b if args.identity == "HUB_A" else args.hub_a).read_bytes())}), flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
