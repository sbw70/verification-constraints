# ESP-LOCAL-008 Coordinator

## Purpose

The ESP-LOCAL-008 coordinator presents frozen, provider-signed authorities to selected endpoints and records the resulting endpoint verdict together with independent witness state.

ESP-LOCAL-008 tests signed target binding:

> A valid provider-issued authority scoped to one endpoint must be rejected by another endpoint at the target-identity gate before persistent authority state is consulted or modified and before a physical control signal is emitted.

Correctly targeted authorities provide the positive control: they must be accepted by the intended endpoint, durably consumed, and cross the physical control-signal boundary once.

The provider authority model is unchanged. Enforcement may transport, verify, and enforce provider-issued authority, but cannot originate or enlarge it.

## Coordinator

Primary script:

    esp_local_008_presenter.py

The presenter:

- selects a frozen authority artifact;
- selects a target endpoint;
- reads the exact frozen request bytes;
- recomputes the authority ID from the canonical authority bytes;
- verifies the computed authority ID against the frozen expected ID;
- brackets the presentation with independent witness START / STOP control;
- sends the authority to the selected endpoint;
- records the endpoint response;
- records pre-run and post-run witness status;
- compares the observed verdict with the expected verdict;
- writes a machine-readable JSON evidence record.

The presenter does not create or modify provider authority.

## Endpoint Configuration

    servo1
      identity: esp32-xiao-servo-01
      host:     192.168.0.81
      port:     19081

    servo2
      identity: esp32-xiao-servo-02
      host:     192.168.0.186
      port:     19081

Endpoint identity is the scored identity.

COM-port assignments are bench interfaces and are not treated as endpoint identity.

## Independent Witness

    identity:     esp32-witness-007
    host:         192.168.0.216
    control port: 19072
    protocol:     UDP
    capture:      RMT RX

Physical signal mapping:

    GPIO4 -> Servo #2 signal
    GPIO5 -> Servo #1 signal

The witness has no provider-authority role.

Its purpose is to independently observe whether a servo-control signal crossed the physical execution boundary.

The witness records capture readiness, selected GPIO, pulse count, burst count, queue depth, capture overflow count, capture truncation count, capture error count, run identifier, and run evidence digest.

A witnessed PWM/control-signal burst is not equivalent to independent measurement of mechanical servo-shaft displacement.

## Frozen Authorities

### X2

Scope:

    esp32-xiao-servo-01

Authority ID:

    0acbe0f43890299440c0f85b0b8a2c27e5cc38268a746f9bf296b765949f2710

Used for the final Servo1-scoped to Servo2 wrong-target denial.

### Y2

Scope:

    esp32-xiao-servo-02

Authority ID:

    3ba6239d703d5ba203be2069f1c4c3fc89c27e63cff0b59be6977883ca654519

Used for the Servo2 correct-target positive case.

### X3

Scope:

    esp32-xiao-servo-01

Authority ID:

    5222af8445ee67ba8712f2469c91449a841c777cb40b9395d22c9bb1f30388ef

Used for the replacement Servo1 correct-target positive case with the witness configured on GPIO5.

### Y3

Scope:

    esp32-xiao-servo-02

Authority ID:

    2c7ded33c6d5cc142c6f4ba91c04add1803fc361d00f34b9d288b3bb67f711fa

Used for the replacement Servo2-scoped to Servo1 wrong-target case with the witness configured on GPIO5.

## Expected Verdict Semantics

The `--expect` argument scores against the actual endpoint result.

Accepted cases use:

    --expect accepted

Denied cases use the specific denial reason:

    --expect target_id_mismatch

For a denial, the presenter scores a match only when the response status is `denied` and the response reason equals the expected denial reason.

Therefore:

    --expect denied

is not equivalent to:

    --expect target_id_mismatch

This distinction matters for retained evidence from `Y3_S1_DENY_001`, where the DUT produced the correct `target_id_mismatch` denial but the presenter invocation supplied the generic string `denied`, producing runner-side `scored_match:false`.

The original evidence is retained unmodified.

## Final Matrix

| Run | Authority Scope | Target | Expected Result | Physical Witness |
|---|---|---|---|---|
| `X2_S2_DENY_001` | Servo1 | Servo2 | `target_id_mismatch` | GPIO4, zero pulses / zero bursts |
| `Y3_S1_DENY_001` | Servo2 | Servo1 | `target_id_mismatch` | GPIO5, zero pulses / zero bursts |
| `X3_S1_ACCEPT_001` | Servo1 | Servo1 | `accepted` | GPIO5, 49 pulses / 1 burst |
| `Y2_S2_ACCEPT_001` | Servo2 | Servo2 | `accepted` | GPIO4, 49 pulses / 1 burst |

All final witness captures completed with zero capture overflow, truncation, and error counts.

## Wrong-Target Acceptance Criteria

A wrong-target presentation supports PASS only when the evidence shows:

1. provider signature validation succeeded;
2. semantic admissibility succeeded;
3. the endpoint rejected the request with `008_DENY_TARGET_ID_MISMATCH`;
4. no persistent authority-state success marker followed the target denial;
5. no PWM command boundary was crossed;
6. the target endpoint's own persistent state remained byte-for-byte unchanged;
7. the independent witness observed zero target-line pulses and zero bursts.

Representative endpoint sequence:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_DENY_TARGET_ID_MISMATCH
    008_CLIENT_COMPLETE ... result=target_id_mismatch

The target gate is evaluated before persistent authority-state access.

## Correct-Target Acceptance Criteria

A correct-target presentation supports PASS only when the endpoint log shows:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_TARGET_ID_MATCH
    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN
    008_PWM_COMMAND_END
    008_ACCEPT_EXECUTED

The persistent-state readback must also confirm durable transition from UNSPENT to SPENT.

The independent witness must record one corresponding servo-control burst with no capture faults.

## Evidence Output

Each presenter run writes a JSON record named:

    ESP_LOCAL_008_PRESENTER_<RUN_ID>_<TIMESTAMP>.json

The record includes authority label, authority ID, target identity, target host and port, expected verdict, endpoint response, scoring result, timing data, witness pre-run state, witness start result, witness stop result, and witness post-run state.

Endpoint serial evidence is stored separately under the test evidence directory.

Persistent-state and witness-partition images are preserved separately and hashed in the package manifest.

## Superseded Runs

### Y2_S1_DENY_001

The endpoint correctly rejected the Servo2-scoped authority at the Servo1 target gate and the target state remained unchanged.

The witness was configured on GPIO4, while Servo1's physical signal was connected to GPIO5.

The endpoint/state evidence remains valid, but the physical zero-signal observation was not made on the correct Servo1 signal line.

### X2_S1_ACCEPT_001

The endpoint correctly matched the target, validated UNSPENT state, durably transitioned the authority to SPENT, crossed one PWM command boundary, and returned accepted/executed.

The witness was configured on GPIO4 rather than Servo1 GPIO5.

`X3_S1_ACCEPT_001` replaced this run for the final independently witnessed Servo1 physical-boundary result.

## Control / Runner Artifact

### Y3_S1_DENY_002

The endpoint returned the expected `target_id_mismatch`, but witness control reported:

    run_already_active

The run is retained as a runner/control artifact and excluded from the final scored matrix.

## Result

ESP-LOCAL-008 demonstrated that provider-signed authority remained bound to its designated endpoint in the tested configuration.

Cross-target presentations were rejected at the target-identity gate before persistent authority-state access and before physical control-signal execution.

Correct-target presentations were accepted, durably consumed, and independently observed crossing the physical control-signal boundary once.
