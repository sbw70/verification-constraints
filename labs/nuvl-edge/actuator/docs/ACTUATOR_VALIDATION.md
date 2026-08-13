# NUVL Physical Actuator Validation

## Overview

This document records physical actuator validation performed with NUVL-controlled ESP32-S3 endpoints and MG90S-class servo effectors.

The purpose of the actuator series was to extend NUVL testing beyond software decisions and visual status indicators into observable physical action.

The central test question was:

> Does externally determined admissibility remain correctly bound to physical execution at the endpoint?

The actuator implementation deliberately preserves a narrow execution rule:

* `accepted / provider_admissible` → actuator command may execute.
* `denied / unauthorized_request` → no actuator invocation.
* `denied / stale_replay_malformed` → no actuator invocation.
* authorization boundary unavailable → no actuator invocation.
* other non-accepted outcomes → no actuator invocation.

The actuator endpoints do not independently convert a failed or unavailable authorization path into permission to act.

ACT-001 through ACT-005 test this behavior across a single physical effector, mixed two-effector outcomes, dual acceptance, dual denial, and shared-boundary outage/recovery.

---

## Validation Classification

The actuator series is an **optional physical-effector integration of the existing NUVL architecture**, not a change to the underlying authority model.

The existing request, coordinator, external boundary, and decision path remain in place. The added capability maps an accepted result to a physical servo command.

The series supports a new physical-execution claim:

> In the tested paths, externally determined admissibility remained bound to physical actuator behavior.

It does **not** establish exactly-once physical execution, sensor-confirmed mechanical position, persistent actuator-side replay protection, or autonomous endpoint authorization.

---

## Test Architecture

### Physical endpoints

Two Seeed XIAO ESP32-S3 boards were qualified as actuator endpoints:

* `esp32-xiao-servo-01`
* `esp32-xiao-servo-02`

Both ran the same actuator firmware during the two-endpoint tests. Endpoint identity remained distinct through `device_id.txt`.

### Actuator

Physical effector:

* MG90S-class micro servo
* Signal: D4 / GPIO5
* PWM: 50 Hz
* Approximate commanded pulse positions: 1.0 ms, 1.5 ms, and 2.0 ms
* Actuation hold: approximately 1 second
* PWM released after the commanded interval

No brownout or endpoint reset was observed during the qualified XIAO servo bring-up.

### Authorization path

The tested path was:

`coordinator → XIAO endpoint → NUVL boundary → returned decision → endpoint actuator gate → servo`

The existing NUVL request and coordinator path was retained.

Physical movement was not used as evidence of authorization by itself. Test results also recorded the returned decision, reason, identity/IP binding, request latency, and software actuator state.

### Actuator telemetry

The endpoint reported:

* `actuator_attempted`
* `actuator_command_completed`
* `actuator_error`

An accepted result was expected to produce:

* `actuator_attempted=True`
* `actuator_command_completed=True`
* `actuator_error=None`

A non-accepted result was expected to produce:

* `actuator_attempted=False`
* `actuator_command_completed=False`
* `actuator_error=None`

Observable servo movement was separately recorded during the physical tests.

---

## Firmware

Qualified actuator firmware:

`esp32_xiao_servo_nuvl_archer.py`

Original tested size:

`9,790 bytes`

Original tested SHA-256:

`C29AD7BB8362BD532C62A87CE5D8BE3ED30C25E4543FF52A2CC98992E493AD84`

The same firmware hash was verified on both actuator endpoints.

The known-good pre-existing Archer fleet firmware was not modified. The actuator implementation was created as a derivative specifically for the physical-effector tests.

Publication copies may be renamed and sanitized. Hashes in this document identify the original qualified test artifacts and must not be attributed to modified publication copies.

---

# ACT-001 — Single-Effector Physical Actuation Binding

## Objective

Demonstrate that a single physical endpoint actuates after an accepted NUVL result and remains physically inactive for unauthorized, stale/replay/malformed, and boundary-unavailable outcomes.

The sequence also tested restoration of accepted physical execution after the external boundary returned.

## Endpoint

`esp32-xiao-servo-01`

IP during qualification:

`192.168.0.81`

Servo:

