# NUVL Physical Actuator Test Matrix

## Purpose

This document provides the test matrix for NUVL physical actuator validation ACT-001 through ACT-005.

The series evaluates whether externally determined NUVL outcomes remain correctly bound to physical execution across one and two ESP32-S3 servo endpoints.

The core execution rule under test was:

| NUVL outcome                      | Expected actuator behavior                   |
| --------------------------------- | -------------------------------------------- |
| `accepted / provider_admissible`  | Actuator invoked; physical movement expected |
| `denied / unauthorized_request`   | No actuator invocation; no movement          |
| `denied / stale_replay_malformed` | No actuator invocation; no movement          |
| `unavailable`                     | No actuator invocation; no movement          |

All conclusions apply **in the tested paths and configurations**.

---

# Test Configuration

## Physical endpoints

| Endpoint              | Hardware            | Servo signal | IP during testing |
| --------------------- | ------------------- | ------------ | ----------------- |
| `esp32-xiao-servo-01` | Seeed XIAO ESP32-S3 | D4 / GPIO5   | `192.168.0.81`    |
| `esp32-xiao-servo-02` | Seeed XIAO ESP32-S3 | D4 / GPIO5   | `192.168.0.186`   |

Both endpoints used MG90S-class servos and the same qualified actuator firmware.

Original tested firmware:

`esp32_xiao_servo_nuvl_archer.py`

Original tested SHA-256:

`C29AD7BB8362BD532C62A87CE5D8BE3ED30C25E4543FF52A2CC98992E493AD84`

---

# Oracle

For an accepted result, PASS required:

```text
decision=accepted
reason=provider_admissible
identity_ip_match=True
arrival_status=ON_TIME
actuator_attempted=True
actuator_command_completed=True
actuator_error=None
physical movement observed
```

For an unauthorized result, PASS required:

```text
decision=denied
reason=unauthorized_request
identity_ip_match=True
arrival_status=ON_TIME
actuator_attempted=False
actuator_command_completed=False
actuator_error=None
no physical movement observed
```

For the stale/replay/malformed rejection class, PASS required:

```text
decision=denied
reason=stale_replay_malformed
identity_ip_match=True
arrival_status=ON_TIME
actuator_attempted=False
actuator_command_completed=False
actuator_error=None
no physical movement observed
```

For boundary unavailability, PASS required:

```text
decision=unavailable
reason=<non-empty failure reason>
identity_ip_match=True
arrival_status=ON_TIME
actuator_attempted=False
actuator_command_completed=False
actuator_error=None
no physical movement observed
```

The test latency budget was:

`250 ms`

This budget applies to the NUVL request/authorization measurement. It does not represent total mechanical-action latency.

---

# ACT-001 — Single-Effector Decision Binding

Endpoint:

`esp32-xiao-servo-01`

## Matrix

| Condition                    | Run ID             | Decision / reason               | Latency | Actuator software state | Physical result | Result |
| ---------------------------- | ------------------ | ------------------------------- | ------: | ----------------------- | --------------- | ------ |
| Accept                       | `18ca4956db80a0f8` | accepted / provider_admissible  |   37 ms | attempted / completed   | MOVE            | PASS   |
| Accept                       | `18ca4960aa45fa38` | accepted / provider_admissible  |   33 ms | attempted / completed   | MOVE            | PASS   |
| Unauthorized                 | `18ca4a45df7242d0` | denied / unauthorized_request   |   37 ms | untouched               | NO MOVE         | PASS   |
| Stale/replay/malformed class | `18ca4b57c9fe064c` | denied / stale_replay_malformed |   33 ms | untouched               | NO MOVE         | PASS   |
| Boundary unavailable         | `18ca4c18d61aa52c` | unavailable / `OSError(104,)`   |   12 ms | untouched               | NO MOVE         | PASS   |
| Boundary restored            | `18ca4ce38d4a0470` | accepted / provider_admissible  |   33 ms | attempted / completed   | MOVE            | PASS   |
| Boundary restored            | `18ca4cea378ad3dc` | accepted / provider_admissible  |   35 ms | attempted / completed   | MOVE            | PASS   |

