#!/usr/bin/env python3
import json
import socket
import threading
import time
import urllib.request
from pathlib import Path

PI_HOST = "192.168.8.234"
PI_PORT = 8089
PI_BASE = "http://{}:{}".format(PI_HOST, PI_PORT)
ARTIFACT_PATH = Path(__file__).resolve().parent / "poc005_race_artifact.json"

print("POC005_CONCURRENT_DOUBLE_SPEND_START")

with urllib.request.urlopen(PI_BASE + "/provider-status", timeout=5) as response:
    provider_status = json.loads(response.read().decode("utf-8"))

provider_offline = provider_status.get("provider_available") is False
print(
    "PROVIDER_STATUS available={} result={}".format(
        provider_status.get("provider_available"),
        "PASS" if provider_offline else "FAIL",
    )
)

if not provider_offline:
    raise RuntimeError("Provider must be offline")

record = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
issue_request = record["issue_request"]
package = record["package"]

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
).format(PI_HOST, PI_PORT, len(payload)).encode("ascii") + payload

barrier = threading.Barrier(3)
results = {}
lock = threading.Lock()


def parse_http(raw):
    marker = raw.find(b"\r\n\r\n")
    if marker < 0:
        raise ValueError("invalid_http_response")
    return json.loads(raw[marker + 4:].decode("utf-8"))


def worker(name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15)
    try:
        sock.connect((PI_HOST, PI_PORT))
        barrier.wait(timeout=10)

        started_ns = time.perf_counter_ns()
        sock.sendall(http_request)

        chunks = []
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)

        finished_ns = time.perf_counter_ns()
        response = parse_http(b"".join(chunks))

        with lock:
            results[name] = {
                "started_ns": started_ns,
                "finished_ns": finished_ns,
                "elapsed_ms": (finished_ns - started_ns) / 1_000_000,
                "response": response,
            }
    except Exception as exc:
        with lock:
            results[name] = {
                "error": repr(exc),
            }
    finally:
        sock.close()


threads = [
    threading.Thread(target=worker, args=("client_1",)),
    threading.Thread(target=worker, args=("client_2",)),
]

for thread in threads:
    thread.start()

barrier.wait(timeout=10)

for thread in threads:
    thread.join(timeout=20)

if len(results) != 2:
    raise RuntimeError("missing_worker_result")

responses = []
start_times = []

for name in ("client_1", "client_2"):
    item = results[name]

    if "error" in item:
        print("CLIENT name={} error={} result=FAIL".format(name, item["error"]))
        continue

    response = item["response"]
    responses.append(response)
    start_times.append(item["started_ns"])

    print(
        "CLIENT name={} decision={} reason={} verified={} "
        "provider_contacted={} elapsed_ms={:.3f}".format(
            name,
            response.get("decision"),
            response.get("reason"),
            response.get("provider_verified"),
            response.get("provider_contacted_for_spend"),
            item["elapsed_ms"],
        )
    )

accepted = [
    response for response in responses
    if response.get("decision") == "accepted"
    and response.get("reason") == "offline_artifact_admissible"
    and response.get("provider_verified") is True
    and response.get("provider_contacted_for_spend") is False
    and response.get("replay_state_persisted_before_accept") is True
]

replayed = [
    response for response in responses
    if response.get("decision") == "denied"
    and response.get("reason") == "replay_detected"
    and response.get("provider_verified") is True
    and response.get("provider_contacted_for_spend") is False
]

artifact_ids = {
    response.get("artifact_id")
    for response in responses
    if response.get("artifact_id")
}

send_start_skew_us = (
    abs(start_times[0] - start_times[1]) / 1_000
    if len(start_times) == 2
    else None
)

passed = (
    len(responses) == 2
    and len(accepted) == 1
    and len(replayed) == 1
    and len(artifact_ids) == 1
)

artifact_file_removed = False
if passed:
    ARTIFACT_PATH.unlink()
    artifact_file_removed = True

print("POC005_CONCURRENT_DOUBLE_SPEND_SUMMARY")
print("connected_clients=", 2)
print("responses=", len(responses))
print("accepted=", len(accepted))
print("replay_denied=", len(replayed))
print("unique_artifact_ids=", len(artifact_ids))
print("send_start_skew_us=", "{:.3f}".format(send_start_skew_us) if send_start_skew_us is not None else None)
print("provider_unavailable_confirmed=", provider_offline)
print("provider_contacted_for_spend=", False)
print("exactly_one_accept=", len(accepted) == 1)
print("exactly_one_replay_denial=", len(replayed) == 1)
print("artifact_file_removed=", artifact_file_removed)
print("result=", "PASS" if passed else "FAIL")
print("POC005_CONCURRENT_DOUBLE_SPEND_END")

if not passed:
    raise SystemExit(1)
