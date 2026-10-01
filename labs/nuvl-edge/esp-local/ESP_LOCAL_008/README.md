# ESP-LOCAL-008 Results

## Result

**PASS — final four-case directionality matrix, 2026-09-29 local / 2026-09-30 UTC**

ESP-LOCAL-008 tested whether valid provider-issued authority remained bound to the endpoint named in its signed `device_id`.

The final matrix exercised both directions across two ESP32-S3 servo endpoints:

    Servo1 authority -> Servo2
    Servo2 authority -> Servo1

and the corresponding correctly targeted positive cases:

    Servo1 authority -> Servo1
    Servo2 authority -> Servo2

Observed final result:

    wrong-target presentations:      2
    wrong-target denials:            2
    wrong-target state changes:      0
    wrong-target physical bursts:    0

    correct-target presentations:    2
    correct-target acceptances:      2
    correct-target durable spends:   2
    correct-target physical bursts:  2

The signed target-binding property held in both tested directions.

## Claim Under Test

ESP-LOCAL-008 asks:

> Can valid provider-issued authority scoped to endpoint X become executable authority at endpoint Y?

PASS requires more than a signature-valid denial.

For each wrong-target case, the evidence must show:

1. provider signature validation succeeded;
2. semantic admissibility succeeded;
3. the request was rejected specifically at the target-identity gate;
4. rejection occurred before successful persistent authority-state processing;
5. the target endpoint's persistent state remained unchanged;
6. the endpoint did not cross the PWM command boundary; and
7. the independent witness observed no target-line control signal.

For each correctly targeted positive case, the evidence must show:

1. provider signature validation succeeded;
2. semantic admissibility succeeded;
3. signed target identity matched the endpoint;
4. the local authority was UNSPENT;
5. the authority was durably transitioned to SPENT;
6. the SPENT state passed a fresh reread before execution;
7. one PWM command boundary was crossed;
8. the endpoint returned accepted/executed; and
9. the independent witness observed one corresponding physical control-signal burst.

The final matrix satisfied these criteria.

## Tested Endpoints

Servo #1:

    device_id:         esp32-xiao-servo-01
    IP:                192.168.0.81
    MAC:               1c:db:d4:45:11:e8
    TCP port:          19081
    endpoint PWM GPIO: 5

Servo #2:

    device_id:         esp32-xiao-servo-02
    IP:                192.168.0.186
    MAC:               1c:db:d4:45:10:a4
    TCP port:          19081
    endpoint PWM GPIO: 5

Independent witness:

    device_id:      esp32-witness-007
    IP:             192.168.0.216
    control port:   19072/UDP
    capture engine: RMT RX

Physical witness mapping:

    witness GPIO4 -> Servo #2 signal
    witness GPIO5 -> Servo #1 signal

## Tested Authority Model

All final authorities used:

    context:  esp_local_008
    action:   move_servo
    max_uses: 1

Trusted provider raw Ed25519 public key:

    48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1

The endpoint possessed the provider public verification material.

Authority generation remained on the provider side.

## Final Matrix

| Run | Authority Scope | Target | Endpoint Result | Persistent State | Witness |
|---|---|---|---|---|---|
| `X2_S2_DENY_001` | Servo1 | Servo2 | `target_id_mismatch` | unchanged | GPIO4: 0 pulses / 0 bursts |
| `Y3_S1_DENY_001` | Servo2 | Servo1 | `target_id_mismatch` | unchanged | GPIO5: 0 pulses / 0 bursts |
| `X3_S1_ACCEPT_001` | Servo1 | Servo1 | `accepted / executed` | SPENT | GPIO5: 49 pulses / 1 burst |
| `Y2_S2_ACCEPT_001` | Servo2 | Servo2 | `accepted / executed` | SPENT | GPIO4: 49 pulses / 1 burst |

All four final witness captures reported:

    capture_overflows:   0
    capture_truncations: 0
    capture_errors:      0

## AUTH-X2

