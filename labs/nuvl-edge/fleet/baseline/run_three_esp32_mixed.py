#!/usr/bin/env python3
import json
import time
import urllib.request

COORD_BASE = "http://192.168.8.234:19052"

ENDPOINTS = {
    "esp32-field-01": "192.168.8.215",
    "esp32-s3-02": "192.168.8.188",
    "esp32-s3-03": "192.168.8.236",
}

RUN_TIMEOUT_S = 15


def request_json(method, path, payload=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        COORD_BASE + path,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


run_id = "{:x}".format(time.time_ns())

print("MULTI_ENDPOINT_POLL_RUN_START")
print("run_id=", run_id)
print("physical_endpoints=", len(ENDPOINTS))

start = request_json(
    "POST",
    "/start",
    {
        "run_id": run_id,
        "delay_ms": 1800,
        "modes": {
            "esp32-field-01": "accept",
            "esp32-s3-02": "deny",
            "esp32-s3-03": "deny_stale_replay",
        },
    },
)

print(
    "COORDINATOR status={} devices={} not_before_ms={}".format(
        start.get("status"),
        start.get("devices"),
        start.get("not_before_ms"),
    )
)

deadline = time.monotonic() + RUN_TIMEOUT_S
results = {}

while time.monotonic() < deadline:
    summary = request_json("GET", "/summary?run_id={}".format(run_id))
    results = summary.get("results") or {}
    if len(results) >= len(ENDPOINTS):
        break
    time.sleep(0.25)

accepted = 0
denied = 0
unavailable = 0
identity_or_ip_mismatch = 0
elapsed_values = []

for device_id, expected_ip in ENDPOINTS.items():
    result = results.get(device_id)

    if result is None:
        unavailable += 1
        print("ENDPOINT device_id={} result=MISSING".format(device_id))
        continue

    if result.get("device_id") != device_id or result.get("ip") != expected_ip:
        identity_or_ip_mismatch += 1

    decision = result.get("decision")

    if decision == "accepted":
        accepted += 1
    elif decision == "denied":
        denied += 1
    else:
        unavailable += 1

    if isinstance(result.get("elapsed_ms"), int):
        elapsed_values.append(result["elapsed_ms"])

    print(
        "ENDPOINT device_id={} ip={} decision={} reason={} "
        "elapsed_ms={} free_delta={}".format(
            device_id,
            result.get("ip"),
            decision,
            result.get("reason"),
            result.get("elapsed_ms"),
            result.get("free_delta"),
        )
    )

elapsed_range_ms = (
    max(elapsed_values) - min(elapsed_values)
    if len(elapsed_values) == len(ENDPOINTS)
    else None
)

expected_outcomes = {
    "esp32-field-01": ("accepted", "provider_admissible"),
    "esp32-s3-02": ("denied", "unauthorized_request"),
    "esp32-s3-03": ("denied", "stale_replay_malformed"),
}

outcomes_match = all(
    results.get(device_id, {}).get("decision") == expected_decision
    and results.get(device_id, {}).get("reason") == expected_reason
    for device_id, (expected_decision, expected_reason) in expected_outcomes.items()
)

LATENCY_BUDGET_MS = 250

stragglers = {
    device_id: results[device_id].get("elapsed_ms")
    for device_id in ENDPOINTS
    if isinstance(results.get(device_id, {}).get("elapsed_ms"), int)
    and results[device_id]["elapsed_ms"] > LATENCY_BUDGET_MS
}

base_valid = (
    len(results) == len(ENDPOINTS)
    and outcomes_match
    and unavailable == 0
    and identity_or_ip_mismatch == 0
)

status = "FAIL"
if base_valid:
    status = "PASS_DEGRADED" if stragglers else "PASS"


print("MULTI_ENDPOINT_POLL_RUN_SUMMARY")
print("physical_endpoints=", len(ENDPOINTS))
print("responses=", len(results))
print("accepted=", accepted)
print("denied=", denied)
print("unavailable=", unavailable)
print("identity_or_ip_mismatch=", identity_or_ip_mismatch)
print("endpoint_elapsed_range_ms=", elapsed_range_ms)
print("latency_budget_ms=", LATENCY_BUDGET_MS)
print("stragglers=", stragglers if stragglers else "none")
print("result=", status)
print("MULTI_ENDPOINT_POLL_RUN_END")

if status == "FAIL":
    raise SystemExit(1)