`D4 / GPIO5`

Latency budget:

`250 ms`

---

## Accepted path

Two consecutive accepted runs passed.

| Run ID             | Decision                       | Latency | Software actuator   | Physical result |
| ------------------ | ------------------------------ | ------: | ------------------- | --------------- |
| `18ca4956db80a0f8` | accepted / provider_admissible |   37 ms | attempted/completed | moved           |
| `18ca4960aa45fa38` | accepted / provider_admissible |   33 ms | attempted/completed | moved           |

Both runs reported:

* correct endpoint identity/IP binding
* `actuator_attempted=True`
* `actuator_command_completed=True`
* `actuator_error=None`
* latency within the 250 ms request budget

Physical servo movement was observed in both runs.

The second accepted run was captured on video.

**Result: PASS x2**

---

## Unauthorized path

Run:

`18ca4a45df7242d0`

Observed result:

`denied / unauthorized_request`

Latency:

`37 ms`

Actuator state:

* `actuator_attempted=False`
* `actuator_command_completed=False`
* `actuator_error=None`

Physical observation:

**No movement**

**Result: PASS**

---

## Stale/replay/malformed rejection class

Run:

`18ca4b57c9fe064c`

Observed result:

`denied / stale_replay_malformed`

Latency:

`33 ms`

Actuator state:

* `actuator_attempted=False`
* `actuator_command_completed=False`
* `actuator_error=None`

Physical observation:

**No movement**

**Result: PASS**

This test demonstrates that the existing `stale_replay_malformed` rejection class did not enter the actuator path.

It does **not** independently demonstrate persistent replay-state enforcement. Persistent replay behavior is outside the scope of ACT-001.

---

## Boundary unavailable

The external NUVL boundary was deliberately stopped and port 8089 was confirmed unavailable before the test.

The endpoint was still instructed to request the accept path.

Run:

`18ca4c18d61aa52c`

Observed result:

`unavailable / OSError(104,)`

Latency:

`12 ms`

Actuator state:

* `actuator_attempted=False`
* `actuator_command_completed=False`
* `actuator_error=None`

Physical observation:

**No movement**

**Result: PASS**

In the tested path, loss of the external authorization boundary did not produce fallback actuation.

---

## Boundary restoration

The boundary was restarted and `/health` returned `ok`.

The XIAO endpoint was not reset.

Two subsequent accepted runs passed:

| Run ID             | Decision                       | Latency | Physical result |
| ------------------ | ------------------------------ | ------: | --------------- |
| `18ca4ce38d4a0470` | accepted / provider_admissible |   33 ms | moved           |
| `18ca4cea378ad3dc` | accepted / provider_admissible |   35 ms | moved           |

Both runs reported successful actuator command completion.

The second recovery run was captured on video.

**Result: PASS x2**

### ACT-001 conclusion

In the tested single-endpoint path, externally determined admissibility controlled access to a physical servo actuator. Accepted decisions produced observable physical movement; unauthorized, stale/replay/malformed, and boundary-unavailable outcomes produced no actuator invocation and no observed movement. Following boundary restoration, accepted physical actuation resumed without resetting the endpoint.

---

# ACT-002 — Two-Endpoint Mixed Physical Actuation Binding

## Objective

Determine whether different authorization results remain correctly associated with separate physical effectors during the same coordinated run.

Two complementary assignments were tested.

### Run A

* `servo-01` → accept → MOVE
* `servo-02` → deny → NO MOVE

### Run B

* `servo-01` → deny → NO MOVE
* `servo-02` → accept → MOVE

Each assignment was repeated twice.

---

## Run A results

### Run `18ca4f82e4a8881c`

`esp32-xiao-servo-01`

* accepted / provider_admissible
* 34 ms
* actuator command completed
* physical movement observed

`esp32-xiao-servo-02`

* denied / unauthorized_request
* 36 ms
* actuator untouched
* no physical movement

**Result: PASS**

### Run `18ca4f8b3096f8dc`

`esp32-xiao-servo-01`

* accepted
* 35 ms
* moved

`esp32-xiao-servo-02`

* denied
* 33 ms
* did not move

**Result: PASS**

Video was captured for the second Run A execution.

---