AUTH-X2 was scoped to Servo1.

    device_id: esp32-xiao-servo-01
    nonce:     c52317c297a174ece0266bc04ba74639
    max_uses:  1

Authority ID:

    0acbe0f43890299440c0f85b0b8a2c27e5cc38268a746f9bf296b765949f2710

Final scored use:

    AUTH-X2 -> Servo2

This is the first wrong-target direction.

## X2_S2_DENY_001

AUTH-X2 was a valid provider-signed authority for:

    esp32-xiao-servo-01

It was presented to:

    esp32-xiao-servo-02

The endpoint recorded:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_DENY_TARGET_ID_MISMATCH
    008_CLIENT_COMPLETE ... result=target_id_mismatch

The presenter received:

    {"status":"denied","reason":"target_id_mismatch"}

Presenter scoring:

    expected:     target_id_mismatch
    scored_match: true

The endpoint did not record:

    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN
    008_PWM_COMMAND_END
    008_ACCEPT_EXECUTED

### Servo2 Persistent State

After the wrong-target X2 presentation, the Servo2/Y2 state image was:

    evidence/state/SERVO2_Y2_AFTER_X2_S2_DENY.bin

Recorded SHA-256:

    3CF11DBE7EA19F45E6194451AB2D5B1C94627FAAD6574A9BB566D7BEFC562E76

This matched the recorded Servo2/Y2 pre-denial state.

The wrong-target presentation therefore did not consume Servo2's legitimate local authority.

### Servo2 Physical Witness

Witness GPIO:

    4

Before:

    pulse_seq: 0
    burst_seq: 0

After:

    pulse_seq: 0
    burst_seq: 0

Capture health:

    overflows:   0
    truncations: 0
    errors:      0

Witness-computed run-file SHA-256:

    ffa3a7b598e55d871b1114dc77123e5e2674cafeec2ef858f89a2a595ce0b4a6

Observed physical result:

    zero target-line control bursts

### X2_S2_DENY_001 Disposition

    PASS

A correctly signed Servo1 authority did not become executable Servo2 authority.

The request was denied at the explicit signed-target gate before the successful persistent-state path and before physical control-signal execution.

## AUTH-Y2

AUTH-Y2 was scoped to Servo2.

    device_id: esp32-xiao-servo-02
    nonce:     71886edad817176a2dca4b8a8bf70fa3
    max_uses:  1

Authority ID:

    3ba6239d703d5ba203be2069f1c4c3fc89c27e63cff0b59be6977883ca654519

Final scored use:

    AUTH-Y2 -> Servo2

This is the Servo2 correctly targeted positive case.

## Y2_S2_ACCEPT_001

AUTH-Y2 was presented to its intended endpoint:

    esp32-xiao-servo-02

The endpoint recorded:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_TARGET_ID_MATCH
    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN
    008_PWM_COMMAND_END
    008_ACCEPT_EXECUTED

The presenter received:

    {"status":"accepted","reason":"executed"}

Presenter scoring:

    expected:     accepted
    scored_match: true

### Servo2 Persistent State

Pre-execution state:

    3CF11DBE7EA19F45E6194451AB2D5B1C94627FAAD6574A9BB566D7BEFC562E76

Post-execution artifact:

    evidence/state/SERVO2_Y2_AFTER_ACCEPT.bin

Post-execution SHA-256:

    A443EE0C0DEB23DE73A4F08F3A6BE20C5231DCFF131AE4A026C1A3D4DBF1C29B

The endpoint emitted:

    008_DURABLE_SPENT_REREAD_PASS

before:

    008_PWM_COMMAND_BEGIN

The correctly targeted authority was therefore durably consumed before execution.

### Servo2 Physical Witness

Witness GPIO:

    4

Before:

    pulse_seq: 0
    burst_seq: 0

After:

    pulse_seq: 49
    burst_seq: 1

Capture health:

    overflows:   0
    truncations: 0
    errors:      0

Witness-computed run-file SHA-256:

    1756bacf8d53c0336137f78876e91a0f42a3d204441850c6c7263bf47447930b

