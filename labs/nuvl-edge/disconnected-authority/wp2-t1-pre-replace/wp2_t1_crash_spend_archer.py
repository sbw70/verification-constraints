#!/usr/bin/env python3

from pathlib import Path
import hashlib
import json
import socket
import time
import urllib.request


PI_HOST = "192.168.0.94"
PI_PORT = 8092
PI_BASE = "http://{}:{}".format(PI_HOST, PI_PORT)

ARTIFACT_PATH = (
    Path(__file__).resolve().parent
    / "wp2_t1_temp_fsync_artifact.json"
)


print("WP2_T1_CRASH_SPEND_START")


with urllib.request.urlopen(
    PI_BASE + "/provider-status",
    timeout=5,
) as response:
    provider_status = json.loads(
        response.read().decode("utf-8")
    )


provider_offline = (
    provider_status.get("provider_available") is False
)

print(
    "PROVIDER_STATUS available={} result={}".format(
        provider_status.get("provider_available"),
        "PASS" if provider_offline else "FAIL",
    )
)

if not provider_offline:
    raise RuntimeError(
        "Provider must be offline before crash spend"
    )


if not ARTIFACT_PATH.exists():
    raise FileNotFoundError(
        "Missing artifact file: {}".format(ARTIFACT_PATH)
    )


record = json.loads(
    ARTIFACT_PATH.read_text(encoding="utf-8")
)

issue_request = record["issue_request"]
package = record["package"]

artifact = package.get("artifact") or {}
artifact_id = artifact.get("artifact_id")


spend_request = {
    "device_id": issue_request["device_id"],
    "context": issue_request["context"],
    "requested_action": issue_request["requested_action"],
    "nonce": issue_request["nonce"],
}


payload = json.dumps(
    {
        "package": package,
        "spend_request": spend_request,
    },
    sort_keys=True,
    separators=(",", ":"),
).encode("utf-8")


http_request = (
    "POST /spend HTTP/1.1\r\n"
    "Host: {}:{}\r\n"
    "Content-Type: application/json\r\n"
    "Content-Length: {}\r\n"
    "Connection: close\r\n"
    "\r\n"
).format(
    PI_HOST,
    PI_PORT,
    len(payload),
).encode("ascii") + payload


sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM,
)
sock.settimeout(15)


send_completed = False
raw_response = b""
client_error = None

started_ns = time.perf_counter_ns()


try:
    sock.connect((PI_HOST, PI_PORT))
    sock.sendall(http_request)
    send_completed = True

    chunks = []

    while True:
        chunk = sock.recv(4096)

        if not chunk:
            break

        chunks.append(chunk)

    raw_response = b"".join(chunks)

except Exception as exc:
    client_error = repr(exc)

finally:
    finished_ns = time.perf_counter_ns()
    sock.close()


elapsed_ms = (
    finished_ns - started_ns
) / 1_000_000


valid_http_response = (
    b"\r\n\r\n" in raw_response
)

artifact_preserved = ARTIFACT_PATH.exists()

artifact_hash = (
    hashlib.sha256(
        ARTIFACT_PATH.read_bytes()
    ).hexdigest()
    if artifact_preserved
    else None
)


phase_pass = (
    provider_offline
    and send_completed
    and not valid_http_response
    and artifact_preserved
)


print("artifact_id={}".format(artifact_id))
print("send_completed={}".format(send_completed))
print("elapsed_ms={:.3f}".format(elapsed_ms))
print("response_bytes={}".format(len(raw_response)))
print(
    "valid_http_response={}".format(
        valid_http_response
    )
)
print("client_error={}".format(client_error))
print(
    "artifact_file_preserved={}".format(
        artifact_preserved
    )
)
print("artifact_sha256={}".format(artifact_hash))
print(
    "client_phase_result={}".format(
        "EXPECTED_CRASH_NO_RESPONSE"
        if phase_pass
        else "FAIL"
    )
)
print("WP2_T1_CRASH_SPEND_END")


if not phase_pass:
    raise SystemExit(1)