## Run B results

### Run `18ca4fbdae8e22b0`

`esp32-xiao-servo-01`

* denied / unauthorized_request
* 32 ms
* actuator untouched
* no movement

`esp32-xiao-servo-02`

* accepted / provider_admissible
* 35 ms
* actuator command completed
* movement observed

**Result: PASS**

### Run `18ca4ff9446c0fc8`

`esp32-xiao-servo-01`

* denied
* 33 ms
* no movement

`esp32-xiao-servo-02`

* accepted
* 34 ms
* moved

**Result: PASS**

---

## ACT-002 summary

Across all four runs:

* endpoint identity remained correct
* IP binding remained correct
* decision and reason remained bound to the intended endpoint
* physical behavior matched the per-device authorization result
* all results were ON_TIME
* observed request latencies were 32–36 ms
* no unexpected result keys were reported
* no cross-actuation was observed

**Result: PASS x4**

### ACT-002 conclusion

In the tested two-endpoint path, externally determined authorization outcomes remained bound to the correct physical effector. Reversing which endpoint was admissible reversed which servo moved, while the denied endpoint remained physically inactive.

---

# ACT-003 — Dual-Admissible Physical Fan-In

## Objective

Demonstrate two physical endpoints receiving accepted results in the same coordinated run and independently reaching their respective actuator paths.

Expected behavior:

* `servo-01` → accept → MOVE
* `servo-02` → accept → MOVE

Three coordinated runs were performed.

## Results

| Run ID             | Servo 01         | Servo 02         | Latency range | Result |
| ------------------ | ---------------- | ---------------- | ------------: | ------ |
| `18ca50afaf3fbcf8` | accepted → moved | accepted → moved |      32–33 ms | PASS   |
| `18ca50e0600de69c` | accepted → moved | accepted → moved |      33–34 ms | PASS   |
| `18ca50e481d5a234` | accepted → moved | accepted → moved |      34–36 ms | PASS   |

Across all three runs:

* both endpoints returned `accepted / provider_admissible`
* both actuator commands completed
* both servos physically moved
* both device/IP bindings were correct
* all results were ON_TIME
* no unexpected result keys were reported

**Result: PASS x3**

### ACT-003 conclusion

In the tested two-endpoint path, two admissible endpoints produced correctly bound physical actuator responses in the same coordinated run, repeated three times.

This is evidence of **near-concurrent coordinated fan-in**. It is not a claim of true parallel boundary processing.

---

# ACT-004 — Dual-Denied Physical Non-Actuation

## Objective

Test the inverse of ACT-003.

Both endpoints received unauthorized outcomes during the same coordinated run, and neither physical effector was permitted to enter its actuator path.

Expected behavior:

* `servo-01` → deny → NO MOVE
* `servo-02` → deny → NO MOVE

## Results

### Run `18ca515fa21c11c4`

`servo-01`

* denied / unauthorized_request
* 37 ms
* actuator untouched
* no movement

`servo-02`

* denied / unauthorized_request
* 38 ms
* actuator untouched
* no movement

**Result: PASS**

### Run `18ca5175764db848`

`servo-01`

* denied / unauthorized_request
* 34 ms
* actuator untouched
* no movement

`servo-02`

* denied / unauthorized_request
* 32 ms
* actuator untouched
* no movement

**Result: PASS**

Across both runs:

* correct identity/IP binding
* correct denial result and reason
* both actuator paths remained untouched
* no physical movement was observed
* all results were ON_TIME
* no unexpected result keys were reported

**Result: PASS x2**

### ACT-004 conclusion

In the tested two-endpoint path, two coordinated unauthorized decisions resulted in zero actuator invocation and zero observed physical movement.

---

# ACT-005 — Dual-Effector Shared-Boundary Outage and Recovery

## Objective

Determine the behavior of both physical effectors when their shared external authorization boundary becomes unavailable.

Both endpoints requested the accept path.

Expected outage behavior:

* `servo-01` → unavailable → NO MOVE
* `servo-02` → unavailable → NO MOVE

The boundary was then restored without resetting either XIAO, followed by two dual-accept recovery runs.

---

## Shared-boundary outage

