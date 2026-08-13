#!/usr/bin/env python3

import json
import time
import urllib.request

COORD_BASE = "http://192.168.0.94:19052"

ENDPOINTS = {
    "esp32-xiao-servo-01": {
        "ip": "192.168.0.81",
        "mode": "deny",
        "decision": "denied",
        "reason": "unauthorized_request",
        "actuator_attempted": False,
        "actuator_command_completed": False,
    },
    "esp32-xiao-servo-02": {
        "ip": "192.168.0.186",
        "mode": "accept",
        "decision": "accepted",
        "reason": "provider_admissible",
        "actuator_attempted": True,
        "actuator_command_completed": True,
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

print("ACT002_MIXED_B_RUN_START")
print("run_id=", run_id)
print("physical_endpoints=", len(ENDPOINTS))
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
on_time_device_ids = set()

while time.monotonic() < deadline:
    summary = request_json(
        "GET",
        "/summary?run_id={}".format(run_id),
    )

    results = summary.get("results") or {}

    for device_id in ENDPOINTS:
        if device_id in results:
            on_time_device_ids.add(device_id)

    if all(device_id in results for device_id in ENDPOINTS):
        break

    time.sleep(0.25)

if not all(device_id in results for device_id in ENDPOINTS):
    grace_deadline = time.monotonic() + LATE_RESULT_GRACE_S

    while time.monotonic() < grace_deadline:
        summary = request_json(
            "GET",
            "/summary?run_id={}".format(run_id),
        )

        results = summary.get("results") or {}

        if all(device_id in results for device_id in ENDPOINTS):
            break

        time.sleep(0.25)

unexpected_result_keys = sorted(set(results) - set(ENDPOINTS))

all_valid = True
any_degraded = False

for device_id, contract in ENDPOINTS.items():
    result = results.get(device_id)

    if result is None:
        print(
            "ENDPOINT device_id={} result=MISSING".format(
                device_id
            )
        )
        all_valid = False
        continue

    actual_device_id = result.get("device_id")
    actual_ip = result.get("ip")
    decision = result.get("decision")
    reason = result.get("reason")
    elapsed_ms = result.get("elapsed_ms")

    actuator_attempted = result.get("actuator_attempted")
    actuator_command_completed = result.get(
        "actuator_command_completed"
    )
    actuator_error = result.get("actuator_error")

    identity_ip_match = (
        actual_device_id == device_id
        and actual_ip == contract["ip"]
    )

    outcome_match = (
        decision == contract["decision"]
        and reason == contract["reason"]
    )

    actuator_match = (
        actuator_attempted is contract["actuator_attempted"]
        and actuator_command_completed
            is contract["actuator_command_completed"]
        and actuator_error is None
    )

    on_time = device_id in on_time_device_ids
    latency_valid = isinstance(elapsed_ms, int)
    latency_within_budget = (
        latency_valid
        and elapsed_ms <= LATENCY_BUDGET_MS
    )

    endpoint_valid = (
        identity_ip_match
        and outcome_match
        and actuator_match
        and on_time
        and latency_valid
    )

    if not endpoint_valid:
        all_valid = False
    elif not latency_within_budget:
        any_degraded = True

    print(
        "ENDPOINT device_id={} actual_device_id={} "
        "expected_ip={} actual_ip={} "
        "expected_mode={} decision={} reason={} "
        "identity_ip_match={} outcome_match={} "
        "arrival_status={} elapsed_ms={} "
        "latency_within_budget={} "
        "actuator_attempted={} "
        "actuator_command_completed={} "
        "actuator_error={} actuator_match={}".format(
            device_id,
            actual_device_id,
            contract["ip"],
            actual_ip,
            contract["mode"],
            decision,
            reason,
            identity_ip_match,
            outcome_match,
            "ON_TIME" if on_time else "LATE",
            elapsed_ms,
            latency_within_budget,
            actuator_attempted,
            actuator_command_completed,
            actuator_error,
            actuator_match,
        )
    )

if unexpected_result_keys:
    all_valid = False

if not all_valid:
    status = "FAIL"
elif any_degraded:
    status = "PASS_DEGRADED"
else:
    status = "PASS"

print("ACT002_MIXED_B_RUN_SUMMARY")
print(
    "expected_physical_behavior="
    "servo-01=NO_MOVE servo-02=MOVE"
)
print(
    "unexpected_result_keys=",
    unexpected_result_keys if unexpected_result_keys else "none",
)
print("result=", status)
print("ACT002_MIXED_B_RUN_END")

if status == "FAIL":
    raise SystemExit(1)

