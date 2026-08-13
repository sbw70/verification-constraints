# Actuator Test Launchers

This directory contains the publication copies of the Python launchers used for the NUVL physical actuator validation series, ACT-001 through ACT-005.

The launchers coordinate test conditions and evaluate returned endpoint results against the expected authorization and actuator behavior.

They are organized by test purpose rather than by the original local bench filenames.

---

## Test Files

### `act001_single_accept.py`

Single-endpoint accepted-path test.

Expected result:

```text
decision=accepted
reason=provider_admissible
actuator_attempted=True
actuator_command_completed=True
actuator_error=None
```

Expected physical behavior:

`MOVE`

Used for:

* initial ACT-001 accepted-path qualification
* ACT-001 post-outage recovery

Original qualified source:

`run_xiao_servo_accept_archer.py`

Original SHA-256:

`BBAB6EA69E6B6C13B0CD7B6BC25FB52A6D0EFCC075652F0920B765956DAF2C3E`

---

### `act001_single_deny.py`

Single-endpoint unauthorized-path test.

Expected result:

```text
decision=denied
reason=unauthorized_request
actuator_attempted=False
actuator_command_completed=False
actuator_error=None
```

Expected physical behavior:

`NO MOVE`

Original qualified source:

`run_xiao_servo_deny_archer.py`

Original size:

`4,374 bytes`

Original SHA-256:

`CED31874869DDD8C2B646746EB6660D29006901C60CBD3EEEFAB1F2804B7429C`

---

### `act001_single_stale.py`

Single-endpoint stale/replay/malformed rejection-class test.

Expected result:

```text
decision=denied
reason=stale_replay_malformed
actuator_attempted=False
actuator_command_completed=False
actuator_error=None
```

Expected physical behavior:

`NO MOVE`

Original qualified source:

`run_xiao_servo_stale_archer.py`

Original size:

`4,393 bytes`

Original SHA-256:

`0ECE21790A1604E2527889544669893CAFCD262A2862AC1199A092F09E654891`

This test verifies non-actuation for the returned `stale_replay_malformed` rejection class.

It is not an independent persistent replay-state test.

---

### `act001_single_outage.py`

Single-endpoint external-boundary-unavailable test.

The endpoint requests the accepted path while the external NUVL boundary is deliberately unavailable.

Expected result:

```text
decision=unavailable
reason=<non-empty failure reason>
actuator_attempted=False
actuator_command_completed=False
actuator_error=None
```

Expected physical behavior:

`NO MOVE`

Original qualified source:

`run_xiao_servo_outage_archer.py`

Original size:

`4,410 bytes`

Original SHA-256:

`23CB242CECA50A4F756AF75A6625351FDC3C441C11E5DB58CF840B1A1FA179E8`

---

### `act002_two_endpoint_mixed_a.py`

Two-endpoint mixed-outcome test, assignment A.

Contract:

```text
servo-01 → accept → MOVE
servo-02 → deny   → NO MOVE
```

Original qualified source:

`run_two_xiao_servo_mixed_a_archer.py`

Original size:

`5,904 bytes`

Original SHA-256:

`5B4E661CB1B53F7B8414C4A93B18A6129486D7E59EFE35D35C46848D2628A8E5`

Qualified executions:

**PASS x2**

---

### `act002_two_endpoint_mixed_b.py`

Two-endpoint mixed-outcome test, assignment B.

This reverses the ACT-002 assignment:

```text
servo-01 → deny   → NO MOVE
servo-02 → accept → MOVE
```

Original qualified source:

`run_two_xiao_servo_mixed_b_archer.py`

Original size:

`5,904 bytes`

Original SHA-256:

`EE8C86604E3A242EC56AFF250C218C63A59B193775C4CF46483A8D728AA98E28`

Qualified executions:

**PASS x2**

Together, the ACT-002 launchers test whether physical execution follows per-device admissibility rather than remaining associated with one particular endpoint.

---

### `act003_two_endpoint_dual_accept.py`

