# ESP-LOCAL-003 Results

## Status

**PASS**

ESP-LOCAL-003 demonstrated endpoint-local recognition of an externally established bounded authority object whose device, context, action, nonce, and use constraint were jointly represented in verification material.

The endpoint rejected modification or enlargement of those bounds before physical command issuance, consumed valid authority before execution, and denied subsequent reuse during the current runtime.

## Test Configuration

| Property | Value |
|---|---|
| Endpoint | Seeed XIAO ESP32-S3 |
| Device ID | `esp32-xiao-servo-01` |
| Context | `esp_local_003` |
| Authorized action | `move_servo` |
| Maximum uses | `1` |
| Physical output | Servo PWM |
| Independent witness | ESP32-S3 DevKit |

Frozen nonce:

```text
eee8483225c14eb493654571128d57e2
```

Frozen SHA-256 authority commitment:

```text
2452e70c9003739fd571a5e38752e54d526c1f7ee876ad3bed3041e09ca9c0cc
```

Authority object:

```json
{
  "device_id": "esp32-xiao-servo-01",
  "context": "esp_local_003",
  "action": "move_servo",
  "nonce": "eee8483225c14eb493654571128d57e2",
  "max_uses": 1
}
```

Canonical representation:

```text
{"action":"move_servo","context":"esp_local_003","device_id":"esp32-xiao-servo-01","max_uses":1,"nonce":"eee8483225c14eb493654571128d57e2"}
```

## Test Matrix

| Test case | Result | Decision reason | Witness |
|---|---|---|---|
| Original authority | **ACCEPT** | `authority_admissible` | PWM burst observed |
| Exact replay | **DENY** | `authority_spent` | No second burst observed |
| `max_uses: 1` → `2` | **DENY** | `use_constraint_invalid` | No burst observed |
| Nonce mutation | **DENY** | `authority_commitment_mismatch` | No burst observed |
| Device mutation | **DENY** | `wrong_device` | No burst observed |
| Context mutation | **DENY** | `wrong_context` | No burst observed |
| Action mutation | **DENY** | `action_not_authorized` | No burst observed |
| Extra field | **DENY** | `unexpected_or_missing_field` | No burst observed |
| Missing required field | **DENY** | `unexpected_or_missing_field` | No burst observed |
| Original authority after non-consuming mutations | **ACCEPT** | `authority_admissible` | PWM burst observed |

## Initial Valid Authority

The frozen authority object was accepted:

```text
decision  reason                device_id
--------  ------                ---------
accepted  authority_admissible  esp32-xiao-servo-01
```

