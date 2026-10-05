# ESP-LOCAL-008 Evidence

## Purpose

This directory contains the retained evidence for ESP-LOCAL-008 signed endpoint-directionality testing.

ESP-LOCAL-008 tests the following property:

> Valid provider-issued authority for one endpoint must not become executable authority at another endpoint.

The final evidence set combines:

- frozen provider-signed authority artifacts;
- presenter JSON records;
- endpoint serial logs;
- raw endpoint authority-state partition images;
- independent RMT witness observations;
- raw witness evidence-partition images;
- retained superseded and control runs.

No single artifact is treated as sufficient by itself.

For a wrong-target case, the evidence must establish that the provider signature was valid, the request reached the explicit target gate, persistent authority state was not changed, and no physical control signal crossed the target line.

For a correct-target case, the evidence must establish target match, valid UNSPENT authority state, durable consumption before execution, one endpoint PWM execution path, and one independently observed physical control-signal burst.

## Directory Layout

        evidence/
    |-- README.md
    |
    |-- final/
    |   |-- ESP_LOCAL_008_PRESENTER_X2_S2_DENY_001_1790729436.json
    |   |-- ESP_LOCAL_008_PRESENTER_X3_S1_ACCEPT_001_1790732953.json
    |   |-- ESP_LOCAL_008_PRESENTER_Y2_S2_ACCEPT_001_1790730312.json
    |   |-- ESP_LOCAL_008_PRESENTER_Y3_S1_DENY_001_1790733844.json
    |   |-- ESP_LOCAL_008_X2_S2_DENY_001_ENDPOINT.log
    |   |-- ESP_LOCAL_008_X3_S1_ACCEPT_001_ENDPOINT.log
    |   |-- ESP_LOCAL_008_Y2_S2_ACCEPT_001_ENDPOINT.log
    |   `-- ESP_LOCAL_008_Y3_S1_DENY_001_ENDPOINT.log
    |
    |-- state/
    |   |-- SERVO1_POST_Y3_DENY.bin
    |   |-- SERVO1_PRE_Y3_DENY.bin
    |   |-- SERVO1_X3_AFTER_ACCEPT.bin
    |   |-- SERVO1_X3_STATE_CHECK.bin
    |   |-- SERVO2_Y2_AFTER_ACCEPT.bin
    |   |-- SERVO2_Y2_AFTER_X2_S2_DENY.bin
    |   `-- nuvl_state_servo2_postS1.bin
    |
    |-- witness-images/
    |   |-- ESP_LOCAL_008_WITNESS_AFTER_X3_PASS.bin
    |   |-- ESP_LOCAL_008_WITNESS_AFTER_Y2_PASS.bin
    |   |-- ESP_LOCAL_008_WITNESS_AFTER_Y3_DENY.bin
    |   `-- ESP_LOCAL_008_WITNESS_EVIDENCE_PRE_SCORE.bin
    |
    |-- superseded/
    |   |-- ESP_LOCAL_008_PRESENTER_X2_S1_ACCEPT_001_1790729763.json
    |   |-- ESP_LOCAL_008_PRESENTER_Y2_S1_DENY_001_1790729623.json
    |   |-- ESP_LOCAL_008_X2_S1_ACCEPT_001_ENDPOINT.log
    |   |-- ESP_LOCAL_008_Y2_S1_DENY_001_ENDPOINT.log
    |   |-- SERVO1_X2_AFTER_ACCEPT.bin
    |   `-- SERVO1_X2_AFTER_Y2_S1_DENY.bin
    |
    `-- controls/
        |-- ESP_LOCAL_008_PRESENTER_Y3_S1_DENY_002_1790734167.json
        `-- ESP_LOCAL_008_Y3_S1_DENY_002_ENDPOINT.log

The canonical scored endpoint logs are the copies under `final/`.


## Final Scored Matrix

| Run | Authority Scope | Target | Endpoint Result | State Result | Witness Result |
|---|---|---|---|---|---|
| `X2_S2_DENY_001` | Servo1 | Servo2 | `target_id_mismatch` | target state unchanged | GPIO4: 0 pulses / 0 bursts |
| `Y3_S1_DENY_001` | Servo2 | Servo1 | `target_id_mismatch` | target state unchanged | GPIO5: 0 pulses / 0 bursts |
| `X3_S1_ACCEPT_001` | Servo1 | Servo1 | `accepted / executed` | authority SPENT | GPIO5: 49 pulses / 1 burst |
| `Y2_S2_ACCEPT_001` | Servo2 | Servo2 | `accepted / executed` | authority SPENT | GPIO4: 49 pulses / 1 burst |