Two-endpoint dual-admissible test.

Contract:

```text
servo-01 → accept → MOVE
servo-02 → accept → MOVE
```

Expected physical behavior:

`MOVE / MOVE`

Original qualified source:

`run_two_xiao_servo_dual_accept_archer.py`

Original size:

`5,914 bytes`

Original SHA-256:

`96BECFB0B85801674D5AEEF117A6B86826AF22F4B0EF82306530FBBD07B05137`

Qualified executions:

**PASS x3**

This launcher was also reused for ACT-005 recovery testing after the external boundary was restored.

There is intentionally no separate ACT-005 recovery launcher in this directory.

---

### `act004_two_endpoint_dual_deny.py`

Two-endpoint dual-denial test.

Contract:

```text
servo-01 → deny → NO MOVE
servo-02 → deny → NO MOVE
```

Expected physical behavior:

`NO MOVE / NO MOVE`

Original qualified source:

`run_two_xiao_servo_dual_deny_archer.py`

Original size:

`5,905 bytes`

Original SHA-256:

`21B65773B6085FE9868F02C9D8DB6BE8CC23A5E7159557939A39D96F83E7A29D`

Qualified executions:

**PASS x2**

---

### `act005_two_endpoint_dual_outage.py`

Two-endpoint shared-boundary-unavailable test.

Both endpoints request accept while the shared external NUVL boundary is deliberately unavailable.

Contract:

```text
servo-01 → request accept → boundary unavailable → NO MOVE
servo-02 → request accept → boundary unavailable → NO MOVE
```

Expected result for both endpoints:

```text
decision=unavailable
reason=<non-empty failure reason>
actuator_attempted=False
actuator_command_completed=False
actuator_error=None
```

Original qualified source:

`run_two_xiao_servo_dual_outage_archer.py`

Original size:

`5,769 bytes`

Original SHA-256:

`E66D54E33A20216B9E4F4CC1CF806C63B3F0D6A126C5512E46543500A96DCE96`

Qualified outage execution:

**PASS**

---

# Test Coverage

The launchers cover the following physical decision matrix:

| Test           | Servo 01               | Servo 02    | Expected physical result |
| -------------- | ---------------------- | ----------- | ------------------------ |
| ACT-001 accept | ACCEPT                 | —           | MOVE                     |
| ACT-001 deny   | DENY                   | —           | NO MOVE                  |
| ACT-001 stale  | STALE/REPLAY/MALFORMED | —           | NO MOVE                  |
| ACT-001 outage | UNAVAILABLE            | —           | NO MOVE                  |
| ACT-002 A      | ACCEPT                 | DENY        | MOVE / NO MOVE           |
| ACT-002 B      | DENY                   | ACCEPT      | NO MOVE / MOVE           |
| ACT-003        | ACCEPT                 | ACCEPT      | MOVE / MOVE              |
| ACT-004        | DENY                   | DENY        | NO MOVE / NO MOVE        |
| ACT-005        | UNAVAILABLE            | UNAVAILABLE | NO MOVE / NO MOVE        |

ACT-003 is additionally reused after ACT-005 boundary restoration to verify:

```text
boundary restored
→ ACCEPT / ACCEPT
→ MOVE / MOVE
```

---

# Launcher Responsibilities

The test launchers are responsible for coordinating and evaluating the test condition.

Depending on the test, they verify fields including:

* expected endpoint identity
* observed endpoint identity
* expected IP
* observed IP
* decision
* reason
* arrival status
* request latency
* actuator attempted state
* actuator completion state
* actuator error state
* unexpected result keys

The launchers do not independently measure servo shaft position.

Physical movement or non-movement was observed separately during qualification.

---

# Latency Oracle

The actuator tests used a request-latency budget of:

`250 ms`

Results within that budget were classified:

`ON_TIME`

The measured latency represents the NUVL request/authorization portion of the tested path.

It does **not** include the complete servo movement or approximately one-second actuator hold.

Therefore, launcher-reported `elapsed_ms` must not be interpreted as total physical-action latency.

