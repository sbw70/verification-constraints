#!/usr/bin/env python3

import argparse
import base64
import hashlib
import json
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LISTEN_HOST = "0.0.0.0"
DEFAULT_LISTEN_PORT = 19060
DEFAULT_TARGET_PORT = 19061
DEFAULT_TIMEOUT = 5.0
MAX_REQUEST_BYTES = 65536


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def recv_line(sock):
    data = bytearray()

    while True:
        chunk = sock.recv(4096)

        if not chunk:
            break

        data.extend(chunk)

        if len(data) > MAX_REQUEST_BYTES:
            raise ValueError("request exceeds maximum size")

        if b"\n" in chunk:
            break

    if not data:
        raise ValueError("empty request")

    line = bytes(data).split(b"\n", 1)[0]

    if not line:
        raise ValueError("empty request line")

    return line


def send_to_endpoint(target_host, target_port, payload, timeout):
    with socket.create_connection(
        (target_host, target_port),
        timeout=timeout
    ) as sock:
        sock.settimeout(timeout)
        sock.sendall(payload + b"\n")
        return recv_line(sock)


def mutate_request(raw_request, mode):
    if mode == "pass" or mode == "replay":
        return raw_request

    envelope = json.loads(raw_request.decode("utf-8"))

    if not isinstance(envelope, dict):
        raise ValueError("request envelope must be a JSON object")

    authority_b64 = envelope.get("authority_b64")
    signature_b64 = envelope.get("signature_b64")

    if not isinstance(authority_b64, str):
        raise ValueError("missing authority_b64")

    if not isinstance(signature_b64, str):
        raise ValueError("missing signature_b64")

    authority_raw = base64.b64decode(
        authority_b64,
        validate=True
    )

    authority = json.loads(authority_raw.decode("utf-8"))

    if not isinstance(authority, dict):
        raise ValueError("authority must decode to a JSON object")

    if mode == "mutate-action":
        authority["action"] = "move_servo_admin"

    elif mode == "mutate-context":
        authority["context"] = "esp_local_006_relay_mutated"

    elif mode == "mutate-device":
        authority["device_id"] = "esp32-xiao-servo-99"

    elif mode == "mutate-max-uses":
        authority["max_uses"] = 2

    else:
        raise ValueError(f"unsupported mode: {mode}")

    mutated_authority = json.dumps(
        authority,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")

    envelope["authority_b64"] = base64.b64encode(
        mutated_authority
    ).decode("ascii")

    # Intentionally retain the original provider signature.
    # The relay has no provider private key and cannot produce a
    # valid signature for the modified authority.
    envelope["signature_b64"] = signature_b64

    return json.dumps(
        envelope,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode("utf-8")


def write_log(log_path, record):
    line = json.dumps(
        record,
        separators=(",", ":"),
        sort_keys=True
    )

    print(line, flush=True)

    with log_path.open("a", encoding="utf-8") as f:
        f.write(line)
        f.write("\n")


def handle_client(
    client,
    peer,
    args,
    log_path
):
    raw_request = recv_line(client)

    outbound = mutate_request(
        raw_request,
        args.mode
    )

    record = {
        "timestamp": utc_now(),
        "peer": f"{peer[0]}:{peer[1]}",
        "mode": args.mode,
        "target": f"{args.target}:{args.target_port}",
        "ingress_sha256": sha256_hex(raw_request),
        "egress_sha256": sha256_hex(outbound),
        "ingress_bytes": len(raw_request),
        "egress_bytes": len(outbound),
    }

    if args.mode == "replay":
        first_response = send_to_endpoint(
            args.target,
            args.target_port,
            outbound,
            args.timeout
        )

        second_response = send_to_endpoint(
            args.target,
            args.target_port,
            outbound,
            args.timeout
        )

        record["first_response_sha256"] = sha256_hex(
            first_response
        )

        record["second_response_sha256"] = sha256_hex(
            second_response
        )

        record["first_response"] = first_response.decode(
            "utf-8",
            errors="replace"
        )

        record["second_response"] = second_response.decode(
            "utf-8",
            errors="replace"
        )

        response = json.dumps(
            {
                "relay_mode": "replay",
                "first_response": record["first_response"],
                "second_response": record["second_response"],
            },
            separators=(",", ":")
        ).encode("utf-8")

    else:
        endpoint_response = send_to_endpoint(
            args.target,
            args.target_port,
            outbound,
            args.timeout
        )

        record["endpoint_response_sha256"] = sha256_hex(
            endpoint_response
        )

        record["endpoint_response"] = endpoint_response.decode(
            "utf-8",
            errors="replace"
        )

        response = endpoint_response

    write_log(log_path, record)

    client.sendall(response + b"\n")


def main():
    parser = argparse.ArgumentParser(
        description="ESP-LOCAL-006 application-layer hostile relay"
    )

    parser.add_argument(
        "--listen-host",
        default=DEFAULT_LISTEN_HOST
    )

    parser.add_argument(
        "--listen-port",
        type=int,
        default=DEFAULT_LISTEN_PORT
    )

    parser.add_argument(
        "--target",
        required=True,
        help="ESP-LOCAL-006 endpoint IPv4 address"
    )

    parser.add_argument(
        "--target-port",
        type=int,
        default=DEFAULT_TARGET_PORT
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT
    )

    parser.add_argument(
        "--mode",
        choices=[
            "pass",
            "mutate-action",
            "mutate-context",
            "mutate-device",
            "mutate-max-uses",
            "replay",
        ],
        default="pass"
    )

    parser.add_argument(
        "--log",
        default=str(
            Path.home()
            / "ESP_LOCAL_006"
            / "evidence"
            / "ESP_LOCAL_006_RELAY.jsonl"
        )
    )

    args = parser.parse_args()

    log_path = Path(args.log)
    log_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as server:
        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        server.bind(
            (
                args.listen_host,
                args.listen_port
            )
        )

        server.listen(8)

        print(
            "ESP-LOCAL-006 hostile relay"
        )
        print(
            f"listen={args.listen_host}:{args.listen_port}"
        )
        print(
            f"target={args.target}:{args.target_port}"
        )
        print(
            f"mode={args.mode}"
        )
        print(
            f"log={log_path}"
        )
        print(
            "provider_private_key=ABSENT"
        )
        print(
            "signing_capability=ABSENT"
        )
        print(
            "006_RELAY_READY",
            flush=True
        )

        while True:
            client, peer = server.accept()

            with client:
                client.settimeout(args.timeout)

                try:
                    handle_client(
                        client,
                        peer,
                        args,
                        log_path
                    )

                except Exception as exc:
                    error_record = {
                        "timestamp": utc_now(),
                        "peer": f"{peer[0]}:{peer[1]}",
                        "mode": args.mode,
                        "error": type(exc).__name__,
                        "detail": str(exc),
                    }

                    write_log(
                        log_path,
                        error_record
                    )

                    error_response = json.dumps(
                        {
                            "relay_error": type(exc).__name__,
                            "detail": str(exc),
                        },
                        separators=(",", ":")
                    ).encode("utf-8")

                    try:
                        client.sendall(
                            error_response + b"\n"
                        )
                    except OSError:
                        pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n006_RELAY_STOPPED")
        sys.exit(0)