All four final witness captures reported:

    capture_overflows:   0
    capture_truncations: 0
    capture_errors:      0

## X2_S2_DENY_001

Authority:

    AUTH-X2

Signed target:

    esp32-xiao-servo-01

Presented to:

    esp32-xiao-servo-02

Presenter artifact:

    final/ESP_LOCAL_008_PRESENTER_X2_S2_DENY_001_1790729436.json

Endpoint artifact:

    final/ESP_LOCAL_008_X2_S2_DENY_001_ENDPOINT.log

Presenter response:

    status:       denied
    reason:       target_id_mismatch
    scored_match: true

The endpoint log records:

    008_CLIENT_REQUEST_RECEIVED
    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_DENY_TARGET_ID_MISMATCH
    008_CLIENT_COMPLETE ... result=target_id_mismatch

No successful authority-state marker, PWM command marker, or acceptance marker follows the target denial.

Independent witness:

    GPIO:        4
    pulse before: 0
    pulse after:  0
    burst before: 0
    burst after:  0

Witness run-file SHA-256:

    ffa3a7b598e55d871b1114dc77123e5e2674cafeec2ef858f89a2a595ce0b4a6

State artifact:

    state/SERVO2_Y2_AFTER_X2_S2_DENY.bin

The post-denial state image matched the previously recorded Servo2/Y2 UNSPENT baseline.

Recorded SHA-256:

    3CF11DBE7EA19F45E6194451AB2D5B1C94627FAAD6574A9BB566D7BEFC562E76

Result:

    PASS

The provider-signed Servo1 authority was rejected by Servo2 before the persistent-state path and before a physical Servo2 control signal was observed.

## Y3_S1_DENY_001

Authority:

    AUTH-Y3

Signed target:

    esp32-xiao-servo-02

Presented to:

    esp32-xiao-servo-01

Presenter artifact:

    final/ESP_LOCAL_008_PRESENTER_Y3_S1_DENY_001_1790733844.json

Endpoint artifact:

    final/ESP_LOCAL_008_Y3_S1_DENY_001_ENDPOINT.log

Endpoint response:

    status: denied
    reason: target_id_mismatch

The endpoint log records:

    008_CLIENT_REQUEST_RECEIVED
    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_DENY_TARGET_ID_MISMATCH
    008_CLIENT_COMPLETE ... result=target_id_mismatch

Independent witness:

    GPIO:         5
    pulse before: 0
    pulse after:  0
    burst before: 0
    burst after:  0

Witness run-file SHA-256:

    8c1f95aa2acaec4c97cace8461892cab3c737e4651c134946a3ec9452694adeb

State artifacts:

    state/SERVO1_PRE_Y3_DENY.bin
    state/SERVO1_POST_Y3_DENY.bin

The two checked-in state images are byte-identical.

Recorded SHA-256 for both:

    F2193B58041E1BFAFB2DB2A97463C4833AA2EAE196F84102DAB3A26DF6144873

### Presenter Metadata Caveat

The presenter invocation used:

    --expect denied

rather than:

    --expect target_id_mismatch

The DUT returned:

    status: denied
    reason: target_id_mismatch

The presenter scores denial cases against the specific expected reason string, so the JSON contains:

    "scored_match": false

This is a runner invocation metadata defect.

It does not indicate a target-binding failure.

The retained independent evidence shows:

- provider signature valid;
- semantic admissibility passed;
- explicit target-ID mismatch;
- no authority-state progression;
- byte-identical target state before and after;
- zero pulses on the correct Servo1 physical line;
- zero bursts on the correct Servo1 physical line;
- zero witness capture faults.

The original presenter JSON is retained unmodified.

Result:

    PASS for the tested target-binding property, with the presenter scoring caveat documented.

## X3_S1_ACCEPT_001

Authority:

    AUTH-X3

Signed target:

    esp32-xiao-servo-01

Presented to:

    esp32-xiao-servo-01

Presenter artifact:

    final/ESP_LOCAL_008_PRESENTER_X3_S1_ACCEPT_001_1790732953.json

Endpoint artifact:

    final/ESP_LOCAL_008_X3_S1_ACCEPT_001_ENDPOINT.log

Presenter response:

    status:       accepted
    reason:       executed
    scored_match: true

The endpoint log records:

    008_CLIENT_REQUEST_RECEIVED
    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_TARGET_ID_MATCH
    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN
    008_PWM_COMMAND_END
    008_ACCEPT_EXECUTED

