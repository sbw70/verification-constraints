# ACT-002 — Two-Endpoint Mixed Physical Actuation Binding

## Status

**PASS x4**

ACT-002 validated per-device physical outcome binding across two XIAO ESP32-S3 actuator endpoints in the same coordinated run.

The test was intentionally performed in both directions:

* Run A: `servo-01` accepted and moved; `servo-02` denied and remained inactive.
* Run B: `servo-01` denied and remained inactive; `servo-02` accepted and moved.

Each assignment was repeated twice.

Across all four runs, the physical result followed the authorization result assigned to the correct endpoint. No cross-actuation was observed.

---

## Test Classification

ACT-002 is an **optional physical-effector integration of the existing NUVL architecture**, not an architecture change.

It maps to the physical actuator / distributed-effector use case.

ACT-002 adds evidence that per-device NUVL outcomes can remain correctly bound through to separate physical outputs during coordinated multi-endpoint execution.

It does not establish true parallel boundary processing, exactly-once physical execution, large-fleet behavior, or sensor-confirmed mechanical position.

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

Both endpoints were simultaneously present in the Raspberry Pi neighbor table as:

`REACHABLE`

Both endpoints used the same external boundary/coordinator path.

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

The firmware hash was verified on both XIAO endpoints.

Endpoint identity remained separate through:

`device_id.txt`

---

# Run A — Servo 01 Accept / Servo 02 Deny

## Contract

Expected mapping:

`esp32-xiao-servo-01 → accept → accepted / provider_admissible → MOVE`

`esp32-xiao-servo-02 → deny → denied / unauthorized_request → NO MOVE`

PASS required:

* correct endpoint identity
* correct IP binding
* correct decision and reason
* accepted endpoint enters the actuator path
* denied endpoint does not enter the actuator path
* accepted servo physically moves
* denied servo physically remains inactive
* both results ON_TIME
* both latencies within the 250 ms request budget
* no unexpected result keys

---

## Run A — Execution 1

Run ID:

`18ca4f82e4a8881c`

### Servo 01

Endpoint:

`esp32-xiao-servo-01`

Observed:

* decision: `accepted`
* reason: `provider_admissible`
* latency: `34 ms`
* identity/IP binding correct
* `actuator_attempted=True`
* `actuator_command_completed=True`
* actuator command completed
* physical movement observed

### Servo 02

Endpoint:

`esp32-xiao-servo-02`

Observed:

* decision: `denied`
* reason: `unauthorized_request`
* latency: `36 ms`
* identity/IP binding correct
* `actuator_attempted=False`
* `actuator_command_completed=False`
* actuator path untouched
* no physical movement observed

Both endpoint results:

`ON_TIME`

Result:

**PASS**

---

## Run A — Execution 2

Run ID:

`18ca4f8b3096f8dc`

### Servo 01

Observed:

* accepted / provider_admissible
* latency: `35 ms`
* actuator command completed
* physical movement observed

### Servo 02

Observed:

* denied / unauthorized_request
* latency: `33 ms`
* actuator untouched
* no physical movement observed

Identity/IP binding was correct for both endpoints.

Both results were ON_TIME.

Physical result:

`MOVE / NO MOVE`

Video was captured for this run.

Result:

**PASS**

---

## Run A Result

**PASS x2**

Both executions produced the same correctly bound mixed physical result:

`servo-01 → MOVE`

`servo-02 → NO MOVE`

---

# Run B — Servo 01 Deny / Servo 02 Accept

## Contract

The authorization assignment was reversed.

Expected mapping:

`esp32-xiao-servo-01 → deny → denied / unauthorized_request → NO MOVE`

`esp32-xiao-servo-02 → accept → accepted / provider_admissible → MOVE`

The purpose of the reversal was to determine whether the physical result followed per-device admissibility rather than remaining associated with one particular endpoint.

---

## Run B — Execution 1

Run ID:

`18ca4fbdae8e22b0`

### Servo 01

Observed:

* decision: `denied`
* reason: `unauthorized_request`
* latency: `32 ms`
* `actuator_attempted=False`
* `actuator_command_completed=False`
* no actuator call
* no physical movement observed

### Servo 02

Observed:

* decision: `accepted`
* reason: `provider_admissible`
* latency: `35 ms`
* `actuator_attempted=True`
* `actuator_command_completed=True`
* actuator command completed
* physical movement observed

Identity/IP binding was correct for both endpoints.

Both results were ON_TIME.

Unexpected results:

`none`

Result:

**PASS**

---

## Run B — Execution 2

Run ID:

`18ca4ff9446c0fc8`

### Servo 01

Observed:

* denied / unauthorized_request
* latency: `33 ms`
* no actuator call
* no physical movement observed

### Servo 02

Observed:

* accepted / provider_admissible
* latency: `34 ms`
* actuator command completed
* physical movement observed

Physical result:

`NO MOVE / MOVE`

Result:

**PASS**

---

## Run B Result

**PASS x2**

Both executions produced the reversed physical outcome:

`servo-01 → NO MOVE`

`servo-02 → MOVE`

