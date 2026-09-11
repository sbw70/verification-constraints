# ESP-LOCAL-003

## Endpoint-Local Integrity-Bound Authority Recognition

ESP-LOCAL-003 demonstrates that a resource-constrained physical endpoint can locally recognize an externally established bounded authority object, reject modification or enlargement of its bounds, consume valid authority before physical command issuance, and deny reuse during the current runtime.

The test moves beyond the bearer-capability model demonstrated in ESP-LOCAL-002 by jointly representing the complete authority object in SHA-256 verification material.

**Status: PASS**

## Architecture

```text
External authority source
        |
        v
Seeed XIAO ESP32-S3
  local recognition
  bound verification
  spent-state check
        |
        v
Servo PWM command
        |
        +----> Independent ESP32-S3 PWM witness
```

Authority recognition occurs directly on the XIAO immediately before physical command issuance.

No Raspberry Pi recognition boundary participates in the decision path.

## Authority Object

The tested authority object contains five bounded elements:

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

SHA-256 authority commitment:

```text
2452e70c9003739fd571a5e38752e54d526c1f7ee876ad3bed3041e09ca9c0cc
```

The device identity, context, action, nonce, and use constraint are therefore jointly represented in the verification material recognized by the endpoint.

## Recognition Path

The endpoint evaluates authority through the following path:

```text
request
   |
   v
exact authority schema
   |
   v
device / context / action / use constraints
   |
   v
canonical authority representation
   |
   v
SHA-256 commitment recognition
   |
   v
spent-state check
   |
   v
consume authority
   |
   v
physical command issuance
```

Authority consumption occurs before PWM command issuance.

No fallback acceptance path is present.

## Test Matrix

ESP-LOCAL-003 exercised:

- valid authority acceptance;
- exact replay;
- `max_uses` enlargement;
- nonce modification;
- device modification;
- context modification;
- action modification;
- additional authority fields;
- missing required authority fields; and
- valid authority after non-consuming mutation attempts.

The original authority was accepted and independently witnessed at the PWM output.

The exact replay was denied as `authority_spent`.

Modification of `max_uses` from `1` to `2` was denied as `use_constraint_invalid`.

Nonce modification was denied as `authority_commitment_mismatch`.

Device, context, and action mutations were denied by their corresponding local bounds.

Unexpected or incomplete authority representations were rejected.

The original authority remained admissible after the non-consuming mutation sequence and produced a second independently witnessed PWM command burst.

Detailed observations are recorded in [`RESULTS.md`](RESULTS.md).

## Independent Physical Witness

An ESP32-S3 DevKit independently monitored the servo PWM signal.

The witness did not participate in authority recognition or endpoint decision-making.

Two valid executions produced independently observed command bursts:

```text
BURST_START ticks_ms=244932
BURST_END pulses=50 duration_ms=978 pulse_min_us=426 pulse_max_us=2003
```

and:

```text
BURST_START ticks_ms=1047996
BURST_END pulses=51 duration_ms=999 pulse_min_us=426 pulse_max_us=2123
```

The retained witness evidence remained `IDLE` through the replay and mutation-denial observations between those accepted events.

Raw retained witness output is published in:

```text
ESP_LOCAL_003_WITNESS_LOG.txt
```

The witness establishes electrical PWM command issuance. It does not establish guaranteed mechanical movement or exactly-once mechanical execution.

The witness implementation is unchanged from ESP-LOCAL-001 and is intentionally published under its original filename to preserve artifact lineage.

## Result

**ESP-LOCAL-003: PASS**

The test demonstrated endpoint-local recognition of an externally established authority object whose tested bounds were jointly represented in verification material.

Modification or enlargement of those bounds did not produce physical command issuance.

Valid authority was consumed before execution and could not be reused during the same endpoint runtime.

Denied mutations did not independently consume the legitimate authority.

## Supported Claim

> A resource-constrained physical endpoint can locally recognize an externally established bounded authority object whose device, context, action, nonce, and use constraint are jointly represented in verification material, reject modification or enlargement of those bounds before physical command issuance, consume valid authority before execution, and deny subsequent reuse within the current runtime.

## Evidence Boundary

ESP-LOCAL-003 demonstrates integrity-bound authority recognition using a SHA-256 commitment.

It does not establish provider identity or asymmetric provider attribution.

Spent state is runtime-local and is not persistent across endpoint reboot.

The test does not establish:

- trusted time or expiration enforcement;
- secure boot;
- protected trust material;
- endpoint-compromise resistance;
- production cryptographic hardening;
- guaranteed mechanical movement; or
- exactly-once physical execution.

Provider-attributable asymmetric authority is evaluated separately in ESP-LOCAL-004.

## Evidence

- [`RESULTS.md`](RESULTS.md) — test matrix and observed results
- [`PROVENANCE.md`](PROVENANCE.md) — artifact and evidence lineage
- [`ESP_LOCAL_003_WITNESS_LOG.txt`](ESP_LOCAL_003_WITNESS_LOG.txt) — extracted contemporaneous COM8 witness output
- [`SHA256SUMS.txt`](SHA256SUMS.txt) — published artifact integrity manifest
