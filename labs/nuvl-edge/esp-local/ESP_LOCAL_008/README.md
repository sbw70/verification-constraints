# ESP-LOCAL-008 — Signed Endpoint Directionality

**Status:** PASS  
**Date:** 2026-09-29 local / 2026-09-30 UTC  
**Classification:** NUVL core  
**Property:** signed endpoint target binding

ESP-LOCAL-008 tests whether valid provider-issued authority remains bound to the endpoint named in its signed `device_id`.

Two ESP32-S3 servo endpoints were used.

Valid authority issued for Servo1 was presented to Servo2, and valid authority issued for Servo2 was presented to Servo1.

In both directions, the unintended endpoint rejected the request at the explicit target-identity gate before its persistent authority state changed and before a physical control signal was observed.

Correctly targeted authorities were then accepted, durably consumed, and independently observed at the physical control-signal boundary.

## Claim Under Test

The test question is:

> Can valid provider-issued authority for endpoint X become executable authority at endpoint Y?

ESP-LOCAL-008 retains the existing provider-controlled bounded-authority model.

The provider originates and signs authority.

The endpoint verifies and enforces it.

The endpoint may transport, recognize, and enforce provider-issued authority, but cannot originate or enlarge it.

The new variable in ESP-LOCAL-008 is explicit signed endpoint directionality.

## Result

Final four-case matrix:

| Run | Authority Scope | Presented To | Result | Physical Witness |
|---|---|---|---|---|
| `X2_S2_DENY_001` | Servo1 | Servo2 | `target_id_mismatch` | 0 pulses / 0 bursts |
| `Y3_S1_DENY_001` | Servo2 | Servo1 | `target_id_mismatch` | 0 pulses / 0 bursts |
| `X3_S1_ACCEPT_001` | Servo1 | Servo1 | accepted / executed | 49 pulses / 1 burst |
| `Y2_S2_ACCEPT_001` | Servo2 | Servo2 | accepted / executed | 49 pulses / 1 burst |

For both wrong-target cases:

    provider signature:        valid
    semantic admissibility:   pass
    target gate:              mismatch / deny
    target persistent state:  unchanged
    PWM execution:            none
    physical signal:          none

For both correct-target cases:

    provider signature:        valid
    semantic admissibility:   pass
    target gate:              match
    authority state:          UNSPENT
    durable consume:          SPENT before PWM
    endpoint execution:       one
    physical signal:          one burst

The signed target-binding property held in both tested directions.

## Test Architecture

    provider
       |
       | signed, endpoint-scoped authority
       v
    presenter
       |
       | exact frozen request bytes
       v
    ESP32-S3 endpoint
       |
       | signature verification
       | semantic admissibility
       | signed target gate
       |
       +---- wrong target ----> DENY
       |                       no state progression
       |                       no PWM
       |
       v
    persistent authority state
       |
       | durable consume
       v
    PWM command
       |
       v
    independent ESP32-S3 RMT witness

The independent witness has no provider-authority or authorization role.

It observes the electrical servo-control signal only.

## Endpoints

Servo #1:

    device_id: esp32-xiao-servo-01
    IP:        192.168.0.81
    MAC:       1c:db:d4:45:11:e8

Servo #2:

    device_id: esp32-xiao-servo-02
    IP:        192.168.0.186
    MAC:       1c:db:d4:45:10:a4

Both endpoint builds used GPIO5 for the actuator PWM output.

Pre-scored validation identified an incorrect Servo #2 actuator GPIO mapping; the configuration was corrected before scored execution.

## Signed Target Gate

ESP-LOCAL-008 separates target identity from the general semantic check.

The relevant enforcement order is:

    provider signature
        |
        v
    semantic admissibility
        |
        v
    signed device_id == local endpoint identity
        |
        +---- no ----> target_id_mismatch
        |
       yes
        |
        v
    persistent authority-state validation
        |
        v
    durable consume
        |
        v
    PWM execution

Wrong-target endpoint logs stop at:

    008_SIGNATURE_VALID
    008_SEMANTIC_ADMISSIBILITY_PASS
    008_DENY_TARGET_ID_MISMATCH

Correct-target logs continue through:

    008_TARGET_ID_MATCH
    008_AUTHORITY_UNSPENT_PASS
    008_DURABLE_SPENT_REREAD_PASS
    008_PWM_COMMAND_BEGIN
    008_PWM_COMMAND_END
    008_ACCEPT_EXECUTED

