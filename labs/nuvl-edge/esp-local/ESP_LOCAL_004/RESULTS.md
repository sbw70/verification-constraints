# ESP-LOCAL-004 Results

## Status

**PASS**

ESP-LOCAL-004 demonstrated endpoint-local verification of provider-signed bounded authority on a Seeed XIAO ESP32-S3.

The endpoint verified an Ed25519 signature against configured provider public-key trust material before evaluating local authority semantics, spent state, and physical command issuance.

The tested implementation rejected:

- modification of signed authority fields;
- attempted enlargement of the signed use constraint;
- malformed or incomplete authority representations;
- unsigned authority;
- altered signatures; and
- a valid Ed25519 signature produced by a different provider key.

Valid authority was consumed before PWM command issuance.

## Test Configuration

| Property | Value |
|---|---|
| Endpoint | Seeed XIAO ESP32-S3 |
| Device ID | `esp32-xiao-servo-01` |
| Context | `esp_local_004` |
| Authorized action | `move_servo` |
| Maximum uses | `1` |
| Signature algorithm | Ed25519 |
| Physical output | Servo PWM |
| Independent witness | ESP32-S3 DevKit |
| Spent-state scope | Runtime-local volatile memory |

Configured provider raw public key:

```text
48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1
```

Frozen authority object:

```json
{
  "device_id": "esp32-xiao-servo-01",
  "context": "esp_local_004",
  "action": "move_servo",
  "nonce": "0d66fb58f65ea7ed6f26afe393add3c1",
  "max_uses": 1
}
```

Canonical signed representation:

```text
{"action":"move_servo","context":"esp_local_004","device_id":"esp32-xiao-servo-01","max_uses":1,"nonce":"0d66fb58f65ea7ed6f26afe393add3c1"}
```

Frozen provider signature:

```text
GVv8Fvwxigoogi4vsO6At+fu54hV9wAfMKyDX2Ycjot3cKFZ4ImsXMCesCw2HJh2fLGo6XZzBuewxjvdSg65BQ==
```

## Recognition Path

The endpoint evaluated received authority through the following path:

```text
request envelope
    ->
exact envelope schema
    ->
exact authority schema
    ->
canonical authority representation
    ->
Ed25519 signature verification
    ->
local device/context/action/use constraints
    ->
spent-state recognition
    ->
consume authority
    ->
physical command issuance
```

Signature verification occurred before local semantic checks and before the spent-state check.

No unsigned fallback path was present.

## Test Matrix

| Test case | Result | Decision reason | Physical result |
|---|---|---|---|
| Authentic provider authority | **ACCEPT** | `authority_admissible` | PWM command observed in retained control sequence |
| Exact replay | **DENY** | `authority_spent` | No additional authority acceptance |
| `max_uses: 1` → `2` with original signature | **DENY** | `provider_signature_invalid` | No PWM from mutated request |
| Nonce mutation with original signature | **DENY** | `provider_signature_invalid` | No PWM |
| Device mutation with original signature | **DENY** | `provider_signature_invalid` | No PWM |
| Context mutation with original signature | **DENY** | `provider_signature_invalid` | No PWM |
| Action mutation with original signature | **DENY** | `provider_signature_invalid` | No PWM |
| Signature mutation | **DENY** | `provider_signature_invalid` | No PWM |
| Missing signature | **DENY** | `unexpected_or_missing_envelope_field` | No PWM |
| Extra envelope field | **DENY** | `unexpected_or_missing_envelope_field` | No PWM |
| Extra authority field | **DENY** | `unexpected_or_missing_authority_field` | No PWM |
| Missing authority field | **DENY** | `unexpected_or_missing_authority_field` | No PWM |
| Valid signature from different provider key | **DENY** | `provider_signature_invalid` | No PWM in fresh physical-control sequence |
| Authentic provider authority after wrong-provider denial | **ACCEPT** | `authority_admissible` | Independent PWM burst observed |

## Authentic Provider Acceptance

