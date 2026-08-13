# ACT-003 — Dual-Admissible Physical Fan-In

## Status

**PASS x3**

ACT-003 validated the dual-admissible case across two physical actuator endpoints.

Both XIAO ESP32-S3 endpoints received accepted NUVL outcomes in the same coordinated run, both entered their actuator paths, and both produced observable physical movement.

The test was repeated three times.

---

## Test Classification

ACT-003 is an **optional physical-effector integration of the existing NUVL architecture**, not an architecture change.

It maps to the coordinated multi-effector use case.

The new property supported by ACT-003 is:

> Two distinct admissible endpoints can each retain correct decision-to-effector binding and reach their respective physical actuator paths during the same coordinated run.

ACT-003 does not establish true parallel boundary execution, large-fleet scaling, deterministic physical synchronization, or exactly-once physical execution.

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

Both endpoints used the same external boundary and coordinator path.

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

The same firmware hash was verified on both XIAO endpoints.

---

# Test Contract

Both endpoints were assigned:

`accept`

Expected result for each endpoint:

`accepted / provider_admissible`

Expected software actuator state:

```text
actuator_attempted=True
actuator_command_completed=True
actuator_error=None
```

Expected physical result:

```text
servo-01 → MOVE
servo-02 → MOVE
```

PASS additionally required:

* correct endpoint identity
* correct IP binding
* correct decision and reason
* both results ON_TIME
* latency within the 250 ms request budget
* no unexpected result keys

---

# Run 1

Run ID:

`18ca50afaf3fbcf8`

## Servo 01

Endpoint:

`esp32-xiao-servo-01`

Observed:

* expected mode: `accept`
* decision: `accepted`
* reason: `provider_admissible`
* latency: `32 ms`
* identity/IP binding correct
* `actuator_attempted=True`
* `actuator_command_completed=True`
* `actuator_error=None`
* actuator oracle matched
* physical movement observed

## Servo 02

Endpoint:

`esp32-xiao-servo-02`

Observed:

* expected mode: `accept`
* decision: `accepted`
* reason: `provider_admissible`
* latency: `33 ms`
* identity/IP binding correct
* `actuator_attempted=True`
* `actuator_command_completed=True`
* `actuator_error=None`
* actuator oracle matched
* physical movement observed

Both endpoint results:

`ON_TIME`

Unexpected result keys:

`none`

Physical result:

`MOVE / MOVE`

Result:

**PASS**

---

# Run 2

Run ID:

`18ca50e0600de69c`

## Servo 01

Observed:

* accepted / provider_admissible
* latency: `34 ms`
* actuator command completed
* identity/IP binding correct
* ON_TIME
* physical movement observed

## Servo 02

Observed:

* accepted / provider_admissible
* latency: `33 ms`
* actuator command completed
* identity/IP binding correct
* ON_TIME
* physical movement observed

Physical result:

`MOVE / MOVE`

Result:

**PASS**

---

# Run 3

Run ID:

`18ca50e481d5a234`

## Servo 01

Observed:

* accepted / provider_admissible
* latency: `36 ms`
* actuator command completed
* identity/IP binding correct
* ON_TIME
* physical movement observed

## Servo 02

Observed:

* accepted / provider_admissible
* latency: `34 ms`
* actuator command completed
* identity/IP binding correct
* ON_TIME
* physical movement observed

Physical result:

`MOVE / MOVE`

Result:

**PASS**

---

# Result Matrix

| Run ID             | Servo 01 | Servo 02 | Latencies  | Physical result | Result |
| ------------------ | -------- | -------- | ---------- | --------------- | ------ |
| `18ca50afaf3fbcf8` | accepted | accepted | 32 / 33 ms | MOVE / MOVE     | PASS   |
| `18ca50e0600de69c` | accepted | accepted | 34 / 33 ms | MOVE / MOVE     | PASS   |
| `18ca50e481d5a234` | accepted | accepted | 36 / 34 ms | MOVE / MOVE     | PASS   |