Observed physical result:

    one servo-like control-signal burst

### Y2_S2_ACCEPT_001 Disposition

    PASS

Servo2 accepted authority scoped to Servo2, durably consumed it before execution, and emitted one independently observed physical control-signal burst.

## AUTH-X3

AUTH-X3 was scoped to Servo1.

    device_id: esp32-xiao-servo-01
    nonce:     86062287c3d8be01446bf80ec69131bf
    max_uses:  1

Authority ID:

    5222af8445ee67ba8712f2469c91449a841c777cb40b9395d22c9bb1f30388ef

Final scored use:

    AUTH-X3 -> Servo1

X3 replaced the earlier X2 Servo1 positive run so the final positive physical observation could be made on the correct Servo1 witness line.

## X3_S1_ACCEPT_001

AUTH-X3 was presented to its intended endpoint:

    esp32-xiao-servo-01

The endpoint recorded:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_TARGET_ID_MATCH
    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN
    008_PWM_COMMAND_END
    008_ACCEPT_EXECUTED

The presenter received:

    {"status":"accepted","reason":"executed"}

Presenter scoring:

    expected:     accepted
    scored_match: true

### Servo1 Persistent State

Pre-execution artifact:

    evidence/state/SERVO1_X3_STATE_CHECK.bin

Pre-execution SHA-256:

    588C34697B132DF7B82E79BC6A06A2DD973938A446AEFF199726CA5F0F4BEF36

The authority was UNSPENT.

Post-execution artifact:

    evidence/state/SERVO1_X3_AFTER_ACCEPT.bin

Post-execution SHA-256:

    F2193B58041E1BFAFB2DB2A97463C4833AA2EAE196F84102DAB3A26DF6144873

The raw NVS image retained the earlier state=1 record and contained a later state=2 record for the same X3 authority ID.

The latest valid authority record was SPENT.

### Servo1 Physical Witness

Witness GPIO:

    5

Before:

    pulse_seq: 0
    burst_seq: 0

After:

    pulse_seq: 49
    burst_seq: 1

Capture health:

    overflows:   0
    truncations: 0
    errors:      0

Witness-computed run-file SHA-256:

    1b7247e7f4639556b66a3db3f14c4054229cd724dfb180107f1b7b645124021d

Observed physical result:

    one servo-like control-signal burst

### X3_S1_ACCEPT_001 Disposition

    PASS

Servo1 accepted authority scoped to Servo1, durably consumed it before execution, and emitted one independently observed physical control-signal burst.

## AUTH-Y3

AUTH-Y3 was scoped to Servo2.

    device_id: esp32-xiao-servo-02
    nonce:     045c3bbf278c91bfe2605cacb5bca37d
    max_uses:  1

Authority ID:

    2c7ded33c6d5cc142c6f4ba91c04add1803fc361d00f34b9d288b3bb67f711fa

Final scored use:

    AUTH-Y3 -> Servo1

This is the second wrong-target direction.

Y3 replaced the earlier Y2 Servo1 wrong-target run so the final zero-signal observation could be made on the correct Servo1 witness line.

## Y3_S1_DENY_001

AUTH-Y3 was a valid provider-signed authority for:

    esp32-xiao-servo-02

It was presented to:

    esp32-xiao-servo-01

The endpoint recorded:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_DENY_TARGET_ID_MISMATCH
    008_CLIENT_COMPLETE ... result=target_id_mismatch

The presenter received:

    {"status":"denied","reason":"target_id_mismatch"}

The endpoint did not record:

    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN
    008_PWM_COMMAND_END
    008_ACCEPT_EXECUTED

### Presenter Scoring Metadata Caveat

The run invocation used:

    --expect denied

rather than:

    --expect target_id_mismatch

The presenter evaluates a denial expectation by comparing the expected string to the endpoint's specific denial reason.

The endpoint correctly returned:

    status: denied
    reason: target_id_mismatch

but the JSON therefore contains:

    expected_verdict: denied
    scored_match:     false

