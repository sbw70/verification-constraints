"""MD001 deployment adapters. Network commands require explicit invocation."""
import argparse
from datetime import datetime, timezone
import http.client
import io
import json
import os
from pathlib import Path
import socketserver
import sys
import threading
import uuid
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

BASE = Path(__file__).resolve().parent
REFERENCE = BASE / "runtime"
sys.path.insert(0, str(REFERENCE))
from artifact import canonical_bytes, digest, key_id, produce, verify, loads
import hub
import wire


def utc():
    return datetime.now(timezone.utc).isoformat()


def write(path, raw):
    with Path(path).open("xb") as f:
        f.write(raw)


def save(path, obj):
    write(path, canonical_bytes(obj))


def config(path):
    c = loads(Path(path).read_bytes())
    required = {"role", "listen", "allowed_peer", "target", "mode"}
    if type(c) is not dict or set(c) != required or c["role"] not in {"relay", "ingress", "verifier"}:
        raise ValueError("configuration_schema")
    wire_address(c["listen"])
    if c["target"] is not None:
        wire_address(c["target"])
    import ipaddress
    if c["allowed_peer"] is not None:
        ipaddress.IPv4Address(c["allowed_peer"])
    if c["role"] == "ingress" and (c["mode"] not in {"pass", "tamper"} or c["target"] is None):
        raise ValueError("ingress_configuration")
    if c["role"] != "ingress" and c["mode"] != "pass":
        raise ValueError("tamper_only_in_separate_ingress")
    if c["role"] == "relay" and c["target"] is None:
        raise ValueError("relay_target")
    if c["role"] == "verifier" and (c["target"] is not None or c["allowed_peer"] != "127.0.0.1"):
        raise ValueError("verifier_must_be_local_only")
    if c["role"] == "verifier" and c["listen"]["host"] != "127.0.0.1":
        raise ValueError("verifier_must_bind_loopback")
    return c


def wire_address(value):
    import ipaddress
    if type(value) is not dict or set(value) != {"host", "port"}:
        raise ValueError("endpoint_schema")
    ip = ipaddress.IPv4Address(value["host"])
    if ip.is_unspecified or ip.is_multicast or str(ip) != value["host"]:
        raise ValueError("numeric_specific_ipv4_required")
    if type(value["port"]) is not int or not 1 <= value["port"] <= 65535:
        raise ValueError("port")


def integrity():
    expected = loads((BASE / "RUNTIME_LOCK.json").read_bytes())
    for name, value in expected.items():
        if digest((REFERENCE / name).read_bytes()) != value:
            raise RuntimeError("runtime_integrity: " + name)


def send(endpoint, raw):
    wire_address(endpoint)
    c = http.client.HTTPConnection(endpoint["host"], endpoint["port"], timeout=15)
    try:
        c.request("POST", "/verify", raw, {"Content-Type": "application/json", "X-MH-Destination": "PROVIDER_B"})
        response = c.getresponse()
        body = response.read(65537)
        if len(body) > 65536:
            raise ValueError("response_too_large")
        return response.status, body
    finally:
        c.close()


class Server(socketserver.TCPServer):
    allow_reuse_address = True