## Independent Physical Witness

The witness is:

    device_id:      esp32-witness-007
    IP:             192.168.0.216
    control port:   19072/UDP
    capture engine: RMT RX

Final physical mapping:

    witness GPIO4 -> Servo #2 signal
    witness GPIO5 -> Servo #1 signal

The two wrong-target runs produced:

    0 pulses
    0 bursts

The two correct-target runs produced:

    49 pulses
    1 servo-like burst

All four final captures reported zero capture overflow, truncation, and error counts.

The witness establishes the electrical control-signal observation.

It does not independently establish mechanical servo-shaft displacement.

## Repository Layout

    ESP_LOCAL_008/
    |-- README.md
    |-- RESULTS.md
    |-- PROVENANCE.md
    |
    |-- provider/
    |-- coordinator/
    |-- firmware/
    |-- witness/
    `-- evidence/

### `provider/`

Contains the ESP-LOCAL-008 provider generator and the frozen X2, Y2, X3, and Y3 authority artifacts.

The provider creates the canonical authority, computes its SHA-256 authority ID, and signs the authority with the established provider Ed25519 key.

See:

    provider/README.md

### `coordinator/`

Contains the presenter used to send one frozen authority to one selected endpoint and record the endpoint and witness result.

The presenter transports authority. It does not originate or enlarge it.

See:

    coordinator/README.md

### `firmware/`

Contains the full ESP-IDF endpoint runtime and explicit authority-state provisioner.

The endpoint runtime implements the target gate before persistent-state access.

See:

    firmware/README.md

### `witness/`

Contains the ESP-IDF RMT RX hardware witness used to observe the physical control-signal boundary.

See:

    witness/README.md

### `evidence/`

Contains:

    final scored presenter JSON
    final endpoint serial logs
    raw endpoint state partitions
    raw witness evidence partitions
    superseded runs
    control artifacts

See:

    evidence/README.md

## Evidence Model

ESP-LOCAL-008 does not treat a single software response as proof of the result.

The evidence chain crosses separate observation domains:

| Domain | Evidence |
|---|---|
| Provider | exact signed target-scoped authority |
| Presenter | exact request, target, response, witness bracket |
| Endpoint | signature, target gate, state, and execution markers |
| Persistent state | raw `nuvl_state` partition images |
| Physical witness | independent RMT control-signal observation |

For wrong-target cases, these layers agree on:

    valid authority
        ->
    unintended endpoint
        ->
    target_id_mismatch
        ->
    target state unchanged
        ->
    no physical signal

For correct-target cases:

    valid authority
        ->
    intended endpoint
        ->
    target match
        ->
    durable consume
        ->
    one PWM execution
        ->
    one physical signal burst

## Retained Caveat

`Y3_S1_DENY_001` contains a presenter-side scoring metadata defect.

The run was invoked with:

    --expect denied

instead of:

    --expect target_id_mismatch

The endpoint correctly returned:

    denied / target_id_mismatch

but the presenter therefore recorded:

    scored_match: false

The original JSON is retained unchanged.

The endpoint log, unchanged pre/post state, and correct GPIO5 witness capture all support the target-binding result.

The defect is documented rather than rewritten.

## Superseded Runs

Two earlier Servo1 runs were retained under:

    evidence/superseded/

Their endpoint-side behavior was valid, but the witness was monitoring GPIO4 while the Servo1 physical signal was connected to GPIO5.

They were replaced by the final GPIO5-observed Servo1 cases.

They are retained for provenance and are not used as the final physical-witness evidence.

## Supported Result

ESP-LOCAL-008 establishes, for the tested two-endpoint configuration:

> Provider-signed authority remained bound to its designated endpoint. Cross-target presentation was rejected before persistent authority-state access and before physical execution, while correctly targeted authority was accepted once, durably consumed, and independently observed at the physical control-signal boundary.

The result is intentionally narrow.

ESP-LOCAL-008 does not independently re-run the persistence, hostile-relay, wrong-provider-key, crash-window, or concurrent-requester properties tested elsewhere in the ESP-LOCAL series.

## Supporting Documents

`RESULTS.md` contains the scored observations and final dispositions.

`PROVENANCE.md` records artifact lineage, tested identities, source/binary relationships, known publication derivatives, and retained evidence caveats.

Folder-specific READMEs document the provider, presenter, endpoint firmware, independent witness, and evidence package.
