import gc
import json
import os
import socket

PI_IP = "YOUR PI IP"
PORT = 8089
ARTIFACT_FILE = "poc003_artifacts.json"


def send_all(sock, data):
    offset = 0
    while offset < len(data):
        sent = sock.send(data[offset:])
        if sent is None:
            sent = 0
        if sent <= 0:
            raise OSError("socket_send_failed")
        offset += sent


def http_json(method, path, payload=None, timeout=12):
    body = b"" if payload is None else json.dumps(payload).encode()
    request = (
        "{} {} HTTP/1.1\r\n"
        "Host: {}\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).format(method, path, PI_IP, len(body)).encode() + body

    s = socket.socket()
    s.settimeout(timeout)

    try:
        s.connect((PI_IP, PORT))
        send_all(s, request)

        chunks = []
        while True:
            chunk = s.recv(512)
            if not chunk:
                break
            chunks.append(chunk)

        raw = b"".join(chunks)
        marker = raw.find(b"\r\n\r\n")
        if marker < 0:
            raise ValueError(
                "invalid_http_response len={} head={!r}".format(
                    len(raw), raw[:120]
                )
            )

        return json.loads(raw[marker + 4:].decode())
    finally:
        try:
            s.close()
        except Exception:
            pass


def primary_case():
    with open(ARTIFACT_FILE, "r") as f:
        artifacts = json.load(f)

    entry = artifacts["primary"]
    src = entry["issue_request"]

    return entry["package"], {
        "device_id": src["device_id"],
        "context": src["context"],
        "requested_action": src["requested_action"],
        "nonce": src["nonce"],
    }


print("POC004_REPLAY_AFTER_RESTART_START")
gc.collect()
baseline_free = gc.mem_free()

provider_status = http_json("GET", "/provider-status")
provider_offline = provider_status.get("provider_available") is False
print(
    "PROVIDER_STATUS available={} result={}".format(
        provider_status.get("provider_available"),
        "PASS" if provider_offline else "FAIL",
    )
)

if not provider_offline:
    raise RuntimeError("Provider must remain offline")

health = http_json("GET", "/health")
state_loaded = (
    health.get("replay_state_persistent") is True
    and int(health.get("spent_count", 0)) >= 1
)

print(
    "BOUNDARY_HEALTH persistent={} spent_count={} result={}".format(
        health.get("replay_state_persistent"),
        health.get("spent_count"),
        "PASS" if state_loaded else "FAIL",
    )
)

package, spend_request = primary_case()
response = http_json(
    "POST",
    "/spend",
    {"package": package, "spend_request": spend_request},
)

passed = (
    state_loaded
    and response.get("decision") == "denied"
    and response.get("reason") == "replay_detected"
    and response.get("provider_verified") is True
    and response.get("provider_contacted_for_spend") is False
)

artifact_file_removed = False
if passed:
    try:
        os.remove(ARTIFACT_FILE)
        artifact_file_removed = True
    except Exception:
        artifact_file_removed = False

gc.collect()
final_free = gc.mem_free()

print(
    "REPLAY expected=denied/replay_detected/True "
    "actual={}/{}/{} provider_contacted={} result={}".format(
        response.get("decision"),
        response.get("reason"),
        response.get("provider_verified"),
        response.get("provider_contacted_for_spend"),
        "PASS" if passed else "FAIL",
    )
)
print("artifact_id=", response.get("artifact_id"))
print("persistent_replay_after_restart=", passed)
print("artifact_file_removed=", artifact_file_removed)
print("baseline_free=", baseline_free)
print("final_free=", final_free)
print("free_delta=", final_free - baseline_free)
print("POC004_REPLAY_AFTER_RESTART_END")