The authentic provider authority object and frozen signature were submitted to the endpoint.

Result:

```text
decision  reason                device_id
--------  ------                ---------
accepted  authority_admissible  esp32-xiao-servo-01
```

This established successful endpoint-local Ed25519 verification against the configured provider public key.

The first successful spend was not paired with a confirmed independent witness capture and is not used as the primary physical-evidence event.

## Replay Rejection

The exact authentic authority envelope was submitted again without resetting the endpoint.

Result:

```json
{"reason": "authority_spent", "decision": "denied"}
```

The replay was denied after signature verification.

This established current-runtime single-use enforcement for the authenticated authority.

## Use-Constraint Enlargement

After returning the endpoint to an unspent state, the signed field:

```text
max_uses: 1
```

was modified to:

```text
max_uses: 2
```

while retaining the original provider signature.

Result:

```json
{"reason": "provider_signature_invalid", "decision": "denied"}
```

The attempted enlargement altered the signed canonical authority representation and therefore failed provider-signature verification.

The authentic authority was then submitted without another endpoint reset.

Result:

```text
accepted / authority_admissible
```

The independent witness recorded:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=480381
ESP_LOCAL_001_WITNESS_BURST_END pulses=51 duration_ms=998 pulse_min_us=420 pulse_max_us=2001
```

This control established that the rejected enlargement attempt did not consume or corrupt the authentic authority and that the authentic authority subsequently reached electrical PWM command issuance.

## Signed-Field Mutation Matrix

Additional mutations were applied while retaining the original provider signature.

### Nonce mutation

The signed nonce was changed from:

```text
0d66fb58f65ea7ed6f26afe393add3c1
```

to a different value.

Result:

```json
{"reason": "provider_signature_invalid", "decision": "denied"}
```

### Device mutation

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
{"reason": "provider_signature_invalid", "decision": "denied"}
```

### Context mutation

The context was changed from:

```text
esp_local_004
```

to:

```text
esp_local_005
```

Result:

```json
{"reason": "provider_signature_invalid", "decision": "denied"}
```

### Action mutation

The action was changed from:

```text
move_servo
```

to:

```text
open_valve
```

Result:

```json
{"reason": "provider_signature_invalid", "decision": "denied"}
```

Because signature verification preceded local semantic and spent-state checks, each mutation directly exercised integrity protection of the signed authority representation.

## Signature Mutation

The frozen Base64 signature was modified while leaving the authority object unchanged.

Result:

```json
{"reason": "provider_signature_invalid", "decision": "denied"}
```

The endpoint did not accept the altered cryptographic proof.

## Envelope and Representation Enforcement

An authority request without a signature was rejected:

```json
{"reason": "unexpected_or_missing_envelope_field", "decision": "denied"}
```

An envelope containing an additional field was rejected:

```json
{"reason": "unexpected_or_missing_envelope_field", "decision": "denied"}
```

An authority object containing an additional field was rejected:

```json
{"reason": "unexpected_or_missing_authority_field", "decision": "denied"}
```

An authority object missing the required `nonce` field was also rejected:

```json
{"reason": "unexpected_or_missing_authority_field", "decision": "denied"}
```

The endpoint therefore required both the tested envelope structure and the tested authority-object structure rather than silently ignoring unrecognized or missing fields.

## Wrong-Provider Signature

A second Ed25519 keypair was used to produce a mathematically valid Ed25519 signature over the exact same canonical authority object.

Wrong-provider signature:

```text
YZrx3cSqUwPStBzvjPYETOKOasJZ+SJBJD7oFvDWwmt26ekwFvcxf9rJ666X/DBWMAZfp8BtK5cK5apka7DqAA==
```

The endpoint remained configured with the original provider public key.

On a fresh, unspent endpoint, the wrong-provider authority request was submitted.

Result:

```json
{"reason": "provider_signature_invalid", "decision": "denied"}
```

The wrong-provider request did not consume the authentic provider authority.

Without resetting the endpoint, the authentic provider authority was then submitted.

