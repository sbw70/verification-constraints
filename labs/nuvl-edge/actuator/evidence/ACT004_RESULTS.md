# ACT-004 — Dual-Denied Physical Non-Actuation

## Status

**PASS x2**

ACT-004 validated the dual-denied case across two physical actuator endpoints.

Both XIAO ESP32-S3 endpoints received `denied / unauthorized_request` outcomes in the same coordinated run. Neither endpoint entered its actuator path, and neither physical servo moved.

The test was repeated twice.

---

## Test Classification

ACT-004 is an **optional physical-effector integration of the existing NUVL architecture**, not an architecture change.

It maps to the coordinated multi-effector denial / physical non-execution use case.

The property supported by ACT-004 is:

> Two distinct unauthorized endpoints can receive correctly bound denial outcomes during the same coordinated run while both physical actuator paths remain untouched.

ACT-004 does not establish exactly-once physical execution, persistent replay protection, large-fleet behavior, or independently instrumented proof of mechanical state.

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

`deny`

Expected result for each endpoint:

`denied / unauthorized_request`

Expected software actuator state:

```text
actuator_attempted=False
actuator_command_completed=False
actuator_error=None
```

Expected physical result:

```text
servo-01 → NO MOVE
servo-02 → NO MOVE
```

PASS additionally required:

* correct endpoint identity
* correct IP binding
* correct decision and reason
* both results ON_TIME
* latency within the 250 ms request budget
* no unexpected result keys

The critical physical requirement was that neither endpoint enter its actuator path.

---

# Run 1

Run ID:

`18ca515fa21c11c4`

## Servo 01

Endpoint:

`esp32-xiao-servo-01`

Observed:

* expected mode: `deny`
* decision: `denied`
* reason: `unauthorized_request`
* latency: `37 ms`
* identity/IP binding correct
* `actuator_attempted=False`
* `actuator_command_completed=False`
* `actuator_error=None`
* actuator oracle matched
* no physical movement observed

## Servo 02

Endpoint:

`esp32-xiao-servo-02`

Observed:

* expected mode: `deny`
* decision: `denied`
* reason: `unauthorized_request`
* latency: `38 ms`
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

Result:

**PASS**

---

# Run 2

Run ID:

`18ca5175764db848`

## Servo 01

Observed:

* decision: `denied`
* reason: `unauthorized_request`
* latency: `34 ms`
* identity/IP binding correct
* actuator untouched
* no physical movement observed

## Servo 02

Observed:

* decision: `denied`
* reason: `unauthorized_request`
* latency: `32 ms`
* identity/IP binding correct
* actuator untouched
* no physical movement observed

Both results:

`ON_TIME`

Unexpected result keys:

`none`

Physical result:

`NO MOVE / NO MOVE`

Result:

**PASS**

---

# Result Matrix

| Run ID             | Servo 01         | Servo 02         | Latencies  | Physical result   | Result |
| ------------------ | ---------------- | ---------------- | ---------- | ----------------- | ------ |
| `18ca515fa21c11c4` | denied → NO MOVE | denied → NO MOVE | 37 / 38 ms | NO MOVE / NO MOVE | PASS   |
| `18ca5175764db848` | denied → NO MOVE | denied → NO MOVE | 34 / 32 ms | NO MOVE / NO MOVE | PASS   |

Total coordinated runs:

**2**

Correct dual-denial outcomes:

**2/2**

Physical actuator invocations:

**0**

Observed physical movements:

**0**

Latency range:

`32–38 ms`

All endpoint results:

`ON_TIME`

Unexpected result keys:

`none`

---

# Source Launcher

Original source:

`run_two_xiao_servo_dual_deny_archer.py`

Size:

`5,905 bytes`

SHA-256:

`21B65773B6085FE9868F02C9D8DB6BE8CC23A5E7159557939A39D96F83E7A29D`

Contract:

```text
servo-01 → deny → NO MOVE
servo-02 → deny → NO MOVE
```

