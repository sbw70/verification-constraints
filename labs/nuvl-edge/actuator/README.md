# NUVL Physical Actuator Validation

This directory contains the physical actuator integration and validation work for the NUVL edge test environment.

The actuator series extends the existing NUVL decision path from logical endpoint outcomes to observable physical execution using Seeed XIAO ESP32-S3 endpoints and MG90S-class servo effectors.

The integration does not change the underlying NUVL authority architecture.

It adds a physical execution capability downstream of the existing decision path:

    request → NUVL boundary → decision → endpoint → actuator gate → physical action

The endpoint can perform a physical action, but the addition of that capability does not give the endpoint independent authority to determine whether the action is admissible.

---

## Status

ACT-001 through ACT-005:

**PASS**

The completed series covers:

- single-effector accepted actuation
- single-effector unauthorized non-actuation
- stale/replay/malformed-class non-actuation
- boundary-unavailable non-actuation
- single-effector outage recovery
- two-effector mixed outcomes
- reversed two-effector mixed outcomes
- dual-admissible physical execution
- dual-denied physical non-execution
- shared-boundary outage
- shared-boundary recovery without endpoint resets

Across the documented series:

**19/19 coordinated test executions passed their defined oracle.**

All conclusions remain bounded to **the tested paths and configurations**.

---

# Directory Structure

    actuator/
    ├── README.md
    │
    ├── firmware/
    │   ├── README.md
    │   └── esp32_xiao_servo_nuvl.py
    │
    ├── tests/
    │   ├── README.md
    │   ├── act001_single_accept.py
    │   ├── act001_single_deny.py
    │   ├── act001_single_stale.py
    │   ├── act001_single_outage.py
    │   ├── act002_two_endpoint_mixed_a.py
    │   ├── act002_two_endpoint_mixed_b.py
    │   ├── act003_two_endpoint_dual_accept.py
    │   ├── act004_two_endpoint_dual_deny.py
    │   └── act005_two_endpoint_dual_outage.py
    │
    ├── docs/
    │   ├── ACTUATOR_VALIDATION.md
    │   ├── TEST_MATRIX.md
    │   ├── HARDWARE_SETUP.md
    │   └── LIMITATIONS.md
    │
    └── evidence/
        ├── README.md
        ├── ACT001_RESULTS.md
        ├── ACT002_RESULTS.md
        ├── ACT003_RESULTS.md
        ├── ACT004_RESULTS.md
        └── ACT005_RESULTS.md

---

# Architecture Role

The actuator work is an **optional capability integration**, not an architecture change.

NUVL continues to determine whether the requested operation is admissible through the existing external decision path.

The actuator endpoint consumes that result.

Conceptually:

                     NUVL decision
                          │
                          ▼
                  ┌───────────────┐
                  │ XIAO endpoint │
                  └───────┬───────┘
                          │
                    decision gate
                     ┌────┴────┐
                     │         │
                  accepted    other
                     │         │
                     ▼         ▼
                  ACTUATE    NO CALL
                     │
                     ▼
                   SERVO

The tested execution rule is intentionally narrow:

    accepted / provider_admissible
    → actuator permitted

Tested non-accepted conditions remained outside the actuator path.

---

# Hardware

Qualified physical endpoints:

- `esp32-xiao-servo-01`
- `esp32-xiao-servo-02`

Each endpoint used:

- Seeed XIAO ESP32-S3
- MG90S-class servo
- MicroPython v1.28.0
- servo signal on D4 / GPIO5
- 50 Hz PWM

Both endpoints ran the same actuator firmware while retaining separate logical identities through `device_id.txt`.

See:

`docs/HARDWARE_SETUP.md`

---

# Firmware

Repository firmware:

`firmware/esp32_xiao_servo_nuvl.py`

Original qualified source:

`esp32_xiao_servo_nuvl_archer.py`

Original qualified SHA-256:

`C29AD7BB8362BD532C62A87CE5D8BE3ED30C25E4543FF52A2CC98992E493AD84`

The same original firmware was qualified on both actuator endpoints.

The repository version is a sanitized publication copy. Local deployment configuration was removed while retaining the actuator decision logic and tested execution path.

Because the publication copy is not byte-identical to the original qualified artifact, the original qualification hash identifies the original tested source, not the sanitized repository copy.

See:

`firmware/README.md`

---

# Actuator Result Fields

The actuator firmware reports:

- `actuator_attempted`
- `actuator_command_completed`
- `actuator_error`

For an accepted path, the expected software state is:

    actuator_attempted=True
    actuator_command_completed=True
    actuator_error=None

For a non-accepted path:

    actuator_attempted=False
    actuator_command_completed=False
    actuator_error=None

These fields distinguish the authorization result from subsequent entry into the actuator routine.

They are software telemetry, not independent mechanical sensors.

Physical movement and non-movement were separately observed during qualification.

---

# ACT-001 — Single-Effector Decision Binding

ACT-001 established the basic physical execution boundary using one actuator endpoint.

Tested conditions:

| Condition | Expected physical result | Result |
|---|---|---|
| accepted / provider_admissible | MOVE | PASS x2 |
| denied / unauthorized_request | NO MOVE | PASS |
| denied / stale_replay_malformed | NO MOVE | PASS |
| boundary unavailable | NO MOVE | PASS |
| boundary restored / accepted | MOVE | PASS x2 |

Total:

**7/7 PASS**

The endpoint was not reset between the outage and recovery portions.

ACT-001 demonstrated that, in the tested path, loss of the external authorization boundary did not become fallback permission to actuate.

Detailed results:

`evidence/ACT001_RESULTS.md`

---

# ACT-002 — Mixed Two-Effector Binding

ACT-002 introduced a second physical endpoint and tested different authorization outcomes during the same coordinated run.

Assignment A:

    servo-01 → ACCEPT → MOVE
    servo-02 → DENY   → NO MOVE

Repeated twice:

**PASS x2**

The assignment was then reversed:

    servo-01 → DENY   → NO MOVE
    servo-02 → ACCEPT → MOVE

Repeated twice:

**PASS x2**

Total:

**4/4 PASS**

Observed cross-actuation:

**0**

The reversal demonstrated that physical execution followed per-device admissibility rather than remaining associated with one particular servo.

Detailed results:

`evidence/ACT002_RESULTS.md`

---

# ACT-003 — Dual-Admissible Physical Fan-In

ACT-003 assigned both physical endpoints to the accepted path.

Expected:

    servo-01 → ACCEPT → MOVE
    servo-02 → ACCEPT → MOVE

Result:

**PASS x3**

Both actuator commands completed and both servos physically moved during every documented run.

ACT-003 supports **near-concurrent coordinated physical fan-in**.

It does not establish true parallel boundary processing.

Detailed results:

`evidence/ACT003_RESULTS.md`

---

# ACT-004 — Dual-Denied Physical Non-Actuation

ACT-004 tested the corresponding dual-denial case.

Expected:

    servo-01 → DENY → NO MOVE
    servo-02 → DENY → NO MOVE

Result:

**PASS x2**

Across both runs:

- both endpoints returned `denied / unauthorized_request`
- neither endpoint entered its actuator path
- neither servo moved

Detailed results:

`evidence/ACT004_RESULTS.md`

---

# ACT-005 — Shared-Boundary Outage and Recovery

ACT-005 tested both physical endpoints while their shared external authorization boundary was deliberately unavailable.

Both endpoints requested accept.

Observed:

    servo-01 → unavailable → NO MOVE
    servo-02 → unavailable → NO MOVE

Outage:

**PASS**

The external boundary was then restored.

Neither XIAO endpoint was reset.

The already-qualified ACT-003 dual-accept launcher was reused rather than creating a duplicate recovery launcher.

Recovery:

    servo-01 → ACCEPT → MOVE
    servo-02 → ACCEPT → MOVE

Result:

**PASS x2**

Detailed results:

`evidence/ACT005_RESULTS.md`

---

# Two-Effector Physical Matrix

ACT-002 through ACT-004 exercised all four basic two-endpoint accept/deny combinations.

| Servo 01 | Servo 02 | Expected physical result | Result |
|---|---|---|---|
| ACCEPT | DENY | MOVE / NO MOVE | PASS x2 |
| DENY | ACCEPT | NO MOVE / MOVE | PASS x2 |
| ACCEPT | ACCEPT | MOVE / MOVE | PASS x3 |
| DENY | DENY | NO MOVE / NO MOVE | PASS x2 |

ACT-005 added shared-boundary unavailability:

| Servo 01 request | Servo 02 request | Boundary | Physical result | Result |
|---|---|---|---|---|
| ACCEPT | ACCEPT | unavailable | NO MOVE / NO MOVE | PASS |
| ACCEPT | ACCEPT | restored | MOVE / MOVE | PASS x2 |

