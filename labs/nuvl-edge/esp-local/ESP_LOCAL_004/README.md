# ESP-LOCAL-004

## Endpoint-Local Provider-Signed Bounded Authority Verification

ESP-LOCAL-004 demonstrates that a resource-constrained physical endpoint can locally verify provider-signed bounded authority against configured public-key trust material before physical command issuance.

The test extends ESP-LOCAL-003 from integrity-bound authority recognition to asymmetric provider verification using Ed25519.

The endpoint rejected modification or enlargement of signed authority, unsigned requests, malformed authority representations, altered signatures, replay, and a valid signature produced by a different provider key.

**Status: PASS**

## Architecture

```text
External provider
  Ed25519 private key
        |
        | signed bounded authority
        v
Seeed XIAO ESP32-S3
  configured provider public key
  local Ed25519 verification
  local bound enforcement
  spent-state check
        |
        v
Servo PWM command
        |
        +----> Independent ESP32-S3 PWM witness
```

Provider verification, local admissibility recognition, authority consumption, and physical command gating occur directly on the XIAO endpoint.

No Raspberry Pi recognition boundary participates in the decision path.

The provider private key is not present on the endpoint.

## Signed Authority Object

The tested authority object contains five bounded elements:

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

Configured provider raw public key:

```text
48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1
```

The device identity, context, action, nonce, and maximum-use constraint are jointly represented in the provider-signed canonical authority object.

## Recognition Path

The endpoint evaluates received authority through the following path:

```text
request envelope
   |
   v
exact envelope schema
   |
   v
exact authority schema
   |
   v
canonical authority representation
   |
   v
Ed25519 provider-signature verification
   |
   v
device / context / action / use constraints
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

Signature verification occurs before local semantic enforcement and before spent-state recognition.

Authority consumption occurs before PWM command issuance.

No unsigned fallback acceptance path is present.

## Provider Authority Separation

The provider holds the Ed25519 private key used to sign the bounded authority object.

The XIAO endpoint holds only the corresponding public verification material.

The endpoint therefore verifies authority without possessing the cryptographic material required to originate a provider signature.

ESP-LOCAL-004 does not establish protected provisioning or storage of that public trust material.

## Test Matrix

ESP-LOCAL-004 exercised:

- authentic provider authority acceptance;
- exact replay;
- `max_uses` enlargement;
- nonce modification;
- device modification;
- context modification;
- action modification;
- signature modification;
- unsigned authority;
- additional envelope fields;
- additional authority fields;
- missing authority fields;
- a valid Ed25519 signature from a different provider key; and
- authentic provider authority following non-consuming denial attempts.

Signed-field mutations using the original provider signature were denied as:

```text
provider_signature_invalid
```

The exact replay was denied as:

```text
authority_spent
```

Unsigned and structurally invalid requests were rejected before physical command issuance.

Detailed observations are recorded in [`RESULTS.md`](RESULTS.md).

## Attempted Authority Enlargement

The signed use constraint:

```text
max_uses: 1
```

was modified to:

```text
max_uses: 2
```

without changing the original provider signature.

The endpoint denied the modified authority as:

```text
provider_signature_invalid
```

Without another endpoint reset, the authentic provider authority was subsequently accepted.

The independent witness recorded:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=480381
ESP_LOCAL_001_WITNESS_BURST_END pulses=51 duration_ms=998 pulse_min_us=420 pulse_max_us=2001
```

The rejected enlargement attempt therefore did not consume or corrupt the authentic authority.

## Signed-Field Integrity

The original provider signature was retained while independently modifying the signed:

- nonce;
- device identity;
- context;
- action; and
- maximum-use constraint.

Each modified signed representation failed Ed25519 verification against the configured provider public key.

Because signature verification occurs before semantic enforcement and spent-state recognition, these cases establish integrity protection of the complete tested signed authority representation.

## Wrong-Provider Verification

A separate Ed25519 keypair was used to produce a valid signature over the exact same canonical authority object.

Wrong-provider signature:

```text
YZrx3cSqUwPStBzvjPYETOKOasJZ+SJBJD7oFvDWwmt26ekwFvcxf9rJ666X/DBWMAZfp8BtK5cK5apka7DqAA==
```