Compile:

**PASS**

---

# Runtime Evidence

## Run 1

`act004_dual_deny_20260809_224056.log`

Size:

`2,192 bytes`

SHA-256:

`17265418F2BFE220B3E4606F1D38843004F27C239A606681D81148D0B2ED9F37`

Result:

**PASS**

Physical observation:

`NO MOVE / NO MOVE`

---

## Run 2

`act004_dual_deny_20260809_224246.log`

Size:

`2,192 bytes`

SHA-256:

`9A62028B9224CF62E54D44E21C505CD018807FB8AF64A68F28D3F32C3E8BE5F5`

Result:

**PASS**

Physical observation:

`NO MOVE / NO MOVE`

---

# Evidence Manifest

Manifest:

`act004_manifest_20260809_224512.txt`

Original path:

`C:\Users\holiw\esp32-main\act004_manifest_20260809_224512.txt`

Size:

`456 bytes`

SHA-256:

`EC44641D332CD48E6A9E0AECFEF8584D1BBC66183B0682A0BAEEC35F37AE5DA6`

The manifest closes the local ACT-004 evidence set.

---

# Relationship to the Physical Decision Matrix

ACT-002 established the two mixed cases:

```text
ACCEPT / DENY → MOVE / NO MOVE
DENY / ACCEPT → NO MOVE / MOVE
```

ACT-003 established:

```text
ACCEPT / ACCEPT → MOVE / MOVE
```

ACT-004 completes the basic two-endpoint accept/deny matrix with:

```text
DENY / DENY → NO MOVE / NO MOVE
```

Together, ACT-002 through ACT-004 exercised all four basic two-endpoint authorization combinations:

| Servo 01 | Servo 02 | Physical result   |
| -------- | -------- | ----------------- |
| ACCEPT   | DENY     | MOVE / NO MOVE    |
| DENY     | ACCEPT   | NO MOVE / MOVE    |
| ACCEPT   | ACCEPT   | MOVE / MOVE       |
| DENY     | DENY     | NO MOVE / NO MOVE |

The ACT-004 result is important because the system was not merely required to produce the correct logical denial strings.

Both physical execution paths also had to remain untouched.

---

# Supported Conclusion

ACT-004 supports the following bounded conclusion:

> In the tested two-endpoint path, two coordinated unauthorized decisions resulted in zero actuator invocation and zero observed physical movement.

Across both executions:

* both endpoints returned `denied / unauthorized_request`
* both endpoint identities remained correct
* both IP bindings remained correct
* neither endpoint entered its actuator path
* neither physical servo moved
* all results were ON_TIME
* request latency remained within 32–38 ms
* no unexpected result keys were reported

---

# What ACT-004 Adds

ACT-003 demonstrated the positive dual-admissible case:

`MOVE / MOVE`

ACT-004 establishes the corresponding negative dual-denial case:

`NO MOVE / NO MOVE`

The new supported property is:

**coordinated dual physical non-execution following independently bound unauthorized outcomes**

This provides evidence that two simultaneous requested actions were not converted into physical execution merely because both endpoints were active and participating in the same coordinated test.

Each endpoint still required an admissible result before entering its physical actuator path.

---

# Claim Boundary

ACT-004 does not demonstrate:

* persistent replay protection
* physical non-execution under every possible denial class
* behavior during external boundary loss
* exactly-once physical execution
* large-fleet actuator behavior
* true parallel boundary processing
* deterministic mechanical timing
* independent sensor-confirmed non-movement
* endpoint-enforced execution deadlines
* safety-critical deployment readiness

The physical observation was that neither servo moved during either documented run.

No independent position sensor or electrical signal witness was used. Therefore, the evidence supports **observed physical non-actuation** and software-reported non-invocation, not independently instrumented proof that no electrical or microscopic mechanical activity occurred.

Boundary-unavailable physical behavior is tested separately in ACT-005.

All conclusions apply **in the tested paths and configurations**.