Result:

```text
accepted / authority_admissible
```

The independent witness recorded:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=2198299
ESP_LOCAL_001_WITNESS_BURST_END pulses=51 duration_ms=999 pulse_min_us=425 pulse_max_us=2001
```

The retained witness output was `IDLE` before the authentic actuation event.

This sequence established that a valid Ed25519 signature from a different key was not admissible under the endpoint's configured provider trust material and that the rejection did not consume or corrupt the authentic authority.

## Provider-Key Attribution Result

ESP-LOCAL-004 does not treat signature validity in isolation as sufficient authority.

The signature must verify against the endpoint's configured provider public key.

The wrong-provider case therefore demonstrated:

```text
valid Ed25519 signature
        +
different signing key
        =
not admissible
```

followed by:

```text
same authority object
        +
signature from configured provider key
        =
admissible
```

This establishes cryptographic attribution to possession of the private key corresponding to the endpoint's configured provider public key.

It does not independently establish organizational identity, PKI lifecycle, or secure trust-anchor provisioning.

## Independent Physical Witness

The physical witness was an ESP32-S3 DevKit monitoring the servo PWM line independently from the authority-recognition path.

The witness implementation retained the `ESP_LOCAL_001` identifier because it reused the established witness code.

Observed authentic-provider command bursts included:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=480381
ESP_LOCAL_001_WITNESS_BURST_END pulses=51 duration_ms=998 pulse_min_us=420 pulse_max_us=2001
```

and:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=2198299
ESP_LOCAL_001_WITNESS_BURST_END pulses=51 duration_ms=999 pulse_min_us=425 pulse_max_us=2001
```

The witness establishes electrical PWM command issuance.

It does not establish guaranteed mechanical movement or exactly-once mechanical execution.

## Ed25519 Feasibility and Performance Observation

The endpoint used a pure-Python Ed25519 verifier derived from the separately tested XIAO MicroPython feasibility gate.

The feasibility gate established:

```text
sha512_ok=True
sha512_ms=58
valid_signature=True
valid_verify_ms=68806
tampered_signature=False
tampered_verify_ms=68825
ED25519_GATE_PASS=True
```

The test therefore established functional Ed25519 verification feasibility under MicroPython 1.28.0 on the XIAO ESP32-S3.

The approximately 68.8-second verification latency is an implementation observation, not an ESP-LOCAL-004 pass criterion.

The verifier is a reference-style pure-Python implementation and is not used to support claims of production cryptographic performance or hardening.

## Result

**ESP-LOCAL-004: PASS**

The test demonstrated that a resource-constrained physical endpoint could:

- locally verify Ed25519-signed bounded authority;
- require verification against configured provider public-key trust material;
- reject signed-field modification;
- reject attempted enlargement of the use constraint;
- reject altered signatures;
- reject unsigned authority;
- reject malformed or incomplete authority representations;
- reject a valid signature created by a different provider key;
- preserve authentic authority across non-consuming denial attempts;
- consume authentic authority before physical command issuance; and
- deny exact reuse during the current runtime.

## Supported Claim

> A resource-constrained physical endpoint can locally verify provider-signed bounded authority against configured public-key trust material, reject tampering, attempted enlargement, unsigned requests, malformed authority representations, and signatures from an untrusted provider before physical command issuance, while preserving valid authority for subsequent authenticated execution.

## Evidence Boundary

ESP-LOCAL-004 establishes endpoint-local asymmetric verification against configured provider public-key trust material.

The test does not establish:

- secure provisioning or protected storage of the provider public key;
- secure boot;
- endpoint-compromise resistance;
- hardware-backed key custody;
- production PKI lifecycle;
- persistent spent-state across endpoint reboot;
- trusted time or expiration enforcement;
- constant-time or side-channel-hardened Ed25519 verification;
- production cryptographic performance;
- guaranteed mechanical movement; or
- exactly-once physical execution.

The provider private key was not present on the endpoint.

The endpoint held only provider public-key verification material.
