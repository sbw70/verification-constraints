# ACT-005 — Dual-Effector Shared-Boundary Outage and Recovery

## Status

**PASS**

ACT-005 validated shared-boundary loss and recovery across two physical actuator endpoints.

Both XIAO ESP32-S3 endpoints requested the accepted path while their shared external NUVL boundary was deliberately unavailable.

Both endpoints returned unavailable outcomes. Neither endpoint entered its actuator path, and neither physical servo moved.

The external boundary was then restored without resetting either XIAO endpoint. Two subsequent dual-accept recovery runs produced accepted results and observable physical movement at both servos.

---

## Test Classification

ACT-005 is an **optional physical-effector integration of the existing NUVL architecture**, not an architecture change.

It maps to the multi-effector availability / fail-unavailable use case.

The property supported by ACT-005 is:

> In the tested two-endpoint path, loss of the shared external authorization boundary prevented physical actuation at both endpoints, and admissible physical execution resumed after boundary restoration without endpoint resets.

ACT-005 does not establish behavior under every degraded-network condition, exactly-once physical execution, persistent physical replay protection, or deterministic recovery timing.

---

## Test Configuration

Physical endpoints:

* `esp32-xiao-servo-01`
* `esp32-xiao-servo-02`

Hardware:

* 2 × Seeed XIAO ESP32-S3
* 2 × MG90S-class servos
* Servo signal: D4 / GPIO5
* Same qualified actuator firmware on both endpoints
* Distinct endpoint identities through `device_id.txt`

Observed IPs during testing:

`esp32-xiao-servo-01 → 192.168.0.81`

`esp32-xiao-servo-02 → 192.168.0.186`

Shared external NUVL boundary:

`192.168.0.75:8089`

Latency budget:

`250 ms`

---

## Qualified Firmware

Original tested actuator firmware:

`esp32_xiao_servo_nuvl_archer.py`

Size:

`9,790 bytes`

SHA-256:

`C29AD7BB8362BD532C62A87CE5D8BE3ED30C25E4543FF52A2CC98992E493AD84`

The same firmware hash was verified on both actuator endpoints.

---

# Phase 1 — Shared-Boundary Outage

## Objective

Determine whether either physical endpoint would actuate when both requested the accept path but the shared external NUVL boundary was unavailable.

The critical condition was:

```text
servo-01 → request accept
servo-02 → request accept
shared NUVL boundary → unavailable
```

Expected physical result:

```text
servo-01 → NO MOVE
servo-02 → NO MOVE
```

This was specifically a test of boundary unavailability.

It was not a denial test.

---

## Boundary Shutdown

The normal Pi boundary process was identified as:

```text
python3 /home/seth/nuvl_local_hardened_latency.py
```

PID:

`2730624`

The process was terminated.

Port 8089 was then checked locally.

Observed:

```text
curl: (7) Failed to connect to 127.0.0.1 port 8089
```

This confirmed that the shared external boundary was unavailable before the physical actuator test was executed.

The XIAO endpoints were not reset.

---

# Outage Test Contract

Both endpoints were assigned:

`accept`

Because the external authorization boundary was unavailable, PASS required each endpoint to report an unavailable result rather than entering the physical execution path.

Expected software actuator state:

```text
actuator_attempted=False
actuator_command_completed=False
actuator_error=None
```

Expected physical result:

```text
NO MOVE / NO MOVE
```

PASS additionally required:

* correct endpoint identity
* correct IP binding
* non-empty unavailable reason
* both results ON_TIME
* no unexpected result keys

---

# Outage Execution

Run ID:

`18ca521127d5f1ac`

## Servo 01

Endpoint:

`esp32-xiao-servo-01`

Expected mode:

`accept`

Observed:

* decision: `unavailable`
* reason: `OSError(104,)`
* latency: `13 ms`
* identity/IP binding correct
* `actuator_attempted=False`
* `actuator_command_completed=False`
* `actuator_error=None`
* actuator oracle matched
* no physical movement observed

## Servo 02

Endpoint:

`esp32-xiao-servo-02`

Expected mode:

`accept`

Observed:

* decision: `unavailable`
* reason: `OSError(104,)`
* latency: `13 ms`
* identity/IP binding correct
* `actuator_attempted=False`
* `actuator_command_completed=False`
* `actuator_error=None`
* actuator oracle matched
* no physical movement observed

Both endpoint results:

`ON_TIME`

Unexpected result keys:

`none`

Physical result:

`NO MOVE / NO MOVE`

Outage result:

**PASS**

---

# Outage Result Matrix