### ACT-001 result

**PASS**

Demonstrated:

* accepted → physical actuation
* unauthorized → no actuation
* stale/replay/malformed rejection class → no actuation
* boundary unavailable → no actuation
* boundary restored → accepted actuation resumed without endpoint reset

The `stale_replay_malformed` row validates the returned rejection class reaching the non-actuation path. It is not an independent persistent replay-state test.

---

# ACT-002 — Two-Endpoint Mixed Physical Binding

ACT-002 tested different outcomes at the two physical endpoints during the same coordinated run.

The assignment was then reversed.

## Run A contract

| Endpoint   | Requested mode | Expected decision | Expected physical result |
| ---------- | -------------- | ----------------- | ------------------------ |
| `servo-01` | accept         | accepted          | MOVE                     |
| `servo-02` | deny           | denied            | NO MOVE                  |

## Run A results

| Run ID             | Servo 01        | Servo 02         | Latencies  | Result |
| ------------------ | --------------- | ---------------- | ---------- | ------ |
| `18ca4f82e4a8881c` | accepted → MOVE | denied → NO MOVE | 34 / 36 ms | PASS   |
| `18ca4f8b3096f8dc` | accepted → MOVE | denied → NO MOVE | 35 / 33 ms | PASS   |

**Run A: PASS x2**

---

## Run B contract

| Endpoint   | Requested mode | Expected decision | Expected physical result |
| ---------- | -------------- | ----------------- | ------------------------ |
| `servo-01` | deny           | denied            | NO MOVE                  |
| `servo-02` | accept         | accepted          | MOVE                     |

## Run B results

| Run ID             | Servo 01         | Servo 02        | Latencies  | Result |
| ------------------ | ---------------- | --------------- | ---------- | ------ |
| `18ca4fbdae8e22b0` | denied → NO MOVE | accepted → MOVE | 32 / 35 ms | PASS   |
| `18ca4ff9446c0fc8` | denied → NO MOVE | accepted → MOVE | 33 / 34 ms | PASS   |

**Run B: PASS x2**

### ACT-002 result

**PASS x4**

Across all four runs:

* correct device identity
* correct IP binding
* correct decision/reason
* correct software actuator state
* all endpoint results ON_TIME
* latency range 32–36 ms
* no unexpected result keys
* physical result matched the intended per-device outcome
* no cross-actuation observed

Reversing admissibility reversed which physical servo moved.

---

# ACT-003 — Dual-Admissible Physical Fan-In

## Contract

Both physical endpoints request accept.

| Endpoint   | Expected decision              | Expected actuator     | Expected physical result |
| ---------- | ------------------------------ | --------------------- | ------------------------ |
| `servo-01` | accepted / provider_admissible | attempted / completed | MOVE                     |
| `servo-02` | accepted / provider_admissible | attempted / completed | MOVE                     |

## Results

| Run ID             | Servo 01        | Servo 02        | Latencies  | Result |
| ------------------ | --------------- | --------------- | ---------- | ------ |
| `18ca50afaf3fbcf8` | accepted → MOVE | accepted → MOVE | 32 / 33 ms | PASS   |
| `18ca50e0600de69c` | accepted → MOVE | accepted → MOVE | 34 / 33 ms | PASS   |
| `18ca50e481d5a234` | accepted → MOVE | accepted → MOVE | 36 / 34 ms | PASS   |

### ACT-003 result

**PASS x3**

Across all three runs:

* both endpoints accepted
* both actuator commands completed
* both servos physically moved
* correct identity/IP binding
* all results ON_TIME
* latency range 32–36 ms
* no unexpected result keys

ACT-003 demonstrates near-concurrent coordinated physical fan-in.