Independent witness:

    GPIO:         5
    pulse before: 0
    pulse after:  49
    burst before: 0
    burst after:  1

Witness run-file SHA-256:

    1b7247e7f4639556b66a3db3f14c4054229cd724dfb180107f1b7b645124021d

Pre-execution state artifact:

    state/SERVO1_X3_STATE_CHECK.bin

Recorded SHA-256:

    588C34697B132DF7B82E79BC6A06A2DD973938A446AEFF199726CA5F0F4BEF36

Post-execution state artifact:

    state/SERVO1_X3_AFTER_ACCEPT.bin

Recorded SHA-256:

    F2193B58041E1BFAFB2DB2A97463C4833AA2EAE196F84102DAB3A26DF6144873

The raw post-execution state contains the earlier UNSPENT record and a later SPENT record for the same authority ID, consistent with NVS append/update behavior.

Result:

    PASS

The correctly targeted authority was accepted, durably consumed before execution, and independently observed as one physical control-signal burst.

## Y2_S2_ACCEPT_001

Authority:

    AUTH-Y2

Signed target:

    esp32-xiao-servo-02

Presented to:

    esp32-xiao-servo-02

Presenter artifact:

    final/ESP_LOCAL_008_PRESENTER_Y2_S2_ACCEPT_001_1790730312.json

Endpoint artifact:

    final/ESP_LOCAL_008_Y2_S2_ACCEPT_001_ENDPOINT.log

Presenter response:

    status:       accepted
    reason:       executed
    scored_match: true

The endpoint log records:

    008_CLIENT_REQUEST_RECEIVED
    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_TARGET_ID_MATCH
    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN
    008_PWM_COMMAND_END
    008_ACCEPT_EXECUTED

Independent witness:

    GPIO:         4
    pulse before: 0
    pulse after:  49
    burst before: 0
    burst after:  1

Witness run-file SHA-256:

    1756bacf8d53c0336137f78876e91a0f42a3d204441850c6c7263bf47447930b

State artifact:

    state/SERVO2_Y2_AFTER_ACCEPT.bin

Recorded SHA-256:

    A443EE0C0DEB23DE73A4F08F3A6BE20C5231DCFF131AE4A026C1A3D4DBF1C29B

The corresponding pre-execution Y2 baseline was:

    3CF11DBE7EA19F45E6194451AB2D5B1C94627FAAD6574A9BB566D7BEFC562E76

Result:

    PASS

The correctly targeted authority was accepted, durably consumed before execution, and independently observed as one physical control-signal burst.

## State Evidence

Raw endpoint authority-state images are 24 KiB dumps of the dedicated:

    nuvl_state

partition.

Relevant final evidence:

    SERVO1_X3_STATE_CHECK.bin
      Servo1 X3 state before scored X3 execution.

    SERVO1_X3_AFTER_ACCEPT.bin
      Servo1 state after successful X3 execution.

    SERVO1_PRE_Y3_DENY.bin
      Servo1 state immediately before the Y3 wrong-target presentation.

    SERVO1_POST_Y3_DENY.bin
      Servo1 state immediately after the Y3 wrong-target presentation.

    SERVO2_Y2_AFTER_X2_S2_DENY.bin
      Servo2/Y2 state after the X2 wrong-target presentation.

    SERVO2_Y2_AFTER_ACCEPT.bin
      Servo2 state after successful Y2 execution.

The Servo1 pre/post Y3 files are byte-identical.

The Servo2 X2-denial state matched the recorded pre-denial Y2 baseline.

These comparisons support the claim that wrong-target rejection occurred without consuming or replacing the target endpoint's own authority state.

### Supplemental Servo2 State Image

The directory also retains:

    nuvl_state_servo2_postS1.bin

This is an earlier Servo2 state capture retained with the test evidence.

It is not required for the four-case final scored matrix described above.

## Witness Evidence Images

The witness uses a dedicated 4 MiB SPIFFS evidence partition.

Raw partition images are retained under:

    witness-images/

### Pre-score image

    ESP_LOCAL_008_WITNESS_EVIDENCE_PRE_SCORE.bin

This preserves a pre-scored witness evidence snapshot.

### After Servo2 positive result

    ESP_LOCAL_008_WITNESS_AFTER_Y2_PASS.bin

Recorded SHA-256:

    BC1DC3B46758BAA7AE470F10557F638AB43584DBA191D410D978ADDC4D0935D1