The boundary on port 8089 was confirmed unavailable before execution.

Run:

`18ca521127d5f1ac`

Both endpoints requested accept.

`servo-01`

* unavailable / `OSError(104,)`
* 13 ms
* `actuator_attempted=False`
* `actuator_command_completed=False`
* no movement

`servo-02`

* unavailable / `OSError(104,)`
* 13 ms
* `actuator_attempted=False`
* `actuator_command_completed=False`
* no movement

Both identity/IP bindings were correct.

Both results were ON_TIME.

No unexpected results were reported.

**Result: PASS**

---

## Shared-boundary recovery

The boundary was restarted.

Health returned:

`ok`

Neither XIAO endpoint was reset.

The already-qualified ACT-003 dual-accept launcher was deliberately reused for recovery verification.

### Recovery run `18ca5244856a83b8`

`servo-01`

* accepted / provider_admissible
* 40 ms
* actuator completed
* moved

`servo-02`

* accepted / provider_admissible
* 38 ms
* actuator completed
* moved

**Result: PASS**

### Recovery run `18ca52542f653994`

`servo-01`

* accepted / provider_admissible
* 35 ms
* actuator completed
* moved

`servo-02`

* accepted / provider_admissible
* 33 ms
* actuator completed
* moved

**Result: PASS**

### ACT-005 conclusion

In the tested two-endpoint path, loss of the shared external authorization boundary caused both endpoints to fail unavailable without physical actuation. After boundary restoration, both endpoints resumed admissible physical actuation without endpoint resets.

---

# Combined Physical Decision Matrix

ACT-002 through ACT-004 exercised all four basic two-endpoint accept/deny combinations.

| Servo 01 | Servo 02 | Expected physical behavior | Observed |
| -------- | -------- | -------------------------- | -------- |
| ACCEPT   | DENY     | move / still               | PASS x2  |
| DENY     | ACCEPT   | still / move               | PASS x2  |
| ACCEPT   | ACCEPT   | move / move                | PASS x3  |
| DENY     | DENY     | still / still              | PASS x2  |

ACT-005 added the shared-unavailability condition:

| Servo 01 request | Servo 02 request | Boundary    | Expected      | Observed |
| ---------------- | ---------------- | ----------- | ------------- | -------- |
| ACCEPT           | ACCEPT           | unavailable | still / still | PASS     |
| ACCEPT           | ACCEPT           | restored    | move / move   | PASS x2  |

No cross-actuation was observed during the mixed-outcome tests.

---

# Evidence Summary

## ACT-001

Manifest:

`act001_manifest_20260809_212704.txt`

SHA-256:

`39FB7C16B173DC0E231917C3D53667800027D083DB41B4459478381755CA1DF3`

Key runtime evidence:

* `xiao_servo_accept_20260809_201357.log`
* `xiao_servo_accept_20260809_201430.log`
* `xiao_servo_deny_20260809_203008.log`
* `xiao_servo_stale_20260809_204955.log`
* `xiao_servo_outage_20260809_210412.log`
* `xiao_servo_recovery_20260809_211901.log`
* `xiao_servo_recovery_20260809_211920.log`

Video evidence was captured for accepted physical actuation, denied non-actuation, and post-outage recovery.

## ACT-002

Manifest:

`act002_manifest_20260809_222040.txt`

SHA-256:

`2FA9B0BF636D71D249B1A00BAE06E2ECED511776D30AC1C390864EEA6F7A7ABF`

Runtime evidence:

* `act002_mixed_a_20260809_220636.log`
* `act002_mixed_a_20260809_220728.log`
* `act002_mixed_b_20260809_221101.log`
* `act002_mixed_b_20260809_221531.log`

## ACT-003

Manifest:

`act003_manifest_20260809_223518.txt`

SHA-256:

`99C445E8A101A9C3A3FC7ED85247F0E5D313D1311E8566C9AA6889648D5DA0AC`

Runtime evidence:

* `act003_dual_accept_20260809_222808.log`
* `act003_dual_accept_20260809_223115.log`
* `act003_dual_accept_20260809_223222.log`

## ACT-004

Manifest:

`act004_manifest_20260809_224512.txt`

SHA-256:

`EC44641D332CD48E6A9E0AECFEF8584D1BBC66183B0682A0BAEEC35F37AE5DA6`

Runtime evidence:

* `act004_dual_deny_20260809_224056.log`
* `act004_dual_deny_20260809_224246.log`

## ACT-005

Manifest:

`act005_manifest_20260809_230307.txt`

SHA-256:

`3B8B38F0D29FB0E189C88984202C7E85EF7B2975F20D83FB7921F3522C41AC1E`

Runtime evidence:

* `act005_dual_outage_20260809_225334.log`
* `act005_dual_recovery_20260809_225715.log`
* `act005_dual_recovery_20260809_225842.log`

Pi recovery evidence:

`/home/seth/nuvl_local_hardened_latency_restart_20260809_225511.log`

SHA-256:

`664E0CCABA1A8E5661405B21118690E9C0035673323CE8520124E724EF7FD666`

---

# What the Actuator Series Demonstrates

Across ACT-001 through ACT-005, the tested implementation demonstrated:

1. An externally returned admissible result can gate entry into a physical actuator path.

2. Unauthorized results can leave the physical actuator untouched.

3. The tested stale/replay/malformed rejection class leaves the actuator untouched.

4. Loss of the external authorization boundary does not produce fallback physical execution in the tested path.

5. Restoring the boundary can restore admissible physical execution without resetting the actuator endpoint.

6. Different authorization results can remain correctly bound to different physical effectors in the same coordinated run.

7. Reversing which endpoint is admissible reverses which physical effector moves.

8. Two admissible endpoints can both reach their physical actuator paths during near-concurrent coordinated fan-in.

9. Two denied endpoints can remain physically inactive during the same coordinated run.

10. Shared-boundary loss can cause multiple physical endpoints to fail unavailable without physical actuation.

The resulting evidence extends the NUVL test program from logical decision binding to observable physical execution behavior.

---

# Limitations

The actuator series does **not** establish:

* exactly-once physical execution
* sensor-confirmed final servo position
* independent mechanical-position attestation
* persistent single-use authority through the actuator path
* actuator replay resistance across restart or power loss
* endpoint-enforced execution deadlines
* deterministic mechanical completion time
* true parallel processing at the shared boundary
* safety certification
* real-time control-system certification

`actuator_command_completed=True` means that the software actuator command completed without a reported error. It is not, by itself, proof that the commanded mechanical position was reached.

Physical movement observations and video provide separate evidence of movement in the documented runs but do not constitute independent position sensing.

The reported `elapsed_ms` values measure the NUVL request/authorization portion of the tested path. They are captured before the approximately one-second servo hold and therefore must **not** be represented as total physical-action latency.

The ACT-001 `stale_replay_malformed` result demonstrates correct non-actuation for that returned rejection class. It must not be represented as an independent persistent replay-state test.

ACT-003 is near-concurrent coordinated fan-in through the tested shared path. It does not demonstrate parallel boundary processing.

All conclusions in this document apply **in the tested paths and configurations**.

---

# Overall Result

**ACT-001: PASS**

Single-effector accepted actuation, unauthorized non-actuation, stale/replay/malformed-class non-actuation, boundary-unavailable non-actuation, and post-restoration physical recovery demonstrated.

**ACT-002: PASS**

Two-effector mixed physical outcome binding demonstrated in both directions, with no observed cross-actuation.

**ACT-003: PASS**

Dual-admissible physical actuation demonstrated in three coordinated runs.

**ACT-004: PASS**

Dual-denied physical non-actuation demonstrated in two coordinated runs.

**ACT-005: PASS**

Shared-boundary outage produced unavailable results and zero physical actuation across both endpoints; dual physical actuation recovered after boundary restoration without endpoint resets.

## Series conclusion

In the tested single- and two-endpoint paths, externally determined NUVL admissibility remained bound to physical actuator execution. Accepted decisions produced the intended observable physical actuation, while unauthorized, stale/replay/malformed-class, and boundary-unavailable outcomes did not enter the actuator path. Across two effectors, per-device authorization remained associated with the correct physical output, including mixed outcomes, reversed outcomes, dual acceptance, dual denial, and shared-boundary outage/recovery.