The original evidence is retained unmodified.

This is a runner invocation metadata defect rather than a DUT target-binding failure.

The run is evaluated from the endpoint, state, and physical-witness evidence described below.

### Servo1 Persistent State

Before Y3:

    evidence/state/SERVO1_PRE_Y3_DENY.bin

After Y3:

    evidence/state/SERVO1_POST_Y3_DENY.bin

Both files have SHA-256:

    F2193B58041E1BFAFB2DB2A97463C4833AA2EAE196F84102DAB3A26DF6144873

The files are byte-identical.

The wrong-target Y3 request did not alter Servo1's persistent authority state.

### Servo1 Physical Witness

Witness GPIO:

    5

Before:

    pulse_seq: 0
    burst_seq: 0

After:

    pulse_seq: 0
    burst_seq: 0

Capture health:

    overflows:   0
    truncations: 0
    errors:      0

Witness-computed run-file SHA-256:

    8c1f95aa2acaec4c97cace8461892cab3c737e4651c134946a3ec9452694adeb

Observed physical result:

    zero target-line control bursts

### Y3_S1_DENY_001 Disposition

    PASS for the target-binding property
    presenter metadata caveat retained

The DUT rejected the correctly signed Servo2 authority at Servo1's explicit target gate.

Servo1 state remained byte-identical and no Servo1 control signal was observed.

## Directionality Closure

The final four cases close the directionality matrix in both directions:

    Servo1-scoped authority -> Servo2
        DENIED
        state unchanged
        zero physical signal

    Servo1-scoped authority -> Servo1
        ACCEPTED
        durably SPENT
        one physical burst

    Servo2-scoped authority -> Servo1
        DENIED
        state unchanged
        zero physical signal

    Servo2-scoped authority -> Servo2
        ACCEPTED
        durably SPENT
        one physical burst

The negative cases therefore cannot be explained by the target endpoint being generally unable to execute.

Each endpoint also accepted correctly scoped provider authority under the same test architecture.

## Target-Gate Ordering

The endpoint runtime evaluates:

    provider signature
        ->
    semantic admissibility
        ->
    signed target identity
        ->
    persistent authority state
        ->
    durable consume
        ->
    PWM command

The wrong-target endpoint logs stop at:

    008_DENY_TARGET_ID_MISMATCH

before successful authority-state markers appear.

The independent raw state captures show no target-state modification across the wrong-target cases.

The physical witness shows no corresponding electrical control burst.

The evidence therefore supports the tested ordering:

> Wrong-target authority was refused before persistent authority-state enforcement progressed and before physical execution.

## Correct-Target Durable Ordering

Both final positive cases recorded:

    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN

in that order.

The runtime therefore required a fresh durable SPENT reread before crossing the PWM command boundary.

ESP-LOCAL-008 uses this sequence as part of the positive control.

It does not independently re-characterize every persistence failure window previously tested in ESP-LOCAL-005.

## Independent Physical Correlation

The endpoint logs contain two final positive PWM executions:

    X3_S1_ACCEPT_001
    Y2_S2_ACCEPT_001

The independent witness recorded:

    X3_S1_ACCEPT_001
      GPIO5
      49 valid pulses
      1 burst

    Y2_S2_ACCEPT_001
      GPIO4
      49 valid pulses
      1 burst

The final wrong-target runs recorded:

    X2_S2_DENY_001
      GPIO4
      0 pulses
      0 bursts

    Y3_S1_DENY_001
      GPIO5
      0 pulses
      0 bursts

The physical evidence therefore correlates with the directionality decision in all four final cases.

## Witness Capture Health

Each final run reported:

    capture_overflows:   0
    capture_truncations: 0
    capture_errors:      0

The zero-signal wrong-target results therefore occurred while the witness reported a healthy capture path.

## Evidence Correlation

The PASS determination is not based on presenter responses alone.

The independent evidence streams agree as follows:

| Evidence Layer | Wrong Target | Correct Target |
|---|---|---|
| Provider artifact | valid authority scoped to other endpoint | valid authority scoped to target endpoint |
| Provider signature | valid | valid |
| Semantic admissibility | pass | pass |
| Target gate | mismatch / deny | match |
| Persistent-state path | no successful progression | UNSPENT then durable SPENT |
| Raw target state | unchanged | changed to SPENT |
| PWM endpoint log | none | one begin/end |
| Endpoint result | denied | accepted/executed |
| Witness | zero bursts | one burst |
| Witness health | no faults | no faults |

These observations support the conclusion that provider authority remained directionally bound to the endpoint named by the provider.

## Superseded Runs

### Y2_S1_DENY_001

Y2 was scoped to Servo2 and presented to Servo1.

Observed endpoint result:

    denied
    target_id_mismatch

Presenter scoring:

    true

The endpoint-side directionality result was correct.

The witness, however, was configured on GPIO4 while Servo1 was physically connected to witness GPIO5.

The run therefore did not satisfy the final Servo1 physical zero-signal criterion.

It was superseded by:

    Y3_S1_DENY_001

### X2_S1_ACCEPT_001

X2 was scoped to Servo1 and presented to Servo1.

Observed endpoint result:

    accepted
    executed

Presenter scoring:

    true

The endpoint recorded the expected target match, durable spend, PWM execution, and acceptance.

The witness was configured on GPIO4 rather than the Servo1 signal connected to witness GPIO5.

The run therefore did not satisfy the final independent Servo1 positive physical criterion.

It was superseded by:

    X3_S1_ACCEPT_001

The superseded runs are retained as valid endpoint-side provenance but are not used as the final physical-witness cases.

## Control Artifact

### Y3_S1_DENY_002

A follow-up Y3-to-Servo1 presentation used the correct expected-denial string:

    --expect target_id_mismatch

The presenter recorded:

    status:       denied
    reason:       target_id_mismatch
    scored_match: true

The witness START reply reported:

    run_already_active

The endpoint serial capture was not successfully obtained; the retained endpoint log is an empty one-byte placeholder.

This run is therefore retained only as a runner/control artifact.

It is not part of the final scored matrix.

## What ESP-LOCAL-008 Establishes

For the tested two-endpoint ESP32-S3 configuration:

> A valid provider-issued authority remained bound to the endpoint named in its signed target identity. Presentation to the other endpoint was rejected at the target gate without changing the target endpoint's persistent authority state and without producing an observed target-line control signal. Correctly targeted authority was accepted, durably consumed, and independently observed at the physical control-signal boundary.

The property held in both tested endpoint directions.

## What ESP-LOCAL-008 Does Not Establish

ESP-LOCAL-008 does not independently establish:

- resistance to trusted provider private-key theft;
- security after complete endpoint firmware compromise;
- resistance to persistent-state rollback;
- resistance to physical storage tampering;
- denial-of-service resistance;
- trusted-time semantics;
- arbitrary multi-endpoint routing correctness;
- arbitrary numbers of endpoints;
- arbitrary hardware implementations;
- mechanical servo movement independent of the electrical signal;
- reboot or full power-loss persistence beyond the separate persistence tests;
- crash-window behavior beyond the separate persistence tests;
- hostile-relay mutation resistance beyond ESP-LOCAL-006;
- wrong-provider-key rejection beyond ESP-LOCAL-006; or
- concurrent requester behavior beyond ESP-LOCAL-007.

## Final Disposition

    ESP-LOCAL-008
    Property: signed endpoint directionality / target binding
    Final matrix: 4 cases

    wrong-target denials:           2 / 2
    wrong-target state unchanged:  2 / 2
    wrong-target physical bursts:  0 / 2

    correct-target acceptances:     2 / 2
    correct-target durable spends:  2 / 2
    correct-target physical bursts: 2 / 2

    witness capture faults:         0

    Result: PASS

The final matrix demonstrates that valid provider authority for one tested endpoint did not become executable authority at the other tested endpoint, while valid correctly targeted authority remained executable under its provider-established bounds.
