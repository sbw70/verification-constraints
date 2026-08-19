#!/usr/bin/env python3

import json
import time
import urllib.request

COORD_BASE = "http://192.168.0.94:19052"

ENDPOINTS = {
    "esp32-field-01": {
        "ip": "192.168.0.39",
        "mode": "accept",
        "decision": "accepted",
        "reason": "provider_admissible",
        "physical_effector": False,
    },
    "esp32-s3-02": {
        "ip": "192.168.0.114",
        "mode": "accept",
        "decision": "accepted",
        "reason": "provider_admissible",
        "physical_effector": False,
    },
    "esp32-s3-03": {
        "ip": "192.168.0.216",
        "mode": "accept",
        "decision": "accepted",
        "reason": "provider_admissible",
        "physical_effector": False,
    },
    "esp32-xiao-servo-01": {
        "ip": "192.168.0.81",
        "mode": "accept",
        "decision": "accepted",
        "reason": "provider_admissible",
        "physical_effector": True,
        "actuator_attempted": True,
        "actuator_command_completed": True,
    },
    "esp32-xiao-servo-02": {
        "ip": "192.168.0.186",
        "mode": "accept",
        "decision": "accepted",
        "reason": "provider_admissible",
        "physical_effector": True,
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

print("FIVE_ENDPOINT_ACCEPT_RUN_START")
print("run_id=", run_id)
print("physical_endpoints=", len(ENDPOINTS))
print("devkit_endpoints=3")
print("physical_effector_endpoints=2")
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


# Brief grace period to distinguish LATE from MISSING.
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

accepted = 0
denied = 0
unavailable = 0
missing = 0
identity_or_ip_mismatch = 0
outcome_mismatch = 0
actuator_mismatch = 0
latency_missing = 0

elapsed_values = []
stragglers = {}
late_device_ids = set()

all_valid = True
any_degraded = False


for device_id, contract in ENDPOINTS.items():
    result = results.get(device_id)

    if result is None:
        missing += 1
        all_valid = False

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

    actual_device_id = result.get("device_id")
    actual_ip = result.get("ip")
    decision = result.get("decision")
    reason = result.get("reason")
    elapsed_ms = result.get("elapsed_ms")

    identity_ip_match = (
        actual_device_id == device_id
        and actual_ip == contract["ip"]
    )

    outcome_match = (
        decision == contract["decision"]
        and reason == contract["reason"]
    )

    if not identity_ip_match:
        identity_or_ip_mismatch += 1
        all_valid = False

    if not outcome_match:
        outcome_mismatch += 1
        all_valid = False

    if decision == "accepted":
        accepted += 1
    elif decision == "denied":
        denied += 1
    else:
        unavailable += 1

    on_time = device_id in on_time_device_ids

    if not on_time:
        late_device_ids.add(device_id)
        all_valid = False

    latency_valid = isinstance(elapsed_ms, int)

    if latency_valid:
        elapsed_values.append(elapsed_ms)

        if elapsed_ms > LATENCY_BUDGET_MS:
            stragglers[device_id] = elapsed_ms
            any_degraded = True
    else:
        latency_missing += 1
        all_valid = False

    if contract["physical_effector"]:
        actuator_attempted = result.get("actuator_attempted")
        actuator_command_completed = result.get(
            "actuator_command_completed"
        )
        actuator_error = result.get("actuator_error")

        actuator_match = (
            actuator_attempted is contract["actuator_attempted"]
            and actuator_command_completed
                is contract["actuator_command_completed"]
            and actuator_error is None
        )

        if not actuator_match:
            actuator_mismatch += 1
            all_valid = False

        print(
            "ENDPOINT device_id={} actual_device_id={} "
            "expected_ip={} actual_ip={} "
            "expected_mode={} decision={} reason={} "
            "identity_ip_match={} outcome_match={} "
            "arrival_status={} elapsed_ms={} "
            "latency_status={} "
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
                (
                    "UNMEASURED"
                    if not latency_valid
                    else (
                        "OVER_BUDGET"
                        if elapsed_ms > LATENCY_BUDGET_MS
                        else "WITHIN_BUDGET"
                    )
                ),
                actuator_attempted,
                actuator_command_completed,
                actuator_error,
                actuator_match,
            )
        )

    else:
        print(
            "ENDPOINT device_id={} actual_device_id={} "
            "expected_ip={} actual_ip={} "
            "expected_mode={} decision={} reason={} "
            "identity_ip_match={} outcome_match={} "
            "arrival_status={} elapsed_ms={} "
            "latency_status={} free_delta={}".format(
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
                (
                    "UNMEASURED"
                    if not latency_valid
                    else (
                        "OVER_BUDGET"
                        if elapsed_ms > LATENCY_BUDGET_MS
                        else "WITHIN_BUDGET"
                    )
                ),
                result.get("free_delta"),
            )
        )


if unexpected_result_keys:
    all_valid = False


elapsed_range_ms = (
    max(elapsed_values) - min(elapsed_values)
    if len(elapsed_values) == len(ENDPOINTS)
    else None
)


if not all_valid:
    status = "FAIL"
elif any_degraded:
    status = "PASS_DEGRADED"
else:
    status = "PASS"


print("FIVE_ENDPOINT_ACCEPT_RUN_SUMMARY")
print("physical_endpoints=", len(ENDPOINTS))
print("responses=", len(results))
print("accepted=", accepted)
print("denied=", denied)
print("unavailable=", unavailable)
print("missing=", missing)
print("identity_or_ip_mismatch=", identity_or_ip_mismatch)
print("outcome_mismatch=", outcome_mismatch)
print("actuator_mismatch=", actuator_mismatch)
print("latency_missing=", latency_missing)
print("endpoint_elapsed_range_ms=", elapsed_range_ms)
print("latency_budget_ms=", LATENCY_BUDGET_MS)
print(
    "stragglers=",
    stragglers if stragglers else "none",
)
print(
    "late_results=",
    sorted(late_device_ids) if late_device_ids else "none",
)
print(
    "unexpected_result_keys=",
    unexpected_result_keys if unexpected_result_keys else "none",
)
print(
    "expected_physical_behavior="
    "servo-01=MOVE servo-02=MOVE"
)
print("result=", status)
print("FIVE_ENDPOINT_ACCEPT_RUN_END")

if status == "FAIL":
    raise SystemExit(1)
