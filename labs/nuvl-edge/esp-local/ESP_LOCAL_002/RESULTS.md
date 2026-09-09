# ESP-LOCAL-002 Results

## Result

**PASS**

ESP-LOCAL-002 demonstrated endpoint-local recognition and single-use consumption of an externally generated bearer capability, with independent observation of physical command issuance.

A valid capability was accepted once and produced one independently witnessed servo PWM command burst. Exact replay of the consumed capability was denied and produced no additional witnessed command burst.

## Test Configuration

| Component | Configuration |
|---|---|
| Endpoint | Seeed XIAO ESP32-S3 |
| Device ID | `esp32-xiao-servo-01` |
| Recognition location | Endpoint-local |
| Context | `esp_local_002` |
| Authorized action | `move_servo` |
| Capability generation | External provider/source utility |
| Capability type | Random 256-bit bearer value |
| Endpoint verification material | SHA-256 commitment |
| Spent-state location | Endpoint RAM |
| Servo output | GPIO5 |
| Independent witness | ESP32-S3 DevKit |
| Witness function | Electrical observation of servo PWM |

The external utility generated the capability:

```text
8b20574c6ba2330e4a4b94e91e1a1669c585b7d86c95e5592bd018ff42337e3e
```

The endpoint stored only the corresponding SHA-256 commitment:

```text
700775b2bd9fd36b8f0c5f6e5072297a6e6df30bbfb24b49fbf9e88960ad18ae
```

The endpoint required the exact request fields:

```text
device_id
context
action
capability
```

For an admissible request, the endpoint required:

```text
device_id = esp32-xiao-servo-01
context   = esp_local_002
action    = move_servo
SHA-256(capability) = stored commitment
capability_spent = false
```

The capability was marked spent before physical command issuance.

## Semantic Matrix

| Test case | Decision | Reason |
|---|---|---|
| Valid capability, first presentation | ACCEPT | `authority_admissible` |
| Exact capability replay | DENY | `capability_spent` |
| Invalid capability | DENY | `capability_invalid` |
| Same capability, wrong device | DENY | `wrong_device` |
| Same capability, wrong context | DENY | `wrong_context` |
| Same capability, unauthorized action | DENY | `action_not_authorized` |

All tested cases produced the expected decision.

## First Capability Spend

Following an endpoint reset establishing a fresh runtime state, the valid externally generated capability was presented with the correct device, context, and action.

The endpoint returned:

```text
decision  reason                 device_id
accepted  authority_admissible   esp32-xiao-servo-01
```

The independent witness recorded one PWM command burst:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=236837
ESP_LOCAL_001_WITNESS_BURST_END pulses=50 duration_ms=980 pulse_min_us=1792 pulse_max_us=2001
```

The witness returned to `IDLE` following the burst.

## Replay

The exact same request and capability were subsequently presented without resetting the endpoint.

The endpoint returned:

```json
{"reason": "capability_spent", "decision": "denied"}
```

No additional PWM command burst was observed.

The independent witness continued reporting `IDLE` through at least:

```text
ESP_LOCAL_001_WITNESS_HEARTBEAT ticks_ms=355095 state=IDLE
```

The observed sequence was therefore:

```text
Valid first presentation
        |
        v
      ACCEPT
        |
        v
One witnessed PWM command
        |
        v
Capability consumed
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

## Supported Claim

ESP-LOCAL-002 supports the following claim:

> A resource-constrained physical endpoint can locally recognize possession of an externally generated one-time capability, independently constrain its admissibility to a specific local device/context/action predicate, consume that capability before physical command issuance, and deny reuse without relying on a separate recognition boundary.

The test extends endpoint-local recognition beyond the static admissibility predicate demonstrated in ESP-LOCAL-001 by introducing an authority-enabling bearer value generated outside the endpoint.

The endpoint retained the capability commitment rather than the capability value itself.

## Claim Boundary

ESP-LOCAL-002 does not establish cryptographic identity of the request sender.

The capability is a bearer value. Possession of the capability permits its presentation.

The `device_id`, `context`, and `action` constraints are endpoint-local predicates. They are not cryptographically bound into the externally generated capability commitment. The result therefore does not establish that the external source cryptographically established those tuple bounds.

Spent state is RAM-only. Endpoint reset clears the spent state. Persistent replay resistance across endpoint restart or power loss is not established by ESP-LOCAL-002.

The test does not establish:

- cryptographic provider identity or signature attribution;
- cryptographic binding of the full authority object;
- persistent spent-state;
- secure boot;
- endpoint-compromise resistance;
- protected trust-anchor or key storage;
- hardware tamper resistance;
- production key custody; or
- exactly-once mechanical execution.

The independent witness establishes electrical PWM command issuance, not mechanical servo movement.

## Artifact Integrity

Test artifacts and curated evidence are covered by the accompanying `SHA256SUMS.txt`.

The manifest verified all four covered artifacts successfully.