### After Servo1 positive result

    ESP_LOCAL_008_WITNESS_AFTER_X3_PASS.bin

Recorded SHA-256:

    393FC673A41E9E99F0B7FE7994B818D04FBB551D151361B448415EF3745CECF1

### After Servo1 wrong-target result

    ESP_LOCAL_008_WITNESS_AFTER_Y3_DENY.bin

Recorded SHA-256:

    28AF6266B49C6C56605C91DC437D7886474AB663875A5143195FA82F7A500458

These are full raw images of the witness evidence partition rather than reconstructed summaries.

## Superseded Runs

The `superseded/` directory preserves two earlier Servo1 cases.

They are not discarded because they still contain valid endpoint-side evidence.

They are excluded from the final physical-witness matrix because the witness was monitoring the wrong physical line.

### Y2_S1_DENY_001

Authority:

    AUTH-Y2

Signed target:

    Servo2

Presented to:

    Servo1

Presenter result:

    status:       denied
    reason:       target_id_mismatch
    scored_match: true

Endpoint behavior correctly demonstrated wrong-target rejection.

The witness was configured on:

    GPIO4

while the Servo1 signal was physically connected to:

    GPIO5

The witness zero-signal result therefore does not establish absence of a Servo1 physical signal.

This run was replaced for the final physical criterion by:

    Y3_S1_DENY_001

### X2_S1_ACCEPT_001

Authority:

    AUTH-X2

Signed target:

    Servo1

Presented to:

    Servo1

Presenter result:

    status:       accepted
    reason:       executed
    scored_match: true

The endpoint log records a correct target match, durable spend, PWM execution, and acceptance.

The witness was configured on:

    GPIO4

while Servo1 was physically connected to:

    GPIO5

The zero-signal witness result therefore cannot be used as physical evidence for this positive case.

This run was replaced for the final physical criterion by:

    X3_S1_ACCEPT_001

Superseded state artifacts are retained as:

    superseded/SERVO1_X2_AFTER_Y2_S1_DENY.bin
    superseded/SERVO1_X2_AFTER_ACCEPT.bin

The superseded runs remain useful provenance but are not substituted for the final witness-corrected matrix.

## Control Artifact

The `controls/` directory contains:

    ESP_LOCAL_008_PRESENTER_Y3_S1_DENY_002_1790734167.json
    ESP_LOCAL_008_Y3_S1_DENY_002_ENDPOINT.log

The presenter recorded:

    expected:     target_id_mismatch
    status:       denied
    reason:       target_id_mismatch
    scored_match: true

The witness START reply was:

    ok:     false
    detail: run_already_active

The endpoint serial log was not successfully captured; the checked-in log is an empty one-byte placeholder.

The witness run therefore was not a clean fresh bracket, and endpoint serial corroboration is absent.

`Y3_S1_DENY_002` is retained as a runner/control artifact only.

It is not part of the final scored matrix.

## Evidence Interpretation

A wrong-target PASS requires agreement between independent evidence layers:

    provider artifact
        ->
    valid provider signature
        ->
    semantic admissibility
        ->
    target_id_mismatch
        ->
    no state progression
        ->
    no PWM execution marker
        ->
    zero physical target-line signal

A correct-target PASS requires:

    provider artifact
        ->
    valid provider signature
        ->
    semantic admissibility
        ->
    target match
        ->
    UNSPENT authority
        ->
    durable SPENT reread
        ->
    PWM command boundary
        ->
    accepted/executed
        ->
    one independent physical signal burst

This prevents a network-level response alone from being treated as proof of the physical result.

## Supported Result

The final ESP-LOCAL-008 evidence supports the following claim for the tested two-endpoint configuration:

> Provider-signed authority remained bound to its designated endpoint. Cross-target presentation was rejected before persistent authority-state access and before physical execution, while correctly targeted authority was accepted once, durably consumed, and independently observed at the physical control-signal boundary.

The physical evidence is evidence of the electrical control-signal boundary.

It is not an independent measurement of mechanical servo-shaft movement.

## Scope

This evidence package is specific to ESP-LOCAL-008 signed target binding.

It does not independently re-establish every property tested elsewhere in the ESP-LOCAL series.

In particular, it is not a substitute for the dedicated evidence packages covering:

- hostile-relay mutation;
- wrong-provider-key rejection;
- reboot persistence;
- power-loss persistence;
- corrupt or missing persistent state;
- crash windows;
- concurrent requester contention.

Superseded and control artifacts are retained for provenance and are explicitly separated from the final scored matrix.
