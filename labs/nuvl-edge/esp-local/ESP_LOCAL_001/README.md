# ESP-LOCAL-001

## Endpoint-Local Bounded-Authority Recognition

ESP-LOCAL-001 evaluates whether bounded-authority admissibility recognition can execute directly on a resource-constrained physical endpoint rather than depending on a separate recognition boundary.

The test moves the recognition decision onto a Seeed XIAO ESP32-S3 controlling a physical servo output.

An independent ESP32-S3 witness observes the servo PWM signal to distinguish logical acceptance from physical command issuance.

## Objective

Demonstrate that a resource-constrained endpoint can:

- evaluate a bounded admissibility predicate locally;
- reject requests outside the defined device, context, and action bounds;
- reject representations containing unexpected fields;
- gate physical command issuance on the accepted result; and
- perform these functions without relying on a separate recognition boundary.

## Test Architecture

```text
Request source
     |
     v
XIAO ESP32-S3
     |
     | endpoint-local
     | admissibility recognition
     v
Accepted / Denied
     |
     | accepted only
     v
Servo PWM command
     |
     v
Independent ESP32-S3 witness
```

The endpoint under test is:

```text
device_id = esp32-xiao-servo-01
context   = esp_local_demo
action    = move_servo
```

The endpoint accepts only the exact request representation containing:

```text
device_id
context
action
```

Physical command issuance occurs only after successful endpoint-local recognition.

## Test Matrix

The final implementation was exercised against:

| Case | Expected result |
|---|---|
| Correct device/context/action | ACCEPT |
| Unauthorized action | DENY |
| Wrong device | DENY |
| Wrong context | DENY |
| Missing device | DENY |
| Missing context | DENY |
| Missing action | DENY |
| Unexpected field | DENY |

All final cases produced the expected decision.

## Independent Execution Witness

The servo PWM output was monitored by a separate ESP32-S3 DevKit.

An accepted request produced one independently observed PWM burst:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=74859
ESP_LOCAL_001_WITNESS_HEARTBEAT ticks_ms=75082 state=ACTIVE
ESP_LOCAL_001_WITNESS_BURST_END pulses=50 duration_ms=978 pulse_min_us=857 pulse_max_us=2006
```

A denied wrong-device request produced no additional observed PWM burst.

This distinguishes logical endpoint acceptance from independently observed electrical command issuance.

## Fail-Open Defect Identified During Testing

The initial implementation validated required fields but did not reject additional fields.

A request containing an unexpected field was therefore accepted.

The implementation was corrected to require the exact request key set. After correction:

- the unexpected-field request was denied with `unexpected_field`; and
- the valid request remained accepted.

The final published endpoint firmware contains the corrected behavior.

## Result

**PASS**

ESP-LOCAL-001 demonstrates that bounded-authority admissibility recognition can be placed directly on a resource-constrained physical endpoint and used to gate local physical command issuance.

The result establishes that the recognition function is not inherently dependent on a Raspberry Pi, gateway, or other separate intermediary.

## Claim Boundary

ESP-LOCAL-001 evaluates endpoint-local placement and admissibility recognition.

The incoming object was not authenticated as externally issued provider authority. The endpoint used a locally configured static admissibility predicate.

Accordingly, ESP-LOCAL-001 does not establish:

- cryptographic provider attribution;
- externally established authority bounds;
- replay or freshness protection;
- persistent spent-state;
- secure boot;
- endpoint-compromise resistance;
- protected trust-anchor or key storage;
- hardware tamper resistance;
- production key custody; or
- exactly-once mechanical execution.

The independent witness establishes electrical PWM command issuance, not mechanical servo movement.

## Repository Contents

```text
ESP_LOCAL_001/
├── README.md
├── RESULTS.md
├── PROVENANCE.md
├── SHA256SUMS.txt
├── firmware/
│   └── esp_local_001_main.py
├── witness/
│   └── esp_local_001_witness.py
└── evidence/
    └── ESP_LOCAL_001_EVIDENCE.log
```

`RESULTS.md` records the test outcomes and supported claim.

`PROVENANCE.md` records artifact identity, hashes, and the relationship between the tested implementation and published evidence.

`SHA256SUMS.txt` covers the published test artifacts.