It does not establish true parallel boundary processing.

---

# ACT-004 — Dual-Denied Physical Non-Actuation

## Contract

Both physical endpoints request the unauthorized path.

| Endpoint   | Expected decision             | Expected actuator | Expected physical result |
| ---------- | ----------------------------- | ----------------- | ------------------------ |
| `servo-01` | denied / unauthorized_request | untouched         | NO MOVE                  |
| `servo-02` | denied / unauthorized_request | untouched         | NO MOVE                  |

## Results

| Run ID             | Servo 01         | Servo 02         | Latencies  | Result |
| ------------------ | ---------------- | ---------------- | ---------- | ------ |
| `18ca515fa21c11c4` | denied → NO MOVE | denied → NO MOVE | 37 / 38 ms | PASS   |
| `18ca5175764db848` | denied → NO MOVE | denied → NO MOVE | 34 / 32 ms | PASS   |

### ACT-004 result

**PASS x2**

Across both runs:

* both endpoints denied
* both reasons were `unauthorized_request`
* both actuator paths remained untouched
* neither servo moved
* identity/IP binding remained correct
* all results ON_TIME
* latency range 32–38 ms
* no unexpected result keys

---

# Two-Endpoint Authorization Matrix

ACT-002 through ACT-004 cover all four basic accept/deny combinations.

| Servo 01 authorization | Servo 02 authorization | Expected physical result | Repetitions | Result  |
| ---------------------- | ---------------------- | ------------------------ | ----------: | ------- |
| ACCEPT                 | DENY                   | MOVE / NO MOVE           |           2 | PASS x2 |
| DENY                   | ACCEPT                 | NO MOVE / MOVE           |           2 | PASS x2 |
| ACCEPT                 | ACCEPT                 | MOVE / MOVE              |           3 | PASS x3 |
| DENY                   | DENY                   | NO MOVE / NO MOVE        |           2 | PASS x2 |

Total coordinated runs across the basic two-endpoint accept/deny matrix:

**9**

Correct physical outcome:

**9/9**

Observed cross-actuation:

**0**

---

# ACT-005 — Shared-Boundary Outage and Recovery

## Outage contract

Both endpoints request accept while the shared external authorization boundary is unavailable.

| Endpoint   | Request | Expected decision | Expected actuator | Expected physical result |
| ---------- | ------- | ----------------- | ----------------- | ------------------------ |
| `servo-01` | accept  | unavailable       | untouched         | NO MOVE                  |
| `servo-02` | accept  | unavailable       | untouched         | NO MOVE                  |

Boundary port 8089 was confirmed unavailable before the test.

## Outage result

Run:

`18ca521127d5f1ac`

| Endpoint   | Observed result               | Latency | Actuator  | Physical result |
| ---------- | ----------------------------- | ------: | --------- | --------------- |
| `servo-01` | unavailable / `OSError(104,)` |   13 ms | untouched | NO MOVE         |
| `servo-02` | unavailable / `OSError(104,)` |   13 ms | untouched | NO MOVE         |

Identity/IP binding:

**PASS x2**

Arrival:

**ON_TIME x2**

Unexpected result keys:

**none**

Physical result:

**NO MOVE / NO MOVE**

**Outage result: PASS**

---

# ACT-005 Recovery Matrix

The boundary was restored.

Neither XIAO endpoint was reset.

The already-qualified ACT-003 dual-accept launcher was reused for the recovery verification.

| Run ID             | Servo 01        | Servo 02        | Latencies  | Endpoint reset | Result |
| ------------------ | --------------- | --------------- | ---------- | -------------- | ------ |
| `18ca5244856a83b8` | accepted → MOVE | accepted → MOVE | 40 / 38 ms | No             | PASS   |
| `18ca52542f653994` | accepted → MOVE | accepted → MOVE | 35 / 33 ms | No             | PASS   |

**Recovery: PASS x2**