| Endpoint   | Requested mode | Boundary    | Returned result               | Actuator  | Physical result | Result |
| ---------- | -------------- | ----------- | ----------------------------- | --------- | --------------- | ------ |
| `servo-01` | accept         | unavailable | unavailable / `OSError(104,)` | untouched | NO MOVE         | PASS   |
| `servo-02` | accept         | unavailable | unavailable / `OSError(104,)` | untouched | NO MOVE         | PASS   |

Requested physical actions:

**2**

Authorized physical actions:

**0**

Actuator invocations:

**0**

Observed movements:

**0**

---

# Phase 2 — Shared-Boundary Restoration

## Objective

Determine whether the same two physical endpoints could return to admissible physical execution after restoration of the external boundary.

Neither XIAO endpoint was reset between the outage test and recovery testing.

This distinction is material: recovery was tested by restoring the external dependency rather than rebooting the actuator endpoints into a fresh state.

---

## Boundary Restart

The boundary was restarted with:

```text
python3 /home/seth/nuvl_local_hardened_latency.py
```

New PID:

`2732099`

Restart log:

`/home/seth/nuvl_local_hardened_latency_restart_20260809_225511.log`

Boundary health after restart:

`ok`

SHA-256 of Pi recovery log:

`664E0CCABA1A8E5661405B21118690E9C0035673323CE8520124E724EF7FD666`

---

# Recovery Test Method

ACT-005 did **not** introduce a separate recovery launcher.

The already-qualified ACT-003 dual-accept launcher was deliberately reused:

`run_two_xiao_servo_dual_accept_archer.py`

This avoided creating a duplicate source file for behavior that had already been qualified.

The recovery contract was therefore:

```text
servo-01 → accept → accepted → MOVE
servo-02 → accept → accepted → MOVE
```

Neither XIAO was reset before these runs.

---

# Recovery Run 1

Run ID:

`18ca5244856a83b8`

## Servo 01

Observed:

* decision: `accepted`
* reason: `provider_admissible`
* latency: `40 ms`
* identity/IP binding correct
* actuator command completed
* physical movement observed

## Servo 02

Observed:

* decision: `accepted`
* reason: `provider_admissible`
* latency: `38 ms`
* identity/IP binding correct
* actuator command completed
* physical movement observed

Both endpoint results:

`ON_TIME`

Physical result:

`MOVE / MOVE`

Result:

**PASS**

---

# Recovery Run 2

Run ID:

`18ca52542f653994`

## Servo 01

Observed:

* decision: `accepted`
* reason: `provider_admissible`
* latency: `35 ms`
* identity/IP binding correct
* actuator command completed
* physical movement observed

## Servo 02

Observed:

* decision: `accepted`
* reason: `provider_admissible`
* latency: `33 ms`
* identity/IP binding correct
* actuator command completed
* physical movement observed

Both endpoint results:

`ON_TIME`

Physical result:

`MOVE / MOVE`

Result:

**PASS**

---

# Recovery Result Matrix

| Run ID             | Servo 01 | Servo 02 | Latencies  | Endpoint reset | Physical result | Result |
| ------------------ | -------- | -------- | ---------- | -------------- | --------------- | ------ |
| `18ca5244856a83b8` | accepted | accepted | 40 / 38 ms | No             | MOVE / MOVE     | PASS   |
| `18ca52542f653994` | accepted | accepted | 35 / 33 ms | No             | MOVE / MOVE     | PASS   |

Recovery executions:

**2**

Correct dual physical outcomes:

**2/2**

Endpoint resets:

**0**

---

# Complete ACT-005 Transition

ACT-005 exercised the following state transition:

```text
BOUNDARY AVAILABLE
        ↓
BOUNDARY STOPPED
        ↓
servo-01 requests accept
servo-02 requests accept
        ↓
UNAVAILABLE / UNAVAILABLE
        ↓
NO MOVE / NO MOVE
        ↓
BOUNDARY RESTORED
        ↓
no endpoint reset
        ↓
ACCEPTED / ACCEPTED
        ↓
MOVE / MOVE
```

The observed transition matched the expected behavior.

---

# Source Launcher — Outage

Original source:

`run_two_xiao_servo_dual_outage_archer.py`

Size:

`5,769 bytes`

SHA-256:

`E66D54E33A20216B9E4F4CC1CF806C63B3F0D6A126C5512E46543500A96DCE96`

Contract:

```text
servo-01 → request accept → boundary unavailable → NO MOVE
servo-02 → request accept → boundary unavailable → NO MOVE
```

Compile:

**PASS**

---

# Source Launcher — Recovery

No separate ACT-005 recovery source was created.

Recovery reused:

`run_two_xiao_servo_dual_accept_archer.py`

Original size:

`5,914 bytes`

SHA-256:

`96BECFB0B85801674D5AEEF117A6B86826AF22F4B0EF82306530FBBD07B05137`

This is the same launcher qualified during ACT-003.

---

# Runtime Evidence

## Outage

`act005_dual_outage_20260809_225334.log`

Size:

`2,221 bytes`

SHA-256:

`38C26133BAFBAF3C2F94E0730D08B38F9DC875CFCEB9FBD0718E5F9E3C120720`

Result:

**PASS**

Physical observation:

`NO MOVE / NO MOVE`

---

## Recovery Run 1

`act005_dual_recovery_20260809_225715.log`

Size:

`2,232 bytes`

SHA-256:

`8C476D67A8911B5C3FEC32E1674A2C910EA7D80E4B8F63DF8F8EDEFB7BD0CC8F`

Result:

**PASS**

Physical observation:

`MOVE / MOVE`

---

## Recovery Run 2

`act005_dual_recovery_20260809_225842.log`

Size:

`2,232 bytes`

SHA-256:

`E9F12455C3D494B8B3A023732820B93EAB93562C84CFAE4C41A9A52F9EAD6F0`

Result:

**PASS**

Physical observation:

`MOVE / MOVE`

---

# Pi-Side Recovery Evidence

Restart log:

`/home/seth/nuvl_local_hardened_latency_restart_20260809_225511.log`

SHA-256:

`664E0CCABA1A8E5661405B21118690E9C0035673323CE8520124E724EF7FD666`

The boundary subsequently returned:

`ok`

The two recovery runs then returned accepted outcomes and physical movement without endpoint resets.

---

# Evidence Manifest

Manifest:

`act005_manifest_20260809_230307.txt`

Original path:

`C:\Users\holiw\esp32-main\act005_manifest_20260809_230307.txt`

Size:

`655 bytes`

SHA-256:

`3B8B38F0D29FB0E189C88984202C7E85EF7B2975F20D83FB7921F3522C41AC1E`

The manifest closes the local ACT-005 evidence set.

---

# Supported Conclusion

ACT-005 supports the following bounded conclusion:

> In the tested two-endpoint path, loss of the shared external authorization boundary caused both endpoints to fail unavailable without physical actuation. After boundary restoration, both endpoints resumed admissible physical actuation without endpoint resets.

The outage portion specifically demonstrated:

```text
requested accept + unavailable external boundary
→ unavailable result
→ actuator not invoked
→ no observed physical movement
```

for both endpoints during the same coordinated run.

The recovery portion demonstrated:

```text
external boundary restored
→ accepted / provider_admissible
→ actuator invoked
→ physical movement
```

for both endpoints without rebooting the physical endpoints.

---

# What ACT-005 Adds

ACT-004 demonstrated physical non-execution when both endpoints received explicit unauthorized decisions.

ACT-005 tests a materially different condition:

**the authorization dependency itself is unavailable.**

The distinction is:

```text
ACT-004:
boundary available
→ explicit DENY
→ NO MOVE
```

versus:

```text
ACT-005:
boundary unavailable
→ no admissible authorization available
→ NO MOVE
```

ACT-005 therefore adds evidence that the tested physical execution path does not convert external authorization unavailability into local fallback permission.

It also demonstrates restoration of the external dependency without requiring endpoint resets.

---

# Failure Semantics

The ACT-005 result should be described as:

**fail-unavailable physical non-actuation**

rather than simply:

**denied**

During the outage, the endpoints did not receive an explicit provider denial.

They reported:

`unavailable / OSError(104,)`

This distinction preserves the difference between:

* an available authority returning a negative decision, and
* the authority path being unavailable.

Both resulted in no actuator invocation, but for different reasons.

---

# Claim Boundary

ACT-005 does not demonstrate behavior under every degraded-network condition.

The tested failure mode was a deliberately unavailable boundary with port 8089 confirmed closed.

ACT-005 did not systematically test:

* packet loss
* connection flapping
* extreme network delay
* partial responses
* asymmetric connectivity
* malformed boundary responses
* prolonged connection timeout loops
* coordinator failure during physical execution
* endpoint failure during recovery
* network infrastructure restart

A clean boundary outage and a degraded or "zombie" connection are different failure modes.

ACT-005 also does not demonstrate:

* exactly-once physical execution
* persistent physical replay protection
* sensor-confirmed final actuator position
* deterministic mechanical recovery time
* true parallel boundary processing
* large-fleet outage behavior
* safety-critical deployment readiness

Reported latency values represent the NUVL request/authorization portion of the tested path and exclude the servo hold and full mechanical completion interval.

Physical movement and non-movement were directly observed. No independent position sensor or electrical signal witness was used.

All conclusions apply **in the tested paths and configurations**.