def serve(c, trust, directory):
    class Handler(socketserver.StreamRequestHandler):
        def handle(self):
            self.connection.settimeout(15)
            status, response = 400, {"error": "malformed_http"}
            request_id = uuid.uuid4().hex
            try:
                method, target, fields, count = wire.request_head(self.rfile)
                raw = wire.read_exact(self.rfile, count)
                if c["allowed_peer"] and self.client_address[0] != c["allowed_peer"]:
                    status, response = 403, {"error": "peer_not_allowed"}
                else:
                    if method != b"POST" or target != b"/verify" or wire.values(fields, b"x-mh-destination") != [b"PROVIDER_B"]:
                        raise ValueError("method_path_or_destination")
                    if wire.values(fields, b"content-type") != [b"application/json"]:
                        raise ValueError("content_type")
                    write(directory / (request_id + "-ingress.bin"), raw)
                    save(directory / (request_id + "-transport.json"), {
                        "utc": utc(), "peer": list(self.client_address), "method": method.decode(),
                        "path": target.decode(), "headers": [line.decode("latin1") for _, _, line in fields],
                        "ingress_sha256": digest(raw), "mode": c["mode"]})
                    if c["role"] == "verifier":
                        response = verify(raw, trust)
                        response.update(pid=os.getpid(), process_instance=instance, utc=utc())
                        status = 200 if response["accepted"] else 422
                    else:
                        if c["mode"] == "tamper":
                            obj = loads(raw)
                            if obj["event"]["outcome"] != "SUCCESS":
                                raise ValueError("tamper_requires_success_fixture")
                            obj["event"]["outcome"] = "FAILURE"
                            raw = canonical_bytes(obj)
                            save(directory / (request_id + "-mutation.json"), {
                                "field": "event.outcome", "before": "SUCCESS", "after": "FAILURE",
                                "signature_replaced": False, "modified_sha256": digest(raw)})
                        write(directory / (request_id + "-egress.bin"), raw)
                        status, body = send(c["target"], raw)
                        write(directory / (request_id + "-downstream-response.bin"), body)
                        response = loads(body)
                    save(directory / (request_id + "-decision-or-response.json"), {"http_status": status, "response": response})
            except (ValueError, KeyError, TypeError, UnicodeError, wire.WireError) as error:
                status, response = 400, {"error": str(error)}
            except OSError as error:
                status, response = 502, {"error": str(error)}
            body = canonical_bytes(response)
            self.wfile.write(f"HTTP/1.1 {status} Result\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode() + body)

    instance = uuid.uuid4().hex
    with Server((c["listen"]["host"], c["listen"]["port"]), Handler) as server:
        ready(c, directory, instance)
        server.serve_forever()


def ready(c, directory, instance):
    record = dict(pid=os.getpid(), process_instance=instance, started_utc=utc(), configuration=c,
                  configuration_sha256=digest(canonical_bytes(c)), adapter_sha256=digest(Path(__file__).read_bytes()),
                  runtime_lock_sha256=digest((BASE / "RUNTIME_LOCK.json").read_bytes()))
    save(directory / "process.json", record)
    print(json.dumps(record), flush=True)


def relay(c, directory):
    # Frozen hub accepts A/B route selectors. A is safely terminated at a local
    # denial responder, never connected to the producer or another domain.
    class Deny(socketserver.StreamRequestHandler):
        def handle(self):
            self.connection.settimeout(2)
            try:
                _, _, _, n = wire.request_head(self.rfile)
                wire.read_exact(self.rfile, n)
                self.wfile.write(b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n")
            except (OSError, wire.WireError):
                pass
    with Server(("127.0.0.1", 0), Deny) as deny:
        threading.Thread(target=deny.serve_forever, daemon=True).start()
        hc = dict(hub_id="HUB_B", listen=c["listen"], timeout_seconds=10, routes={
            "PROVIDER_A": {"next_hop": "PROVIDER_A", "endpoint": {"host": "127.0.0.1", "port": deny.server_address[1]}},
            "PROVIDER_B": {"next_hop": "PROVIDER_B", "endpoint": c["target"]}})
        save(directory / "effective-hub-config.json", hc)
        # Preserve its normal HUB_B schema checks, without two-hub CLI coupling.
        hub.routes.load(directory / "effective-hub-config.json")
        with (directory / "relay.jsonl").open("x", encoding="utf-8") as log, hub.Hub(hc, log) as server:
            ready(c, directory, uuid.uuid4().hex)
            server.serve_forever()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    k = sub.add_parser("keygen"); k.add_argument("--out", type=Path, required=True)
    s = sub.add_parser("serve"); s.add_argument("--config", type=Path, required=True)
    s.add_argument("--trust", type=Path); s.add_argument("--out", type=Path, required=True)
    for command in ("produce-send", "resubmit"):
        s = sub.add_parser(command); s.add_argument("--host", required=True); s.add_argument("--port", type=int, required=True)
        s.add_argument("--out", type=Path, required=True)
        if command == "produce-send": s.add_argument("--key", type=Path, required=True)
        else: s.add_argument("--artifact", type=Path, required=True)
    a = p.parse_args()
    integrity()
    a.out.mkdir(parents=True, exist_ok=False)
    if a.command == "keygen":
        key = Ed25519PrivateKey.generate()
        write(a.out / "TEST_ONLY_private.pem", key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        if os.name != "nt": (a.out / "TEST_ONLY_private.pem").chmod(0o600)
        public = key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        save(a.out / "trust.json", {"DOMAIN_A": {key_id(key.public_key()): public.hex()}})
        save(a.out / "provisioning.json", dict(method="operator out-of-band transfer; verify fingerprint on B", key_id=key_id(key.public_key()), utc=utc(), disposable_test_key=True))
    elif a.command == "serve":
        c = config(a.config)
        trust = loads(a.trust.read_bytes()) if a.trust else None
        if c["role"] == "verifier":
            if not trust or set(trust) != {"DOMAIN_A"}: raise ValueError("public_trust_required")
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
            for kid, raw in trust["DOMAIN_A"].items():
                if key_id(Ed25519PublicKey.from_public_bytes(bytes.fromhex(raw))) != kid: raise ValueError("trust_fingerprint")
            save(a.out / "trust-provisioned.json", trust)
        elif trust is not None: raise ValueError("trust_only_on_verifier")
        if c["role"] == "relay": relay(c, a.out)
        else: serve(c, trust, a.out)
    else:
        if a.command == "produce-send":
            key = serialization.load_pem_private_key(a.key.read_bytes(), password=None)
            result = sorted([9, 1, 4, 2])
            if result != [1, 2, 4, 9]: raise RuntimeError("operation_failed")
            save(a.out / "operation.json", dict(event_id="LOCAL_SORT_V1", input=[9,1,4,2], observed=result, boundary="sort_completed", utc=utc()))
            raw = produce(key)
        else: raw = a.artifact.read_bytes()
        write(a.out / "artifact.json", raw)
        write(a.out / "signed-bytes.bin", b"NUVL-MD001-ARTIFACT-v1|" + canonical_bytes(loads(raw)["event"]))
        endpoint = dict(host=a.host, port=a.port)
        save(a.out / "submission.json", dict(utc=utc(), endpoint=endpoint, artifact_sha256=digest(raw), command=a.command, pid=os.getpid()))
        status, response = send(endpoint, raw)
        write(a.out / "response.bin", response)
        save(a.out / "result.json", dict(http_status=status, response=loads(response)))
        print(json.dumps(dict(http_status=status, response=loads(response))), flush=True)
        if status not in (200, 422): raise SystemExit(1)


if __name__ == "__main__":
    main()