Total coordinated runs:

**3**

Correct dual physical outcomes:

**3/3**

Latency range:

`32–36 ms`

Observed physical result in every run:

`MOVE / MOVE`

Unexpected result keys:

`none`

---

# Source Launcher

Original source:

`run_two_xiao_servo_dual_accept_archer.py`

Size:

`5,914 bytes`

SHA-256:

`96BECFB0B85801674D5AEEF117A6B86826AF22F4B0EF82306530FBBD07B05137`

Contract:

```text
servo-01 → accept → MOVE
servo-02 → accept → MOVE
```

Compile:

**PASS**

---

# Runtime Evidence

## Run 1

`act003_dual_accept_20260809_222808.log`

Size:

`2,232 bytes`

SHA-256:

`B4FDB05182D9579607681C0A216F481AF51AD521BD229669CCEBA673E7F0998A`

Result:

**PASS**

---

## Run 2

`act003_dual_accept_20260809_223115.log`

Size:

`2,232 bytes`

SHA-256:

`8DCC923E5B3BAFDCEE0C2E23E61CC59C69C4A5E44AA0A356A7955F03ED37D6C5`

Result:

**PASS**

---

## Run 3

`act003_dual_accept_20260809_223222.log`

Size:

`2,232 bytes`

SHA-256:

`E0C3BD546EE4038AC03907340F6417F0C6199C5311D8E636FA13738AB005E42B`

Result:

**PASS**

---

# Evidence Manifest

Manifest:

`act003_manifest_20260809_223518.txt`

Original path:

`C:\Users\holiw\esp32-main\act003_manifest_20260809_223518.txt`

Size:

`558 bytes`

SHA-256:

`99C445E8A101A9C3A3FC7ED85247F0E5D313D1311E8566C9AA6889648D5DA0AC`

The manifest closes the local ACT-003 evidence set.

---

# Supported Conclusion

ACT-003 supports the following bounded conclusion:

> In the tested two-endpoint path, two admissible endpoints produced correctly bound physical actuator responses in the same coordinated run, repeated three times.

Across all three executions:

* both endpoints returned `accepted / provider_admissible`
* both endpoint identities remained correct
* both IP bindings remained correct
* both actuator commands completed
* both physical servos moved
* all results were ON_TIME
* request latency remained within 32–36 ms
* no unexpected result keys were reported

---

# What ACT-003 Adds

ACT-002 demonstrated mixed physical outcomes with one admissible and one denied endpoint.

ACT-003 adds the dual-admissible case.

The new supported property is:

**coordinated dual physical execution after independently bound admissible outcomes**

This demonstrates that the tested shared NUVL path did not collapse two admissible endpoint results into one physical execution or misassign the result to the wrong effector.

Both endpoints independently reached their physical actuator paths in the same coordinated run.

---

# Concurrency Qualification

ACT-003 should be described as:

**near-concurrent coordinated fan-in**

It should not be described as:

**parallel boundary processing**

The test demonstrates two physical endpoints participating in the same coordinated execution window and both receiving correctly bound results.

It does not prove that the shared boundary processed both requests simultaneously at the instruction, thread, process, or server level.

---

# Claim Boundary

ACT-003 does not demonstrate:

* true parallel boundary execution
* deterministic synchronization between physical effectors
* simultaneous mechanical start time
* exactly-once physical execution
* large-fleet actuator scaling
* persistent actuator replay prevention
* endpoint-enforced execution deadlines
* sensor-confirmed final servo position
* deterministic mechanical completion time
* safety-critical deployment readiness

The physical observation was that both servos moved in all three runs.

No independent sensor or synchronized mechanical timing instrument was used to determine whether the two servos began or completed movement at exactly the same time.

Reported latency values describe the NUVL request/authorization portion of the tested path and exclude the servo hold and full mechanical-action interval.

All conclusions apply **in the tested paths and configurations**.