---

# Result Matrix

| Assignment | Run ID             | Servo 01         | Servo 02         | Latencies  | Result |
| ---------- | ------------------ | ---------------- | ---------------- | ---------- | ------ |
| A          | `18ca4f82e4a8881c` | accepted → MOVE  | denied → NO MOVE | 34 / 36 ms | PASS   |
| A          | `18ca4f8b3096f8dc` | accepted → MOVE  | denied → NO MOVE | 35 / 33 ms | PASS   |
| B          | `18ca4fbdae8e22b0` | denied → NO MOVE | accepted → MOVE  | 32 / 35 ms | PASS   |
| B          | `18ca4ff9446c0fc8` | denied → NO MOVE | accepted → MOVE  | 33 / 34 ms | PASS   |

Total coordinated runs:

**4**

Correct per-device physical outcomes:

**4/4**

Observed cross-actuation:

**0**

Latency range:

`32–36 ms`

All endpoint results:

`ON_TIME`

---

# Source Launchers

## Run A

Original source:

`run_two_xiao_servo_mixed_a_archer.py`

Size:

`5,904 bytes`

SHA-256:

`5B4E661CB1B53F7B8414C4A93B18A6129486D7E59EFE35D35C46848D2628A8E5`

Contract:

`servo-01 → accept → MOVE`

`servo-02 → deny → NO MOVE`

---

## Run B

Original source:

`run_two_xiao_servo_mixed_b_archer.py`

Size:

`5,904 bytes`

SHA-256:

`EE8C86604E3A242EC56AFF250C218C63A59B193775C4CF46483A8D728AA98E28`

Contract:

`servo-01 → deny → NO MOVE`

`servo-02 → accept → MOVE`

---

# Runtime Evidence

## Run A

`act002_mixed_a_20260809_220636.log`

Size:

`2,212 bytes`

SHA-256:

`0700399D57F7CD6BECE3918843A66CA6DA64C2BF9F39E6B376A11725BA10A4CC`

Result:

**PASS**

---

`act002_mixed_a_20260809_220728.log`

Size:

`2,212 bytes`

SHA-256:

`C524A5F0EB8FAF2D377532B2A1739CC42335DAF967DD037627FF72FEEB16DB56`

Result:

**PASS**

Video captured.

---

## Run B

`act002_mixed_b_20260809_221101.log`

Size:

`2,212 bytes`

SHA-256:

`46A75DFC827732CD707822270B12C4589A0F8A8F7554C12E654837DA2146C15D`

Result:

**PASS**

---

`act002_mixed_b_20260809_221531.log`

Size:

`2,212 bytes`

SHA-256:

`E4D4A509DCDCF2F390A6EF0A9F3AE68794F284C290C4A3B557239D072B306F1B`

Result:

**PASS**

---

# Evidence Manifest

Manifest:

`act002_manifest_20260809_222040.txt`

Original path:

`C:\Users\holiw\esp32-main\act002_manifest_20260809_222040.txt`

Size:

`760 bytes`

SHA-256:

`2FA9B0BF636D71D249B1A00BAE06E2ECED511776D30AC1C390864EEA6F7A7ABF`

The manifest closes the local ACT-002 evidence set.

---

# Supported Conclusion

ACT-002 supports the following bounded conclusion:

> In the tested two-endpoint path, externally determined authorization outcomes remained bound to the correct physical effector. Reversing which endpoint was admissible reversed which servo moved, while the denied endpoint remained physically inactive.

The reversal is material because both physical endpoints demonstrated both sides of the execution boundary:

`servo-01 → accepted and moved`

`servo-01 → denied and remained inactive`

`servo-02 → accepted and moved`

`servo-02 → denied and remained inactive`

The observed physical result therefore followed per-device admissibility rather than a fixed endpoint assignment.

---

# What ACT-002 Adds

ACT-001 demonstrated physical decision binding at one endpoint.

ACT-002 extends that evidence to two separate physical outputs during coordinated execution.

The new supported property is:

**per-device physical outcome binding across separate effectors**

Specifically, the test demonstrated:

* distinct endpoint identities
* distinct physical effectors
* different authorization outcomes in the same coordinated run
* correct outcome-to-device association
* correct physical outcome-to-device association
* reversal of the admissible endpoint
* corresponding reversal of physical movement
* no observed cross-actuation

---

# Claim Boundary

ACT-002 does not demonstrate:

* true parallel boundary processing
* exactly-once physical execution
* persistent actuator replay resistance
* large-fleet physical scaling
* independent mechanical position sensing
* deterministic mechanical completion time
* endpoint-enforced execution deadlines
* exhaustive concurrency behavior
* safety-critical deployment readiness

The tests used two physical endpoints and four coordinated mixed-outcome executions.

No cross-actuation was observed in those runs. This is evidence for the tested configuration, not proof that cross-assignment is impossible under every possible fleet size, timing condition, or fault state.

Reported latency values represent the NUVL request/authorization portion of the tested path and exclude the servo hold and mechanical completion interval.

All conclusions apply **in the tested paths and configurations**.

