# ESP-LOCAL-008 Coordinator

## Purpose

The ESP-LOCAL-008 coordinator presents frozen, provider-signed authorities to selected endpoints and records the resulting endpoint verdict together with independent witness state.

ESP-LOCAL-008 tests signed target binding:

> A valid provider-issued authority scoped to one endpoint must be rejected by another endpoint at the target-identity gate before persistent authority state is consulted or modified and before a physical control signal is emitted.

Correctly targeted authorities provide the positive control: they must be accepted by the intended endpoint, durably consumed, and cross the physical control-signal boundary once.

The provider authority model is unchanged. Enforcement may transport, verify, and enforce provider-issued authority, but cannot originate or enlarge it.

## Repository Layout

The coordinator package contains:

    coordinator/
    |-- README.md
    `-- esp_local_008_presenter.py

Frozen authority artifacts used by the presenter are stored separately under:

    provider/
    `-- authorities/
        |-- ESP_LOCAL_008_AUTH_X2.txt
        |-- ESP_LOCAL_008_AUTH_X2_REQUEST.json
        |-- ESP_LOCAL_008_AUTH_Y2.txt
        |-- ESP_LOCAL_008_AUTH_Y2_REQUEST.json
        |-- ESP_LOCAL_008_AUTH_X3.txt
        |-- ESP_LOCAL_008_AUTH_X3_REQUEST.json
        |-- ESP_LOCAL_008_AUTH_Y3.txt
        `-- ESP_LOCAL_008_AUTH_Y3_REQUEST.json

The publication-tree authority lookup therefore resolves request artifacts from:

    provider/authorities/

The presenter does not create or enlarge provider authority.

## Presenter

Primary script:

    esp_local_008_presenter.py

The presenter performs one authority presentation per invocation.

It:

- selects a frozen authority artifact;
- selects one target endpoint;
- reads the exact frozen request bytes;
- recomputes the authority ID from the canonical authority bytes;
- verifies the computed authority ID against the frozen expected ID;
- optionally brackets the presentation with independent witness START / STOP control;
- sends the authority to the selected endpoint;
- records the endpoint response;
- records pre-run and post-run witness state;
- compares the observed verdict with the requested expected verdict;
- writes a machine-readable JSON evidence record.

Live-mode execution requires confirmation of the computed authority ID before transmission.

Default rehearsal mode sends a deliberately malformed request that is rejected before the target gate and before authority-state access.

## Source Provenance Note

The checked-in presenter source contains comment text from the earlier X/Y planning stage of ESP-LOCAL-008.

Those comments describe the original planned three-step matrix using `AUTH-X` and `AUTH-Y`.

The final scored matrix did not use that original matrix as its final evidence set.

The final scored evidence uses:

    X2
    Y2
    X3
    Y3

The executable configuration in the presenter contains these frozen authorities and their final authority IDs.

The final evidence JSON records and endpoint logs are authoritative for scored execution.

Historical X/Y comments are retained as source provenance and are not the definition of the final scored matrix.

## Endpoint Configuration

Two XIAO ESP32-S3 endpoints participated in the final matrix.

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

The presenter controls an independent RMT capture witness over UDP.

    identity:     esp32-witness-007
    host:         192.168.0.216
    control port: 19072
    protocol:     UDP
    capture:      RMT RX

Physical signal mapping during the final matrix:

    GPIO4 -> Servo #2 signal
    GPIO5 -> Servo #1 signal

The witness has no provider-authority role.

Its function is to independently observe whether a servo-control signal crossed the physical execution boundary.

The witness reports:

- capture readiness;
- selected GPIO;
- pulse count;
- burst count;
- capture queue depth;
- capture overflow count;
- capture truncation count;
- capture error count;
- run identifier;
- run evidence digest.

A witnessed PWM/control-signal burst is evidence of a physical control signal. It is not an independent measurement of mechanical servo-shaft displacement.

## Frozen Authorities

### X2

Scope:

    esp32-xiao-servo-01

Authority ID:

    0acbe0f43890299440c0f85b0b8a2c27e5cc38268a746f9bf296b765949f2710

Final use:

    X2 -> Servo2

Expected result:

    target_id_mismatch

X2 was valid provider-issued authority for Servo1 and was presented to Servo2 to test wrong-target rejection.

### Y2

Scope:

    esp32-xiao-servo-02

Authority ID:

    3ba6239d703d5ba203be2069f1c4c3fc89c27e63cff0b59be6977883ca654519

Final use:

    Y2 -> Servo2

Expected result:

    accepted

Y2 provided the final correctly targeted positive case for Servo2.

### X3

Scope:

    esp32-xiao-servo-01

Authority ID:

    5222af8445ee67ba8712f2469c91449a841c777cb40b9395d22c9bb1f30388ef

Final use:

    X3 -> Servo1

Expected result:

    accepted

X3 replaced the earlier Servo1 positive case so the physical signal could be independently captured on the correct Servo1 witness line.

### Y3

Scope:

    esp32-xiao-servo-02

Authority ID:

    2c7ded33c6d5cc142c6f4ba91c04add1803fc361d00f34b9d288b3bb67f711fa

Final use:

    Y3 -> Servo1

Expected DUT result:

    target_id_mismatch

Y3 replaced the earlier Servo1 wrong-target physical-witness case so the Servo1 signal could be observed on the correct witness GPIO.

## Expected Verdict Semantics

The `--expect` argument is compared against the actual endpoint response.

Accepted cases use:

    --expect accepted

Denied cases are expected to use the specific denial reason:

    --expect target_id_mismatch

For an accepted expectation, the presenter scores:

    status == accepted

For a denial expectation, the presenter scores:

    status == denied

and:

    reason == expected denial reason

Therefore:

    --expect denied

is not equivalent to:

    --expect target_id_mismatch

This distinction produced a runner-side metadata mismatch in one retained final run.

## Final Matrix

| Run | Authority Scope | Target | DUT Result | Physical Witness |
|---|---|---|---|---|
| `X2_S2_DENY_001` | Servo1 | Servo2 | `target_id_mismatch` | GPIO4, 0 pulses / 0 bursts |
| `Y3_S1_DENY_001` | Servo2 | Servo1 | `target_id_mismatch` | GPIO5, 0 pulses / 0 bursts |
| `X3_S1_ACCEPT_001` | Servo1 | Servo1 | `accepted / executed` | GPIO5, 49 pulses / 1 burst |
| `Y2_S2_ACCEPT_001` | Servo2 | Servo2 | `accepted / executed` | GPIO4, 49 pulses / 1 burst |

All four final witness captures reported:

    capture_overflows:   0
    capture_truncations: 0
    capture_errors:      0

## X2_S2_DENY_001

Authority:

    AUTH-X2

Authority scope:

    esp32-xiao-servo-01

Target:

    esp32-xiao-servo-02

Presenter response:

    status: denied
    reason: target_id_mismatch
    scored_match: true

Witness:

    GPIO:      4
    pre pulse: 0
    pre burst: 0
    post pulse: 0
    post burst: 0

Witness stop digest:

    ffa3a7b598e55d871b1114dc77123e5e2674cafeec2ef858f89a2a595ce0b4a6

The endpoint log records:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_DENY_TARGET_ID_MISMATCH

No authority-state success marker, PWM command marker, or acceptance marker follows the target mismatch.

Servo2 persistent state remained byte-for-byte unchanged across the wrong-target presentation.

## Y3_S1_DENY_001

Authority:

    AUTH-Y3

Authority scope:

    esp32-xiao-servo-02

Target:

    esp32-xiao-servo-01

DUT response:

    status: denied
    reason: target_id_mismatch

Witness:

    GPIO:       5
    pre pulse:  0
    pre burst:  0
    post pulse: 0
    post burst: 0

Witness stop digest:

    8c1f95aa2acaec4c97cace8461892cab3c737e4651c134946a3ec9452694adeb

The endpoint log records:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_DENY_TARGET_ID_MISMATCH

Servo1 persistent state was byte-for-byte identical before and after the presentation.

### Presenter Scoring Metadata Caveat

The invocation supplied:

    --expect denied

instead of:

    --expect target_id_mismatch

The endpoint nevertheless returned the correct scored DUT behavior:

    status: denied
    reason: target_id_mismatch

Because the presenter compares denial expectations against the specific reason string, the resulting JSON contains:

    "scored_match": false

This is a presenter invocation metadata defect, not a DUT target-binding failure.

The original artifact is retained unmodified.

The run remains usable for the target-binding property because the independent evidence establishes:

- valid provider signature;
- semantic admissibility;
- explicit target-identity mismatch;
- unchanged persistent state;
- zero PWM/control-signal activity on the correct physical line.

## X3_S1_ACCEPT_001

Authority:

    AUTH-X3

Authority scope:

    esp32-xiao-servo-01

Target:

    esp32-xiao-servo-01

Presenter response:

    status: accepted
    reason: executed
    scored_match: true

Witness:

    GPIO:        5
    pre pulse:   0
    pre burst:   0
    post pulse:  49
    post burst:  1

Witness stop digest:

    1b7247e7f4639556b66a3db3f14c4054229cd724dfb180107f1b7b645124021d

The endpoint log records:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_TARGET_ID_MATCH
    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN
    008_PWM_COMMAND_END
    008_ACCEPT_EXECUTED

The authority was durably consumed before the PWM command boundary.

## Y2_S2_ACCEPT_001

Authority:

    AUTH-Y2

Authority scope:

    esp32-xiao-servo-02

Target:

    esp32-xiao-servo-02

Presenter response:

    status: accepted
    reason: executed
    scored_match: true

Witness:

    GPIO:        4
    pre pulse:   0
    pre burst:   0
    post pulse:  49
    post burst:  1

Witness stop digest:

    1756bacf8d53c0336137f78876e91a0f42a3d204441850c6c7263bf47447930b

The endpoint log records:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_TARGET_ID_MATCH
    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN
    008_PWM_COMMAND_END
    008_ACCEPT_EXECUTED

The authority was durably consumed before the PWM command boundary.

## Wrong-Target Acceptance Criteria

A wrong-target presentation supports the ESP-LOCAL-008 property only when the combined evidence shows:

1. provider signature validation succeeded;
2. semantic admissibility succeeded;
3. the endpoint rejected the request with `008_DENY_TARGET_ID_MISMATCH`;
4. no successful authority-state path followed the target denial;
5. no PWM command boundary was crossed;
6. the target endpoint's persistent state remained byte-for-byte unchanged;
7. the independent witness observed zero pulses and zero bursts on the correct target signal line.

Representative endpoint sequence:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_DENY_TARGET_ID_MISMATCH
    008_CLIENT_COMPLETE ... result=target_id_mismatch

The target gate is evaluated before persistent authority-state access.

## Correct-Target Acceptance Criteria

A correct-target presentation supports PASS only when the endpoint evidence shows:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_TARGET_ID_MATCH
    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN
    008_PWM_COMMAND_END
    008_ACCEPT_EXECUTED

The authority must transition durably from UNSPENT to SPENT before execution.

The independent witness must record one corresponding control-signal burst on the correct physical line with no capture overflow, truncation, or error.

## Evidence Output

Presenter evidence is written as:

    ESP_LOCAL_008_PRESENTER_<RUN_ID>_<TIMESTAMP>.json

Final presenter records are stored under:

    evidence/final/

Final endpoint serial logs are stored under:

    evidence/final/

Raw authority-state partition images are stored under:

    evidence/state/

Witness evidence-partition images are stored under:

    evidence/witness-images/

Earlier replaced cases are stored under:

    evidence/superseded/

Non-scored runner/control artifacts are stored under:

    evidence/controls/

The evidence JSON records include:

- test ID;
- run ID;
- live/rehearsal state;
- authority label;
- authority ID;
- target identity;
- target host and port;
- expected verdict;
- endpoint response;
- scoring result;
- timing data;
- witness pre-run status;
- witness START result;
- witness STOP result;
- witness post-run status.

## Superseded Runs

### Y2_S1_DENY_001

The endpoint correctly rejected the Servo2-scoped authority at the Servo1 target gate.

The target state remained unchanged.

The independent witness was configured on GPIO4, while Servo1's physical signal was connected to GPIO5.

The endpoint and state evidence remain valid, but the physical zero-signal observation was not made on the correct Servo1 signal line.

`Y3_S1_DENY_001` replaced this run for the final Servo1 wrong-target physical-witness result.

### X2_S1_ACCEPT_001

The endpoint correctly:

- matched the signed target;
- validated UNSPENT state;
- durably transitioned the authority to SPENT;
- crossed one PWM command boundary;
- returned accepted/executed.

The witness was configured on GPIO4 rather than the Servo1 GPIO5 signal line.

`X3_S1_ACCEPT_001` replaced this run for the final independently witnessed Servo1 positive result.

Superseded runs are retained for provenance and are not substituted for the final physical-witness matrix.

## Control / Runner Artifact

### Y3_S1_DENY_002

The presenter recorded:

    status: denied
    reason: target_id_mismatch

The presenter-side expected verdict matched in this control attempt.

Witness START control returned:

    run_already_active

The endpoint serial log for this control attempt was not successfully captured; the checked-in endpoint log is an empty placeholder.

Because the witness run was already active and the endpoint serial evidence is absent, `Y3_S1_DENY_002` is not part of the final scored matrix.

It is retained only as a runner/control artifact.

## Result

ESP-LOCAL-008 demonstrated signed endpoint directionality in the tested two-endpoint configuration.

Provider-signed authority scoped to one endpoint was rejected when presented to the other endpoint.

The rejection occurred at the target-identity gate before persistent authority-state access and before physical control-signal execution.

Correctly targeted authority was accepted, durably consumed, and independently observed crossing the corresponding physical control-signal boundary once.

The supported claim is limited to the tested property and configuration.