ACT-005 therefore demonstrated:

`shared boundary unavailable → unavailable / unavailable → NO MOVE / NO MOVE`

followed by:

`boundary restored → accepted / accepted → MOVE / MOVE`

without resetting either actuator endpoint.

---

# Complete ACT-001 Through ACT-005 Matrix

| Test    | Condition                                     | Physical endpoints | Expected physical result | Runs | Result  |
| ------- | --------------------------------------------- | -----------------: | ------------------------ | ---: | ------- |
| ACT-001 | Accept                                        |                  1 | MOVE                     |    2 | PASS x2 |
| ACT-001 | Unauthorized                                  |                  1 | NO MOVE                  |    1 | PASS    |
| ACT-001 | Stale/replay/malformed class                  |                  1 | NO MOVE                  |    1 | PASS    |
| ACT-001 | Boundary unavailable                          |                  1 | NO MOVE                  |    1 | PASS    |
| ACT-001 | Boundary recovery                             |                  1 | MOVE                     |    2 | PASS x2 |
| ACT-002 | Accept / Deny                                 |                  2 | MOVE / NO MOVE           |    2 | PASS x2 |
| ACT-002 | Deny / Accept                                 |                  2 | NO MOVE / MOVE           |    2 | PASS x2 |
| ACT-003 | Accept / Accept                               |                  2 | MOVE / MOVE              |    3 | PASS x3 |
| ACT-004 | Deny / Deny                                   |                  2 | NO MOVE / NO MOVE        |    2 | PASS x2 |
| ACT-005 | Boundary unavailable / both requesting accept |                  2 | NO MOVE / NO MOVE        |    1 | PASS    |
| ACT-005 | Boundary restored / dual accept               |                  2 | MOVE / MOVE              |    2 | PASS x2 |

Total documented actuator-series executions represented in this matrix:

**19 coordinated test runs**

All documented runs:

**PASS**

---

# Evidence Manifests

| Test    | Manifest                              | SHA-256                                                            |
| ------- | ------------------------------------- | ------------------------------------------------------------------ |
| ACT-001 | `act001_manifest_20260809_212704.txt` | `39FB7C16B173DC0E231917C3D53667800027D083DB41B4459478381755CA1DF3` |
| ACT-002 | `act002_manifest_20260809_222040.txt` | `2FA9B0BF636D71D249B1A00BAE06E2ECED511776D30AC1C390864EEA6F7A7ABF` |
| ACT-003 | `act003_manifest_20260809_223518.txt` | `99C445E8A101A9C3A3FC7ED85247F0E5D313D1311E8566C9AA6889648D5DA0AC` |
| ACT-004 | `act004_manifest_20260809_224512.txt` | `EC44641D332CD48E6A9E0AECFEF8584D1BBC66183B0682A0BAEEC35F37AE5DA6` |
| ACT-005 | `act005_manifest_20260809_230307.txt` | `3B8B38F0D29FB0E189C88984202C7E85EF7B2975F20D83FB7921F3522C41AC1E` |

---

# Matrix Conclusion

ACT-001 through ACT-005 establish a consistent physical decision-binding matrix across the tested one- and two-effector configurations.

The observed mapping was:

```text
accepted                  → actuator invoked → physical movement
unauthorized              → actuator untouched → no movement
stale/replay/malformed    → actuator untouched → no movement
boundary unavailable      → actuator untouched → no movement
boundary restored         → accepted path restored → physical movement
```

Across the two-effector accept/deny matrix, all four authorization combinations were exercised and the physical result followed the per-device decision in every documented run.

The shared-boundary outage test additionally demonstrated that loss of the external authorization boundary did not convert requested action into fallback physical execution.

These results support physical authorization-to-execution binding **in the tested paths and configurations**.

They do not establish exactly-once physical execution, sensor-confirmed mechanical position, persistent actuator-side replay prevention, true parallel boundary processing, or safety-critical deployment readiness.