For the full matrix:

`docs/TEST_MATRIX.md`

---

# Test Launchers

Publication launchers are under:

`tests/`

They cover:

    act001_single_accept.py
    act001_single_deny.py
    act001_single_stale.py
    act001_single_outage.py
    act002_two_endpoint_mixed_a.py
    act002_two_endpoint_mixed_b.py
    act003_two_endpoint_dual_accept.py
    act004_two_endpoint_dual_deny.py
    act005_two_endpoint_dual_outage.py

ACT-005 recovery intentionally reuses:

`act003_two_endpoint_dual_accept.py`

There is no duplicate ACT-005 recovery launcher.

See:

`tests/README.md`

---

# Evidence

Curated result summaries are under:

`evidence/`

Each ACT result file records the applicable:

- run IDs
- expected conditions
- observed decisions and reasons
- endpoint binding
- request latency
- actuator telemetry
- physical observations
- original qualified source names
- original source hashes
- runtime evidence hashes
- evidence manifest
- supported conclusion
- claim boundary

The repository does not require publication of every raw timestamped bench artifact.

Original logs, manifests, videos, and qualification artifacts are retained in the local evidence archive.

See:

`evidence/README.md`

---

# Source Provenance

Repository filenames are intentionally cleaner than the original bench filenames.

Examples:

    esp32_xiao_servo_nuvl_archer.py
    → firmware/esp32_xiao_servo_nuvl.py

and:

    run_two_xiao_servo_mixed_a_archer.py
    → tests/act002_two_endpoint_mixed_a.py

Original qualified filenames and hashes are retained in the evidence documentation.

An original tested SHA-256 belongs to the exact original tested bytes.

If a repository copy was sanitized or otherwise modified, it is a derivative publication artifact and must not be represented as having the original qualification hash.

---

# Latency

The actuator tests used a:

`250 ms`

request-latency budget.

Qualified ACT-001 through ACT-005 request latencies remained within that budget.

The reported latency measures the NUVL request/authorization portion of the path.

It does not represent total physical-action latency.

In particular, it excludes the approximately one-second servo hold and does not independently measure:

- first physical motion
- time to commanded position
- mechanical settling
- total request-to-mechanical-completion time

Authorization latency and mechanical execution time remain separate quantities.

---

# Supported Conclusion

ACT-001 through ACT-005 support the following bounded conclusion:

> In the tested single- and two-endpoint paths, externally determined NUVL admissibility remained bound to physical actuator execution. Accepted decisions produced the intended observable physical actuation, while unauthorized, stale/replay/malformed-class, and boundary-unavailable outcomes did not enter the actuator path. Across two effectors, per-device authorization remained associated with the correct physical output through mixed outcomes, reversed outcomes, dual acceptance, dual denial, and shared-boundary outage/recovery.

The actuator work adds physical execution capability to the bench without transferring the admissibility decision to the actuator endpoint.

---

# Claim Boundary

The completed actuator series does not establish:

- exactly-once physical execution
- sensor-confirmed mechanical completion
- persistent actuator-side replay protection
- single-use physical authority across restart or power loss
- crash-safe physical execution accounting
- endpoint-enforced execution deadlines
- deterministic mechanical timing
- true parallel boundary processing
- arbitrary fleet scale
- exhaustive degraded-network behavior
- independent endpoint authorization
- safety-critical deployment readiness

The `stale_replay_malformed` ACT-001 case demonstrates non-actuation for that returned rejection class. It is not an independent persistent replay-state test.

ACT-003 demonstrates near-concurrent coordinated fan-in, not parallel boundary execution.

ACT-005 demonstrates a clean shared-boundary outage and recovery path, not every possible degraded or partially connected network condition.

See:

`docs/LIMITATIONS.md`

---

# Documentation

Detailed documentation:

- `docs/ACTUATOR_VALIDATION.md` — validation narrative and results
- `docs/TEST_MATRIX.md` — test conditions and outcome matrix
- `docs/HARDWARE_SETUP.md` — qualified physical configuration
- `docs/LIMITATIONS.md` — evidence and claim boundaries
- `tests/README.md` — launcher descriptions and provenance
- `firmware/README.md` — endpoint firmware and actuator gate
- `evidence/README.md` — curated evidence index

All results and conclusions apply **in the tested paths and configurations**.