The independent witness recorded one PWM command burst:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=244932
ESP_LOCAL_001_WITNESS_HEARTBEAT ticks_ms=245092 state=ACTIVE
ESP_LOCAL_001_WITNESS_BURST_END pulses=50 duration_ms=978 pulse_min_us=426 pulse_max_us=2003
```

The `ESP_LOCAL_001` identifier reflects reuse of the established witness implementation. The witness did not participate in the authority decision.

## Replay Rejection

The exact authority object was submitted again without resetting the endpoint.

Result:

```json
{"reason": "authority_spent", "decision": "denied"}
```

No second PWM burst was observed during the retained replay interval.

This established current-runtime single-use enforcement for the recognized authority.

## Use-Constraint Enlargement

After returning the endpoint to an unspent state, `max_uses` was changed from `1` to `2`.

Result:

```json
{"reason": "use_constraint_invalid", "decision": "denied"}
```

No PWM burst was observed.

The attempted enlargement of the externally established use constraint therefore did not reach physical command issuance.

## Nonce Mutation

The frozen nonce:

```text
eee8483225c14eb493654571128d57e2
```

was changed to:

```text
eee8483225c14eb493654571128d57e3
```

Result:

```json
{"reason": "authority_commitment_mismatch", "decision": "denied"}
```

No PWM burst was observed.

This case exercised the integrity-bound authority representation directly: the modified object no longer matched the frozen SHA-256 commitment.

## Device Mutation

The device identity was changed from:

```text
esp32-xiao-servo-01
```

to:

```text
esp32-xiao-servo-02
```

Result:

```json
{"reason": "wrong_device", "decision": "denied"}
```

No PWM burst was observed during the retained denial sequence.

## Context Mutation

The context was changed from:

```text
esp_local_003
```

to:

```text
esp_local_004
```

Result:

```json
{"reason": "wrong_context", "decision": "denied"}
```

No PWM burst was observed.

## Action Mutation

The authorized action was changed from:

```text
move_servo
```

to:

```text
open_valve
```

Result:

```json
{"reason": "action_not_authorized", "decision": "denied"}
```

No PWM burst was observed during the retained denial sequence.

## Representation Enforcement

An authority object containing an additional field was denied:

```json
{"reason": "unexpected_or_missing_field", "decision": "denied"}
```

An authority object missing the required `nonce` field was also denied:

```json
{"reason": "unexpected_or_missing_field", "decision": "denied"}
```

The endpoint therefore rejected authority representations outside the tested schema rather than ignoring additional or absent fields.

## Non-Consumption of Denied Mutations

The original authority object remained usable after the mutation-denial sequence.

Without an intervening endpoint reset, the original authority was submitted again.

Result:

```text
decision  reason                device_id
--------  ------                ---------
accepted  authority_admissible  esp32-xiao-servo-01
```

The independent witness recorded:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=1047996
ESP_LOCAL_001_WITNESS_BURST_END pulses=51 duration_ms=999 pulse_min_us=426 pulse_max_us=2123
```

The endpoint returned to `IDLE` afterward.

This control established that rejected mutation attempts did not consume or corrupt the legitimate authority state.

## Physical Witness Result

Two accepted execution events were independently observed.

Initial valid authority:

```text
BURST_START ticks_ms=244932
BURST_END pulses=50 duration_ms=978 pulse_min_us=426 pulse_max_us=2003
```

Final valid control:

```text
BURST_START ticks_ms=1047996
BURST_END pulses=51 duration_ms=999 pulse_min_us=426 pulse_max_us=2123
```

The retained witness record remained `IDLE` through the replay and mutation-denial observations between those accepted events.

The witness establishes electrical PWM command issuance. It does not establish guaranteed mechanical movement or exactly-once mechanical execution.

## Fail-Closed Implementation Observations

MicroPython compatibility defects were encountered during implementation.

An initial canonicalization path used an unsupported `json.dumps(..., separators=...)` form. Authority processing failed and returned a denial rather than issuing a physical command.

A subsequent implementation required adjustment because the MicroPython hashing API did not provide the initially assumed `hexdigest()` behavior.

Both implementation failures remained on the denied path. No unintended PWM command issuance was observed.

The final tested implementation used MicroPython-compatible canonicalization and SHA-256 processing.

## Result

**ESP-LOCAL-003: PASS**

The test demonstrated that a resource-constrained physical endpoint could:

- recognize an externally established bounded authority object locally;
- jointly represent device, context, action, nonce, and use constraint in verification material;
- reject modification of the tested bounds;
- reject attempted enlargement of the use constraint;
- reject unexpected or incomplete authority representations;
- consume valid authority before physical command issuance;
- deny reuse during the current runtime; and
- preserve legitimate authority across non-consuming denial attempts.

## Supported Claim

> A resource-constrained physical endpoint can locally recognize an externally established bounded authority object whose device, context, action, nonce, and use constraint are jointly represented in verification material, reject modification or enlargement of those bounds before physical command issuance, consume valid authority before execution, and deny subsequent reuse within the current runtime.

## Evidence Boundary

ESP-LOCAL-003 establishes commitment-based integrity recognition. It does not establish asymmetric provider attribution.

The test does not establish:

- persistent spent-state across endpoint reboot;
- trusted time or expiration enforcement;
- secure boot;
- protected trust material;
- endpoint-compromise resistance;
- production cryptographic hardening;
- guaranteed mechanical movement; or
- exactly-once physical execution.

Provider-attributable asymmetric authority is evaluated separately in ESP-LOCAL-004.
