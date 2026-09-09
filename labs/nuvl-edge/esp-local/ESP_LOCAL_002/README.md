# ESP-LOCAL-002

## External Capability with Endpoint-Local Recognition

ESP-LOCAL-002 evaluates whether a resource-constrained physical endpoint can locally recognize and consume an externally generated one-time capability while retaining physical command gating at the endpoint.

The test extends ESP-LOCAL-001 by introducing an authority-enabling bearer value generated outside the endpoint.

The external source generates the capability. The endpoint stores only its SHA-256 commitment and independently evaluates the presented capability together with locally configured device, context, and action constraints.

An independent ESP32-S3 witness observes the servo PWM signal to distinguish logical acceptance from physical command issuance.

## Objective

Demonstrate that a resource-constrained endpoint can:

- recognize possession of an externally generated bearer capability;
- retain only verification material rather than the capability value;
- independently constrain admissibility by device, context, and action;
- reject an invalid capability;
- consume a valid capability before physical command issuance;
- reject reuse of the consumed capability during the same runtime; and
- gate physical command issuance on the accepted result without relying on a separate recognition boundary.

## Test Architecture

```text
External capability source
        |
        | bearer capability
        v
XIAO ESP32-S3
        |
        | endpoint-local recognition
        | device/context/action checks
        | SHA-256 capability verification
        | single-use consumption
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
context   = esp_local_002
action    = move_servo
```

The endpoint requires the exact request representation:

```text
device_id
context
action
capability
```

## Capability Model

The external capability utility generates a random 256-bit bearer value.

For the tested instance:

```text
capability =
8b20574c6ba2330e4a4b94e91e1a1669c585b7d86c95e5592bd018ff42337e3e
```

The endpoint stores only the corresponding SHA-256 commitment:

```text
700775b2bd9fd36b8f0c5f6e5072297a6e6df30bbfb24b49fbf9e88960ad18ae
```

For a request to be admissible, the endpoint requires:

```text
device_id = esp32-xiao-servo-01
context   = esp_local_002
action    = move_servo
SHA-256(capability) = stored commitment
capability_spent = false
```

The capability is marked spent before physical command issuance.

Spent state in ESP-LOCAL-002 is maintained in RAM.

## Test Matrix

| Case | Expected result |
|---|---|
| Valid capability, first presentation | ACCEPT |
| Exact capability replay | DENY |
| Invalid capability | DENY |
| Same capability, wrong device | DENY |
| Same capability, wrong context | DENY |
| Same capability, unauthorized action | DENY |

All tested cases produced the expected decision.

## Independent Execution Witness

Following an endpoint reset establishing an unspent runtime state, the valid capability was presented with the correct device, context, and action.

The endpoint returned:

```text
accepted
authority_admissible
```

The independent witness observed one PWM command burst:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=236837
ESP_LOCAL_001_WITNESS_BURST_END pulses=50 duration_ms=980 pulse_min_us=1792 pulse_max_us=2001
```

The exact same capability was then presented again without resetting the endpoint.

The endpoint denied the replay:

```text
decision=denied
reason=capability_spent
```

No additional PWM burst was observed.

The witness remained `IDLE` through at least:

```text
ESP_LOCAL_001_WITNESS_HEARTBEAT ticks_ms=355095 state=IDLE
```

The observed execution sequence was:

```text
Externally generated capability
             |
             v
     First valid presentation
             |
             v
           ACCEPT
             |
             v
     Capability consumed
             |
             v
 One witnessed PWM command
             |
             v
        Exact replay
             |
             v
            DENY
             |
             v
 No additional PWM command
```

## Result

**PASS**

ESP-LOCAL-002 demonstrates that a resource-constrained physical endpoint can locally recognize possession of an externally generated one-time capability, constrain its admissibility to a specific local device/context/action predicate, consume the capability before physical command issuance, and deny reuse without relying on a separate recognition boundary.

The result extends ESP-LOCAL-001 by separating the authority-enabling bearer value from the endpoint that performs recognition and physical command gating.

## Claim Boundary

ESP-LOCAL-002 uses a bearer capability.

Possession of the capability permits presentation. The test does not establish cryptographic identity of the request sender or cryptographic provider attribution.

The endpoint independently enforces the configured `device_id`, `context`, and `action` predicates. Those predicates are not cryptographically bound into the externally generated capability commitment.

Accordingly, ESP-LOCAL-002 does not establish that the external source cryptographically established the complete bounded authority object.

Spent state is maintained only in endpoint RAM. Endpoint reset clears the spent state. Persistent replay resistance across restart or power loss is therefore not established by this test.

ESP-LOCAL-002 does not establish:

- cryptographic provider attribution;
- cryptographic binding of the complete authority object;
- persistent replay resistance across endpoint restart or power loss;
- secure boot;
- endpoint-compromise resistance;
- protected trust-anchor or key storage;
- hardware tamper resistance;
- production key custody; or
- exactly-once mechanical execution.

The independent witness establishes electrical PWM command issuance, not mechanical servo movement.

## Repository Contents

```text
ESP_LOCAL_002/
├── README.md
├── RESULTS.md
├── PROVENANCE.md
├── SHA256SUMS.txt
├── firmware/
│   └── esp_local_002_main.py
├── provider/
│   └── esp_local_002_provider.py
├── witness/
│   └── esp_local_002_witness.py
└── evidence/
    └── ESP_LOCAL_002_EVIDENCE.log
```

`RESULTS.md` records the observed test results and supported claim.

`PROVENANCE.md` records artifact identity, hashes, and the relationship between the external capability utility, endpoint implementation, witness, and evidence.

`SHA256SUMS.txt` covers the published test artifacts.
