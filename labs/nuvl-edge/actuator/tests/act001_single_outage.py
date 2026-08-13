#!/usr/bin/env python3

import json
import time
import urllib.request


COORD_BASE = "http://192.168.0.94:19052"

DEVICE_ID = "esp32-xiao-servo-01"
EXPECTED_IP = "192.168.0.81"

RUN_TIMEOUT_S = 15
LATE_RESULT_GRACE_S = 3
LATENCY_BUDGET_MS = 250


def request_json(method, path, payload=None):
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        COORD_BASE + path,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


run_id = "{:x}".format(time.time_ns())

print("XIAO_SERVO_OUTAGE_RUN_START")
print("run_id=", run_id)
print("device_id=", DEVICE_ID)
print("expected_ip=", EXPECTED_IP)
print("latency_budget_ms=", LATENCY_BUDGET_MS)


start = request_json(
    "POST",
    "/start",
    {
        "run_id": run_id,
        "delay_ms": 1800,
        "modes": {
            DEVICE_ID: "accept",
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
result = None
on_time = False

while time.monotonic() < deadline:
    summary = request_json(
        "GET",
        "/summary?run_id={}".format(run_id),
    )

    results = summary.get("results") or {}

    if DEVICE_ID in results:
        result = results[DEVICE_ID]
        on_time = True
        break

    time.sleep(0.25)


if result is None:
    grace_deadline = time.monotonic() + LATE_RESULT_GRACE_S

    while time.monotonic() < grace_deadline:
        summary = request_json(
            "GET",
            "/summary?run_id={}".format(run_id),
        )

        results = summary.get("results") or {}

        if DEVICE_ID in results:
            result = results[DEVICE_ID]
            break

        time.sleep(0.25)


if result is None:
    print("ENDPOINT result=MISSING")
    print("result=FAIL")
    print("XIAO_SERVO_OUTAGE_RUN_END")
    raise SystemExit(1)


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
    actual_device_id == DEVICE_ID
    and actual_ip == EXPECTED_IP
)

outcome_match = (
    decision == "unavailable"
    and isinstance(reason, str)
    and bool(reason.strip())
)

actuator_match = (
    actuator_attempted is False
    and actuator_command_completed is False
    and actuator_error is None
)

latency_valid = isinstance(elapsed_ms, int)

latency_within_budget = (
    latency_valid
    and elapsed_ms <= LATENCY_BUDGET_MS
)


print(
    "ENDPOINT device_id={} actual_device_id={} "
    "expected_ip={} actual_ip={} "
    "decision={} reason={} "
    "identity_ip_match={} "
    "arrival_status={} elapsed_ms={} "
    "actuator_attempted={} "
    "actuator_command_completed={} "
    "actuator_error={}".format(
        DEVICE_ID,
        actual_device_id,
        EXPECTED_IP,
        actual_ip,
        decision,
        reason,
        identity_ip_match,
        "ON_TIME" if on_time else "LATE",
        elapsed_ms,
        actuator_attempted,
        actuator_command_completed,
        actuator_error,
    )
)


passed = (
    identity_ip_match
    and outcome_match
    and actuator_match
    and on_time
    and latency_valid
)


if not passed:
    status = "FAIL"
elif latency_within_budget:
    status = "PASS"
else:
    status = "PASS_DEGRADED"


print("XIAO_SERVO_OUTAGE_RUN_SUMMARY")
print("identity_ip_match=", identity_ip_match)
print("outcome_match=", outcome_match)
print("actuator_match=", actuator_match)
print("on_time=", on_time)
print("elapsed_ms=", elapsed_ms)
print("latency_within_budget=", latency_within_budget)
print("result=", status)
print("XIAO_SERVO_OUTAGE_RUN_END")


if status == "FAIL":
    raise SystemExit(1)

