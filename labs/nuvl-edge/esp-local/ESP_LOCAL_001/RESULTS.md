# ESP-LOCAL-001 Results

## Result

**PASS**

ESP-LOCAL-001 demonstrated that bounded-authority admissibility recognition can execute directly on a resource-constrained physical endpoint and gate local physical command issuance without relying on a separate recognition boundary.

## Test Configuration

| Component | Configuration |
|---|---|
| Endpoint | Seeed XIAO ESP32-S3 |
| Device ID | `esp32-xiao-servo-01` |
| Recognition location | Endpoint-local |
| Context | `esp_local_demo` |
| Authorized action | `move_servo` |
| Servo output | GPIO5 |
| Independent witness | ESP32-S3 DevKit |
| Witness function | Electrical observation of servo PWM |

The endpoint accepted only the exact authority tuple:

```text
device_id = esp32-xiao-servo-01
context   = esp_local_demo
action    = move_servo
```

Physical command issuance occurred only after the request passed the endpoint-local admissibility checks.

## Semantic Matrix

| Test case | Decision | Reason |
|---|---|---|
| Valid device/context/action | ACCEPT | `authority_admissible` |
| Unauthorized action | DENY | `action_not_authorized` |
| Wrong device | DENY | `wrong_device` |
| Wrong context | DENY | `wrong_context` |
| Missing context | DENY | `wrong_context` |
| Missing device | DENY | `wrong_device` |
| Missing action | DENY | `action_not_authorized` |
| Unexpected field | DENY | `unexpected_field` |

All final semantic cases produced the expected result.

## Representation-Ambiguity Defect

Initial testing identified a fail-open representation defect.

The first endpoint implementation validated the required fields but did not reject additional fields. A request containing:

```json
{
  "device_id": "esp32-xiao-servo-01",
  "context": "esp_local_demo",
  "action": "move_servo",
  "extra": "ignored"
}
```

was accepted.

This behavior was inconsistent with exact bounded-authority recognition because the endpoint was accepting a representation larger than the defined admissible object.

The implementation was changed to require the exact key set:

```text
device_id
context
action
```

Requests containing additional fields were subsequently denied with:

```text
unexpected_field
```

A valid request remained accepted after the correction.

## Independent Physical-Command Witness

The independent witness observed the endpoint servo PWM signal.

For an accepted request, the witness recorded:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=74859
ESP_LOCAL_001_WITNESS_HEARTBEAT ticks_ms=75082 state=ACTIVE
ESP_LOCAL_001_WITNESS_BURST_END pulses=50 duration_ms=978 pulse_min_us=857 pulse_max_us=2006
```

The observed burst is consistent with the configured approximately one-second servo PWM command.

A subsequent wrong-device request was denied.

No additional PWM burst was observed during the denial interval, and the witness remained `IDLE` through at least:

```text
ticks_ms=195088
```

The witness therefore independently distinguished physical command issuance following an accepted request from the absence of command issuance following a denied request.

## Supported Claim

ESP-LOCAL-001 supports the following claim:

> A resource-constrained physical endpoint can perform local bounded-authority admissibility recognition and gate its own physical command issuance without relying on a separate recognition boundary.

The result establishes that NUVL-style recognition is not inherently dependent on placement at a Raspberry Pi, gateway, or other separate intermediary.

## Limitations

ESP-LOCAL-001 did not authenticate the incoming object as externally issued provider authority.

The endpoint used a locally configured static admissibility predicate. The test therefore does not establish:

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

The independent witness establishes electrical PWM command issuance. It does not independently establish mechanical servo movement.

## Artifact Integrity

Test artifacts and curated evidence are covered by the accompanying `SHA256SUMS.txt`.

