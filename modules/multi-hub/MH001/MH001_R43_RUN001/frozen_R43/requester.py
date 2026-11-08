"""Construct provider-bound artifacts from already-issued authority; never mint/sign."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import io
import ipaddress
import json
from pathlib import Path

import routes
import wire


def digest(value):
    return hashlib.sha256(value).hexdigest()



def literal_endpoint(address):
    # Reuse only the generic endpoint validator, never the hub route-file loader.
    endpoint = routes.endpoint(dict(address))
    if "%" in endpoint["host"]:
        raise ValueError("scoped_ip_not_supported")
    return endpoint


def load_approved_hubs(path):
    config = json.loads(Path(path).read_bytes(), object_pairs_hook=routes.unique)
    if not isinstance(config, dict) or set(config) != {"approved_hubs"}:
        raise ValueError("approved_hub_configuration_fields")
    if not isinstance(config["approved_hubs"], list):
        raise ValueError("approved_hubs_must_be_list")
    approved = set()
    for entry in config["approved_hubs"]:
        if not isinstance(entry, dict):
            raise ValueError("approved_hub_entry_must_be_object")
        endpoint = literal_endpoint(entry)
        pair = (endpoint["host"], endpoint["port"])
        if pair in approved:
            raise ValueError("duplicate_approved_hub")
        approved.add(pair)
    return frozenset(approved)


def validate_destination(address, approved_hubs=()):
    endpoint = literal_endpoint(address)
    if (not ipaddress.ip_address(endpoint["host"]).is_loopback
            and (endpoint["host"], endpoint["port"]) not in approved_hubs):
        raise ValueError("remote_destination_not_approved")
    return endpoint


def prepare(operation, issued_package, context, destination, output):
    if destination not in routes.DESTINATIONS or not isinstance(context, str):
        raise ValueError("destination_or_context")
    request_repr = digest(operation)
    binding = digest(("NUVL_BIND_V1|" + request_repr + "|" + context).encode("utf-8"))
    artifact = {"request_repr": request_repr, "verification_context": context, "binding": binding,
                "provider_authorization_b64": base64.urlsafe_b64encode(issued_package).rstrip(b"=").decode("ascii")}
    body = json.dumps(artifact, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")
    if len(body) > wire.MAX_BODY:
        raise ValueError("provider_artifact_too_large")
    packet = (b"POST /ingest HTTP/1.1\r\nHost: requester.invalid\r\nX-MH-Destination: "
              + destination.encode("ascii") + b"\r\nContent-Type: application/json\r\nContent-Length: "
              + str(len(body)).encode("ascii") + b"\r\n\r\n" + body)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    (output / "request.http").write_bytes(packet)
    (output / "body.bin").write_bytes(body)
    (output / "requester_observation.json").write_text(json.dumps({
        "destination": destination, "body_sha256": digest(body), "packet_sha256": digest(packet),
        "operation_sha256": request_repr, "issued_package_sha256": digest(issued_package),
        "binding": binding, "signature_verified_by_adapter": False}, indent=2) + "\n", encoding="utf-8")
    return packet


def submit(packet, address, receipt, approved_hubs=()):
    endpoint = validate_destination(address, approved_hubs)
    stream = io.BytesIO(packet)
    method, _, _, count = wire.request_head(stream)
    body = wire.read_exact(stream, count)
    if stream.read(1):
        raise ValueError("extra_request_bytes")
    # Reserve evidence output before any send; no silent overwrite or automatic resend.
    with Path(receipt).open("x", encoding="utf-8") as output:
        record = {"timestamp": datetime.now(timezone.utc).isoformat(), "hub": endpoint,
                  "packet_sha256": digest(packet), "body_sha256": digest(body),
                  "provider_execution": "NOT_INFERRED"}
        output.write(json.dumps(dict(record, transport_result="send_pending")) + "\n")
        output.flush()
        try:
            with wire.connect(endpoint, 20) as sock:
                sock.sendall(packet)
                with sock.makefile("rb") as incoming:
                    response = wire.response(incoming, method)
            record.update(transport_result="response_received", response_sha256=digest(response))
        except (OSError, wire.WireError):
            output.write(json.dumps(dict(record, transport_result="TRANSPORT_ERROR_EXECUTION_UNKNOWN")) + "\n")
            raise
        output.write(json.dumps(record) + "\n")
        return response


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    build = actions.add_parser("prepare")
    build.add_argument("--operation", type=Path, required=True)
    build.add_argument("--issued", type=Path, required=True)
    build.add_argument("--context", required=True)
    build.add_argument("--destination", choices=sorted(routes.DESTINATIONS), required=True)
    build.add_argument("--output", type=Path, required=True)
    send = actions.add_parser("send", help="Loopback by default; exact approved IP/port pairs only otherwise")
    send.add_argument("--request", type=Path, required=True)
    send.add_argument("--host", required=True)
    send.add_argument("--port", type=int, required=True)
    send.add_argument("--receipt", type=Path, required=True)
    send.add_argument("--approved-hubs", type=Path, help="Optional requester-only approved endpoint list")
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(args.operation.read_bytes(), args.issued.read_bytes(), args.context,
                args.destination, args.output)
    else:
        try:
            approved = load_approved_hubs(args.approved_hubs) if args.approved_hubs else frozenset()
            endpoint = validate_destination({"host": args.host, "port": args.port}, approved)
        except (ValueError, TypeError, OSError) as error:
            parser.error(str(error))
        reply = submit(args.request.read_bytes(), endpoint, args.receipt, approved_hubs=approved)
        print(json.dumps({"transport_response_sha256": digest(reply), "provider_execution": "NOT_INFERRED"}))


if __name__ == "__main__":
    main()
