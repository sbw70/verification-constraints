# Actuator Evidence

This directory contains the curated evidence summaries for the NUVL physical actuator validation series, ACT-001 through ACT-005.

The actuator series extends the existing NUVL validation path from logical decisions and endpoint status indications to observable physical execution using Seeed XIAO ESP32-S3 endpoints and MG90S-class servo effectors.

The evidence is organized by test rather than as a dump of raw logs.

Original timestamped logs, manifests, videos, and other qualification artifacts are retained separately in the local evidence archive.

---

## Evidence Files

### `ACT001_RESULTS.md`

Single-effector physical decision binding.

Covers:

* accepted → physical movement
* unauthorized → no movement
* stale/replay/malformed rejection class → no movement
* external boundary unavailable → no movement
* boundary restoration → accepted physical movement resumes
* recovery without endpoint reset

Result:

**PASS — 7/7 documented executions**

Evidence manifest:

`act001_manifest_20260809_212704.txt`

Manifest SHA-256:

`39FB7C16B173DC0E231917C3D53667800027D083DB41B4459478381755CA1DF3`

---

### `ACT002_RESULTS.md`

Two-endpoint mixed physical outcome binding.

Covers both assignments:

```text id="cn6mmn"
servo-01 ACCEPT → MOVE
servo-02 DENY   → NO MOVE
```

and:

```text id="3mhb7e"
servo-01 DENY   → NO MOVE
servo-02 ACCEPT → MOVE
```

Each assignment was repeated twice.

Result:

**PASS — 4/4 coordinated runs**

Observed cross-actuation:

**0**

Evidence manifest:

`act002_manifest_20260809_222040.txt`

Manifest SHA-256:

`2FA9B0BF636D71D249B1A00BAE06E2ECED511776D30AC1C390864EEA6F7A7ABF`

---

### `ACT003_RESULTS.md`

Dual-admissible physical fan-in.

Both endpoints received:

`accepted / provider_admissible`

Both entered their respective actuator paths and both physical servos moved.

Result:

**PASS — 3/3 coordinated runs**

Evidence manifest:

`act003_manifest_20260809_223518.txt`

Manifest SHA-256:

`99C445E8A101A9C3A3FC7ED85247F0E5D313D1311E8566C9AA6889648D5DA0AC`

ACT-003 demonstrates near-concurrent coordinated physical fan-in. It does not establish true parallel boundary processing.

---

### `ACT004_RESULTS.md`

Dual-denied physical non-actuation.

Both endpoints received:

`denied / unauthorized_request`

Neither endpoint entered its actuator path.

Observed physical result:

`NO MOVE / NO MOVE`

Result:

**PASS — 2/2 coordinated runs**

Evidence manifest:

`act004_manifest_20260809_224512.txt`

Manifest SHA-256:

`EC44641D332CD48E6A9E0AECFEF8584D1BBC66183B0682A0BAEEC35F37AE5DA6`

---

### `ACT005_RESULTS.md`

Dual-effector shared-boundary outage and recovery.

During boundary outage, both endpoints requested accept but returned:

`unavailable / OSError(104,)`

Neither endpoint entered its actuator path.

Observed physical result:

`NO MOVE / NO MOVE`

After the external boundary was restored, neither XIAO endpoint was reset.

Two subsequent dual-accept runs produced:

`MOVE / MOVE`

Result:

**PASS**

* outage: PASS
* recovery: PASS x2

Evidence manifest:

`act005_manifest_20260809_230307.txt`

Manifest SHA-256:

`3B8B38F0D29FB0E189C88984202C7E85EF7B2975F20D83FB7921F3522C41AC1E`

---

# Series Summary

| Test    | Primary condition                                 | Runs | Physical result                            | Status |
| ------- | ------------------------------------------------- | ---: | ------------------------------------------ | ------ |
| ACT-001 | Single-effector accept/deny/stale/outage/recovery |    7 | Expected movement/non-movement in all runs | PASS   |
| ACT-002 | Mixed two-effector outcomes                       |    4 | Correct effector moved in all runs         | PASS   |
| ACT-003 | Dual accept                                       |    3 | MOVE / MOVE                                | PASS   |
| ACT-004 | Dual deny                                         |    2 | NO MOVE / NO MOVE                          | PASS   |
| ACT-005 | Shared-boundary outage                            |    1 | NO MOVE / NO MOVE                          | PASS   |
| ACT-005 | Shared-boundary recovery                          |    2 | MOVE / MOVE                                | PASS   |

Total documented coordinated executions represented by the evidence summaries:

**19**

Documented PASS results:

**19/19**

---

# Two-Effector Decision Matrix

ACT-002 through ACT-004 exercised all four basic two-endpoint accept/deny combinations.

| Servo 01 | Servo 02 | Expected physical result | Observed |
| -------- | -------- | ------------------------ | -------- |
| ACCEPT   | DENY     | MOVE / NO MOVE           | PASS x2  |
| DENY     | ACCEPT   | NO MOVE / MOVE           | PASS x2  |
| ACCEPT   | ACCEPT   | MOVE / MOVE              | PASS x3  |
| DENY     | DENY     | NO MOVE / NO MOVE        | PASS x2  |

ACT-005 added shared authorization-boundary unavailability:

| Servo 01 request | Servo 02 request | Boundary    | Expected physical result | Observed |
| ---------------- | ---------------- | ----------- | ------------------------ | -------- |
| ACCEPT           | ACCEPT           | unavailable | NO MOVE / NO MOVE        | PASS     |
| ACCEPT           | ACCEPT           | restored    | MOVE / MOVE              | PASS x2  |

No cross-actuation was observed during the mixed-outcome tests.

---

# Qualified Actuator Firmware

Original tested source:

`esp32_xiao_servo_nuvl_archer.py`

Original tested size:

`9,790 bytes`

Original tested SHA-256:

`C29AD7BB8362BD532C62A87CE5D8BE3ED30C25E4543FF52A2CC98992E493AD84`

The same firmware hash was verified on both physical actuator endpoints.

The repository publication copy is:

`../firmware/esp32_xiao_servo_nuvl.py`

The original qualification hash above identifies the original tested source.

If the repository copy has been sanitized or otherwise modified, the original qualification hash must not be attributed to that modified copy.

---

# Evidence Model

The actuator series uses several complementary forms of evidence.

## Coordinator/runtime evidence

The runtime logs record:

* run ID
* expected endpoint
* observed endpoint
* expected IP
* observed IP
* decision
* reason
* arrival status
* authorization/request latency
* actuator attempted state
* actuator completion state
* actuator error state
* overall oracle result

## Physical observation

Servo movement or non-movement was directly observed during the documented tests.

Selected runs were also captured on video.

Physical observation is distinct from software actuator telemetry.

## Hash evidence

Original qualified source files, runtime logs, and manifests were hashed with SHA-256.

The per-test result files identify the relevant original hashes.

## Pi-side evidence

Where applicable, Pi-side evidence records external boundary shutdown, restart, and health restoration.

---

# Raw Evidence Policy

This directory contains **curated evidence summaries**, not the complete raw evidence archive.

The original evidence archive includes items such as:

* timestamped runtime logs
* source launchers
* original actuator firmware
* evidence manifests
* Pi-side restart logs
* video files
* provisioning and qualification records

Those artifacts are retained locally.

The purpose of the repository evidence summaries is to make the test result, provenance, and claim boundary reviewable without publishing every raw bench artifact.

A curated raw-evidence package may be published separately if required.

---

# Source Naming and Hash Discipline

Repository source names may differ from the original qualified filenames.

For example:

Original qualified source:

`run_two_xiao_servo_mixed_a_archer.py`

Repository copy:

`../tests/act002_two_endpoint_mixed_a.py`

These should not be treated as automatically hash-equivalent.

The rule for this repository is:

> An original tested hash belongs to the exact original tested bytes.

If a source is:

* renamed only,
* sanitized,
* reformatted,
* commented,
* configuration-modified,
* or otherwise changed,

its publication status and hash must be represented accurately.

A modified publication copy must receive its own hash if one is published.

Do not attach an original qualification hash to modified bytes.

---

# Physical Evidence Boundary

The endpoint firmware reports:

* `actuator_attempted`
* `actuator_command_completed`
* `actuator_error`

These fields provide software evidence about entry into and completion of the actuator routine.

They are not independent mechanical sensors.

`actuator_command_completed=True`

means the software actuator command completed without a reported error.

It does not independently prove final shaft position or mechanical completion.

Physical movement was separately observed during the documented tests.

No independent encoder, position sensor, or electrical signal witness was used during ACT-001 through ACT-005.

---

# Latency Boundary

Reported `elapsed_ms` values describe the NUVL request/authorization portion of the tested path.

They are captured before completion of the approximately one-second servo hold.

Therefore, values such as:

`32 ms`

or:

`40 ms`

must not be represented as total physical-action latency.

The actuator evidence separates:

1. authorization/request latency,
2. software actuator invocation,
3. observed physical movement.

---

# Supported Series Conclusion

The curated ACT-001 through ACT-005 evidence supports the following bounded conclusion:

> In the tested single- and two-endpoint paths, externally determined NUVL admissibility remained bound to physical actuator execution. Accepted decisions produced the intended observable physical actuation, while unauthorized, stale/replay/malformed-class, and boundary-unavailable outcomes did not enter the actuator path. Across two effectors, per-device authorization remained associated with the correct physical output, including mixed outcomes, reversed outcomes, dual acceptance, dual denial, and shared-boundary outage/recovery.

The evidence also demonstrates that, in the tested shared-boundary outage path, external authorization unavailability did not become local fallback permission to actuate.

---

# What This Evidence Does Not Establish

The actuator evidence does not establish:

* exactly-once physical execution
* sensor-confirmed final mechanical position
* persistent actuator-side replay protection
* single-use physical authority across restart or power loss
* crash-safe physical execution accounting
* deterministic mechanical timing
* endpoint-enforced execution deadlines
* true parallel boundary processing
* arbitrary fleet scale
* exhaustive degraded-network behavior
* safety-critical deployment readiness

The `stale_replay_malformed` result in ACT-001 demonstrates non-actuation for that returned rejection class. It is not an independent persistent replay-state test.

ACT-003 demonstrates near-concurrent coordinated fan-in, not parallel boundary execution.

ACT-005 demonstrates a clean shared-boundary outage, not every possible degraded or partially connected network state.

For the full qualification boundaries, see:

`../docs/LIMITATIONS.md`

---

## Evidence Index

| File                | Purpose                                                                          |
| ------------------- | -------------------------------------------------------------------------------- |
| `ACT001_RESULTS.md` | Single-effector accept, deny, stale/replay/malformed-class, outage, and recovery |
| `ACT002_RESULTS.md` | Mixed two-effector physical outcome binding                                      |
| `ACT003_RESULTS.md` | Dual-admissible physical fan-in                                                  |
| `ACT004_RESULTS.md` | Dual-denied physical non-actuation                                               |
| `ACT005_RESULTS.md` | Shared-boundary outage and recovery                                              |

Supporting documentation:

`../docs/ACTUATOR_VALIDATION.md`

`../docs/TEST_MATRIX.md`

`../docs/HARDWARE_SETUP.md`

`../docs/LIMITATIONS.md`

All conclusions remain qualified by:

**in the tested paths and configurations.**