---

# Physical Oracle

For accepted outcomes, the expected software state is:

```text
actuator_attempted=True
actuator_command_completed=True
actuator_error=None
```

The corresponding expected physical observation is:

`MOVE`

For non-accepted outcomes, the expected software state is:

```text
actuator_attempted=False
actuator_command_completed=False
actuator_error=None
```

The corresponding expected physical observation is:

`NO MOVE`

`actuator_command_completed=True` indicates that the software actuator routine completed without a reported error.

It is not an independent measurement of final mechanical position.

---

# Boundary Outage Tests

The outage launchers do not stop or restart the external NUVL boundary themselves.

Boundary state is a controlled test precondition.

For the qualified ACT-001 and ACT-005 outage tests, port 8089 was confirmed unavailable before the launcher was executed.

This distinction is deliberate:

* the launcher evaluates endpoint behavior;
* boundary shutdown establishes the external failure condition.

Recovery is likewise verified only after boundary health has been restored.

---

# Source Provenance

The filenames in this directory are publication names.

They differ from the original local qualification filenames to make the repository structure easier to understand.

Mapping:

| Repository file                      | Original qualified source                  |
| ------------------------------------ | ------------------------------------------ |
| `act001_single_accept.py`            | `run_xiao_servo_accept_archer.py`          |
| `act001_single_deny.py`              | `run_xiao_servo_deny_archer.py`            |
| `act001_single_stale.py`             | `run_xiao_servo_stale_archer.py`           |
| `act001_single_outage.py`            | `run_xiao_servo_outage_archer.py`          |
| `act002_two_endpoint_mixed_a.py`     | `run_two_xiao_servo_mixed_a_archer.py`     |
| `act002_two_endpoint_mixed_b.py`     | `run_two_xiao_servo_mixed_b_archer.py`     |
| `act003_two_endpoint_dual_accept.py` | `run_two_xiao_servo_dual_accept_archer.py` |
| `act004_two_endpoint_dual_deny.py`   | `run_two_xiao_servo_dual_deny_archer.py`   |
| `act005_two_endpoint_dual_outage.py` | `run_two_xiao_servo_dual_outage_archer.py` |

---

# Hash Discipline

Original SHA-256 values in this README identify the exact original qualified source files.

They do not automatically identify the repository copies.

If a publication copy has been:

* sanitized,
* edited,
* reformatted,
* configuration-modified,
* or otherwise changed,

it is a different artifact and should receive its own hash.

A filename change alone does not alter file contents, but any content modification does.

Do not attach an original qualification hash to modified bytes.

---

# Reproduction Notes

Before using these launchers, the corresponding actuator endpoints must already be:

* provisioned with distinct identities,
* running the actuator firmware,
* connected to the expected network,
* reachable through the coordinator path,
* independently verified to produce physical servo movement,
* connected to the intended external NUVL boundary.

The launchers assume the physical actuator path itself has already been qualified.

A failed servo, incorrect GPIO connection, incorrect endpoint identity, or unavailable network path can invalidate interpretation of the authorization test.

---

# Results

Detailed qualified results are documented under:

`../evidence/ACT001_RESULTS.md`

`../evidence/ACT002_RESULTS.md`

`../evidence/ACT003_RESULTS.md`

`../evidence/ACT004_RESULTS.md`

`../evidence/ACT005_RESULTS.md`

The overall test matrix is documented at:

`../docs/TEST_MATRIX.md`

Hardware configuration:

`../docs/HARDWARE_SETUP.md`

Claim and test limitations:

`../docs/LIMITATIONS.md`

---

# Scope

These launchers support reproduction and review of the NUVL actuator validation paths.

They do not by themselves establish:

* exactly-once physical execution
* persistent physical replay protection
* sensor-confirmed mechanical position
* deterministic physical timing
* true parallel boundary processing
* arbitrary fleet scaling
* safety-critical actuator control

All qualification conclusions remain bounded to the documented test conditions and apply **in the tested paths and configurations**.

