#!/usr/bin/env python3
import json
import time
import urllib.request

COORD_BASE = "YOUR PI IP:19052"

ENDPOINTS = {
    "esp32-field-01": {
        "ip": "192.168.8.215",
        "mode": "accept",
        "decision": "accepted",
        "reason": "provider_admissible",
    },
    "esp32-s3-02": {
        "ip": "192.168.8.188",
        "mode": "accept",
        "decision": "accepted",
        "reason": "provider_admissible",
    },
    "esp32-s3-03": {
        "ip": "192.168.8.236",
        "mode": "accept",
        "decision": "accepted",
        "reason": "provider_admissible",
    },
}

RUN_TIMEOUT_S = 15
LATE_RESULT_GRACE_S = 3
LATENCY_BUDGET_MS = 250


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
print("run_timeout_s=", RUN_TIMEOUT_S)
print("late_result_grace_s=", LATE_RESULT_GRACE_S)
print("latency_budget_ms=", LATENCY_BUDGET_MS)

start = request_json(
    "POST",
    "/start",
    {
        "run_id": run_id,
        "delay_ms": 1800,
        "modes": {
            device_id: contract["mode"]
            for device_id, contract in ENDPOINTS.items()
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

    if all(device_id in results for device_id in ENDPOINTS):
        break

    time.sleep(0.25)

on_time_device_ids = {
    device_id for device_id in ENDPOINTS if device_id in results
}

# If an expected endpoint missed the main collection deadline, briefly
# continue observing so a late result can be distinguished from no result.
if len(on_time_device_ids) < len(ENDPOINTS):
    grace_deadline = time.monotonic() + LATE_RESULT_GRACE_S

    while time.monotonic() < grace_deadline:
        summary = request_json("GET", "/summary?run_id={}".format(run_id))
        results = summary.get("results") or {}

        if all(device_id in results for device_id in ENDPOINTS):
            break

        time.sleep(0.25)

late_device_ids = {
    device_id
    for device_id in ENDPOINTS
    if device_id in results and device_id not in on_time_device_ids
}

unexpected_result_keys = sorted(set(results) - set(ENDPOINTS))

accepted = 0
denied = 0
unavailable = 0
missing = 0
identity_or_ip_mismatch = 0
outcome_mismatch = 0
latency_missing = 0
elapsed_values = []
stragglers = {}

for device_id, contract in ENDPOINTS.items():
    result = results.get(device_id)

    if result is None:
        missing += 1
        print(
            "ENDPOINT device_id={} result=MISSING "
            "expected_ip={} expected_decision={} expected_reason={}".format(
                device_id,
                contract["ip"],
                contract["decision"],
                contract["reason"],
            )
        )
        continue

    actual_ip = result.get("ip")
    actual_device_id = result.get("device_id")
    decision = result.get("decision")
    reason = result.get("reason")
    elapsed_ms = result.get("elapsed_ms")

    identity_ip_match = (
        actual_device_id == device_id and actual_ip == contract["ip"]
    )

    expected_outcome_match = (
        decision == contract["decision"] and reason == contract["reason"]
    )

    if not identity_ip_match:
        identity_or_ip_mismatch += 1

    if not expected_outcome_match:
        outcome_mismatch += 1

    if decision == "accepted":
        accepted += 1
    elif decision == "denied":
        denied += 1
    else:
        unavailable += 1

    if isinstance(elapsed_ms, int):
        elapsed_values.append(elapsed_ms)

        if elapsed_ms > LATENCY_BUDGET_MS:
            stragglers[device_id] = elapsed_ms
    else:
        latency_missing += 1

    if device_id in late_device_ids:
        arrival_status = "LATE"
    else:
        arrival_status = "ON_TIME"

    if not isinstance(elapsed_ms, int):
        latency_status = "UNMEASURED"
    elif elapsed_ms > LATENCY_BUDGET_MS:
        latency_status = "OVER_BUDGET"
    else:
        latency_status = "WITHIN_BUDGET"

    print(
        "ENDPOINT device_id={} actual_device_id={} "
        "expected_ip={} actual_ip={} "
        "expected_decision={} actual_decision={} "
        "expected_reason={} actual_reason={} "
        "identity_ip_match={} outcome_match={} "
        "arrival_status={} elapsed_ms={} latency_status={} "
        "free_delta={}".format(
            device_id,
            actual_device_id,
            contract["ip"],
            actual_ip,
            contract["decision"],
            decision,
            contract["reason"],
            reason,
            identity_ip_match,
            expected_outcome_match,
            arrival_status,
            elapsed_ms,
            latency_status,
            result.get("free_delta"),
        )
    )

elapsed_range_ms = (
    max(elapsed_values) - min(elapsed_values)
    if len(elapsed_values) == len(ENDPOINTS)
    else None
)

all_expected_results_present = all(
    device_id in results for device_id in ENDPOINTS
)

base_valid = (
    all_expected_results_present
    and not unexpected_result_keys
    and missing == 0
    and unavailable == 0
    and identity_or_ip_mismatch == 0
    and outcome_mismatch == 0
    and latency_missing == 0
    and not late_device_ids
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
print("missing=", missing)
print("identity_or_ip_mismatch=", identity_or_ip_mismatch)
print("outcome_mismatch=", outcome_mismatch)
print("latency_missing=", latency_missing)
print("endpoint_elapsed_range_ms=", elapsed_range_ms)
print("latency_budget_ms=", LATENCY_BUDGET_MS)
print("stragglers=", stragglers if stragglers else "none")
print(
    "late_results=",
    sorted(late_device_ids) if late_device_ids else "none",
)
print(
    "unexpected_result_keys=",
    unexpected_result_keys if unexpected_result_keys else "none",
)
print("result=", status)
print("MULTI_ENDPOINT_POLL_RUN_END")

if status == "FAIL":
    raise SystemExit(1)