The endpoint remained configured with the original provider public key.

On a fresh, unspent endpoint, the wrong-provider request was denied as:

```text
provider_signature_invalid
```

Without resetting the endpoint, the authentic provider authority was then submitted and accepted as:

```text
authority_admissible
```

The independent witness recorded:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=2198299
ESP_LOCAL_001_WITNESS_BURST_END pulses=51 duration_ms=999 pulse_min_us=425 pulse_max_us=2001
```

The retained witness output was `IDLE` before the authentic-provider actuation event.

A mathematically valid Ed25519 signature from an untrusted key was therefore insufficient for authority admissibility.

The signature had to verify against the endpoint's configured provider public-key trust material.

## Replay Recognition

After authentic authority was consumed, exact reuse of the same signed authority envelope was denied as:

```text
authority_spent
```

The replay check occurs after successful provider-signature verification.

Single-use state is maintained in volatile endpoint memory for ESP-LOCAL-004 and does not survive endpoint reboot.

## Independent Physical Witness

An ESP32-S3 DevKit independently monitored the servo PWM signal.

The witness does not participate in:

- provider-signature verification;
- authority recognition;
- local admissibility decisions;
- spent-state management; or
- command issuance.

The reused witness implementation retains the `ESP_LOCAL_001` identifier in its terminal output.

Observed authentic-provider PWM command bursts included:

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

## Ed25519 Implementation

ESP-LOCAL-004 uses a pure-Python Ed25519 verifier derived from the separately tested XIAO ESP32-S3 feasibility implementation.

The feasibility gate demonstrated functional Ed25519 verification under MicroPython 1.28.0.

Observed verification latency was approximately 68.8 seconds per verification in that implementation.

This latency is an implementation observation, not an ESP-LOCAL-004 pass criterion.

The verifier is a functional architecture-test implementation. ESP-LOCAL-004 does not use it to claim production cryptographic performance, constant-time execution, side-channel resistance, or production hardening.

## Result

**ESP-LOCAL-004: PASS**

The test demonstrated endpoint-local asymmetric verification of provider-signed bounded authority against configured public-key trust material.

Modification or enlargement of the signed authority representation failed provider-signature verification.

Unsigned or structurally invalid authority was rejected.

A valid Ed25519 signature produced by a different provider key was not admissible under the endpoint's configured provider trust material.

Non-consuming denial attempts preserved the authentic provider authority.

Authentic authority was consumed before physical command issuance and exact reuse was denied during the current runtime.

## Supported Claim

> A resource-constrained physical endpoint can locally verify provider-signed bounded authority against configured public-key trust material, reject tampering, attempted enlargement, unsigned requests, malformed authority representations, and signatures from an untrusted provider before physical command issuance, while preserving valid authority for subsequent authenticated execution.

ESP-LOCAL-004 additionally demonstrates that the provider private key need not be present on the physical endpoint for local verification of provider-signed authority.

## Evidence Boundary

ESP-LOCAL-004 establishes asymmetric verification against configured provider public-key trust material.

Cryptographic attribution in this test means successful verification against the public key configured as the trusted provider key. It does not independently establish organizational identity.

Spent state is runtime-local and is not persistent across endpoint reboot.

The test does not establish:

- secure provisioning of provider public-key trust material;
- protected trust-anchor storage;
- secure boot;
- endpoint-compromise resistance;
- hardware-backed key custody;
- production PKI lifecycle;
- persistent replay state;
- trusted time or expiration enforcement;
- constant-time cryptographic execution;
- side-channel resistance;
- production Ed25519 performance;
- guaranteed mechanical movement; or
- exactly-once physical execution.

## Evidence

- [`RESULTS.md`](RESULTS.md) — test matrix and observed results
- [`PROVENANCE.md`](PROVENANCE.md) — artifact, key, and evidence lineage
- [`evidence/ESP_LOCAL_004_PROVIDER_OUTPUT.txt`](evidence/ESP_LOCAL_004_PROVIDER_OUTPUT.txt) — retained frozen provider authority-generation output
- [`SHA256SUMS.txt`](SHA256SUMS.txt) — published artifact integrity manifest
