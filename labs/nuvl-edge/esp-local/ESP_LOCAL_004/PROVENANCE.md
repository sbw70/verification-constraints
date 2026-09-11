# ESP-LOCAL-004 Provenance

## Test Identity

**Test:** ESP-LOCAL-004  
**Status:** PASS  
**Function:** Endpoint-local verification of provider-signed bounded authority using Ed25519

ESP-LOCAL-004 extended endpoint-local authority recognition from integrity-bound authority in ESP-LOCAL-003 to asymmetric provider verification.

The endpoint verified an Ed25519 signature against configured provider public-key trust material before local semantic enforcement, spent-state recognition, authority consumption, and physical command issuance.

The tested signed authority representation included:

- device identity;
- context;
- action;
- nonce; and
- maximum-use constraint.

---

## Tested Architecture

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

Authority verification, local admissibility recognition, consumption, and command gating occurred on the XIAO endpoint.

No Raspberry Pi recognition boundary participated in the decision path.

The provider private key was not present on the endpoint.

---

## Endpoint Identity

| Property | Value |
|---|---|
| Platform | Seeed XIAO ESP32-S3 |
| Device ID | `esp32-xiao-servo-01` |
| Context | `esp_local_004` |
| Authorized action | `move_servo` |
| Maximum uses | `1` |
| Servo output | GPIO 5 |
| Signature algorithm | Ed25519 |
| Spent-state scope | Runtime-local volatile memory |

---

## Frozen Authority Object

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

The device identity, context, action, nonce, and use constraint were jointly represented in the signed canonical authority object.

---

## Provider Key Material

The ESP-LOCAL-004 provider keypair was generated outside the endpoint.

Private-key artifact:

```text
provider/keys/esp_local_004_private.pem
```

Tested private-key SHA-256:

```text
DA0A36F274EFC6E3CE1C7643800B952B1AA2895201E5A6D6852D308729466509
```

The private key is excluded from the public repository.

Public-key artifact:

```text
esp_local_004_public.pem
```

Tested public-key SHA-256:

```text
B9B33C65DDA94C39D8E48A2C563F18A24B6B9B460280184F81882BFA5C97C7ED
```

The endpoint contained only public verification material.

The test establishes verification against the configured public key. It does not establish protected trust-anchor provisioning or storage.

---

## Provider Implementation

Provider source:

```text
provider/esp_local_004_provider.py
```

The provider implementation:

1. loaded the existing Ed25519 private key;
2. constructed the bounded authority object;
3. generated a fresh nonce;
4. serialized the authority into the canonical signed representation;
5. signed that representation using Ed25519; and
6. emitted the authority object, canonical representation, signature, and public verification material.

The provider was executed once to produce the frozen ESP-LOCAL-004 authority and signature used by the test.

Contemporaneous provider output is retained as:

```text
evidence/ESP_LOCAL_004_PROVIDER_OUTPUT.txt
```

---

## Endpoint Implementation

Primary endpoint source:

```text
firmware/esp_local_004_main.py
```

Tested-source SHA-256:

```text
6BBF7BAF88E5D058D5C7BEEC09CF9B2D5F794A61A7C5B4EBE4C80C9BCC90C80D
```

Ed25519 verification module:

```text
firmware/ed25519_verify.py
```

Tested-source SHA-256:

```text
92197116AE3C48D15DB86F513951424870090350D4EF959266EDEC8B45DC157C
```

ESP-LOCAL-003 baseline retained with the ESP-LOCAL-004 test artifacts:

```text
firmware/esp_local_003_baseline.py
```

The ESP-LOCAL-004 endpoint recognition path enforced:

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
device/context/action/use constraints
    ->
spent-state recognition
    ->
consume authority
    ->
physical command issuance
```

Signature verification occurred before local semantic enforcement and before the spent-state check.

Authority was consumed before PWM command issuance.

Spent state was maintained in volatile endpoint memory for this test.

No unsigned fallback acceptance path was present.

---

## Ed25519 Verification Implementation

The endpoint used a pure-Python Ed25519 verifier derived from the separately exercised XIAO ESP32-S3 Ed25519 feasibility gate.

The feasibility gate established functional SHA-512 and Ed25519 verification under MicroPython 1.28.0.

Observed feasibility-gate results included:

```text
sha512_ok=True
sha512_ms=58
valid_signature=True
valid_verify_ms=68806
tampered_signature=False
tampered_verify_ms=68825
ED25519_GATE_PASS=True
```

The approximately 68.8-second verification time is an implementation observation rather than an ESP-LOCAL-004 pass criterion.

The verifier establishes functional feasibility for this architecture test. It is not represented as a production-hardened, constant-time, side-channel-resistant, or performance-optimized cryptographic implementation.

---

## Signed-Authority Integrity Evidence

The original provider signature was retained while individual signed authority fields were modified.

Observed mutations included:

```text
max_uses: 1 -> 2
nonce modification
device modification
context modification
action modification
```

Each mutated signed representation was denied as:

```text
provider_signature_invalid
```

A direct mutation of the signature was also denied as:

```text
provider_signature_invalid
```

Because signature verification occurred before semantic enforcement and spent-state recognition, these cases exercised the cryptographic integrity of the signed authority representation independently of later local admissibility checks.

---

## Representation Enforcement

The endpoint required the exact tested envelope and authority schemas.

Observed denials included:

```text
missing signature
    -> unexpected_or_missing_envelope_field

extra envelope field
    -> unexpected_or_missing_envelope_field

extra authority field
    -> unexpected_or_missing_authority_field

missing authority field
    -> unexpected_or_missing_authority_field
```

These cases were rejected before physical command issuance.

---

## Wrong-Provider Evidence

A separate Ed25519 keypair was used to sign the exact same canonical authority representation.

Wrong-provider signature:

```text
YZrx3cSqUwPStBzvjPYETOKOasJZ+SJBJD7oFvDWwmt26ekwFvcxf9rJ666X/DBWMAZfp8BtK5cK5apka7DqAA==
```

The signature was valid Ed25519 material for the same canonical authority under a different signing key.

The endpoint remained configured with the original provider public key.

On a fresh, unspent endpoint, the wrong-provider request was denied as:

```text
provider_signature_invalid
```

Without resetting the endpoint, the authentic provider authority was then submitted and accepted as:

```text
authority_admissible
```

This sequence establishes that signature validity under an arbitrary Ed25519 key was insufficient. Verification had to succeed against the endpoint's configured provider public-key trust material.

The result establishes cryptographic attribution to possession of the private key corresponding to that configured public key. It does not independently establish organizational identity or a production PKI lifecycle.

---

## Independent Witness

ESP-LOCAL-004 reused the established independent ESP32-S3 PWM witness implementation.

Repository witness artifact:

```text
witness/esp_local_004_witness.py
```

The implementation retained the `ESP_LOCAL_001` identifier in its terminal output because the established witness logic was reused without changing the evidence identifier.

The witness independently monitored the servo PWM signal and did not participate in provider verification, authority recognition, spent-state management, or endpoint decision-making.

---

## Physical Witness Evidence

Following rejection of a `max_uses` enlargement attempt, the authentic provider authority was accepted without another endpoint reset.

The independent witness recorded:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=480381
ESP_LOCAL_001_WITNESS_BURST_END pulses=51 duration_ms=998 pulse_min_us=420 pulse_max_us=2001
```

A separate fresh wrong-provider sequence produced:

```text
wrong-provider signature
    ->
provider_signature_invalid
    ->
no accepted authority
```

followed, without resetting the endpoint, by authentic provider authority acceptance.

The independent witness then recorded:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=2198299
ESP_LOCAL_001_WITNESS_BURST_END pulses=51 duration_ms=999 pulse_min_us=425 pulse_max_us=2001
```

The retained witness output was `IDLE` before the authentic-provider actuation event in that sequence.

These observations establish that non-admissible authority did not independently produce the witnessed PWM command and did not consume the authentic provider authority.

The witness establishes electrical PWM command issuance. It does not establish guaranteed mechanical movement or exactly-once mechanical execution.

---

## Replay Evidence

After authentic authority had been consumed, exact reuse of the same signed authority envelope was denied as:

```text
authority_spent
```

The spent-state check occurred after successful signature verification.

The replay result establishes single-use enforcement within the current endpoint runtime.

Spent state was not persistent across endpoint reboot in ESP-LOCAL-004.

---

## Evidence Lineage

ESP-LOCAL-004 evidence consists of distinct artifact classes:

| Artifact class | Provenance |
|---|---|
| Provider implementation | Source used to generate the frozen signed authority |
| Provider private key | Local test artifact; excluded from publication |
| Provider public key | Verification material corresponding to the test provider |
| Provider output | Contemporaneously retained output from frozen authority generation |
| Endpoint implementation | Source executed on the XIAO ESP32-S3 during ESP-LOCAL-004 |
| Ed25519 verifier | Pure-Python verification implementation executed by the endpoint |
| ESP-LOCAL-003 baseline | Pre-004 endpoint baseline retained for lineage |
| Witness implementation | Reused independent ESP32-S3 PWM witness |
| Witness observations | Contemporaneously retained terminal output from ESP-LOCAL-004 execution |

Repository SHA-256 manifests identify the exact bytes published in the repository.

Tested-source and published-copy digests are distinct provenance identities when their byte representations differ. No byte-identity claim is implied solely by functional equivalence.

---

## Supported Evidence

ESP-LOCAL-004 supports the following claim:

> A resource-constrained physical endpoint can locally verify provider-signed bounded authority against configured public-key trust material, reject tampering, attempted enlargement, unsigned requests, malformed authority representations, and signatures from an untrusted provider before physical command issuance, while preserving valid authority for subsequent authenticated execution.

The test additionally establishes that the provider private key need not be present at the physical endpoint for local authority verification.

---

## Evidence Boundary

ESP-LOCAL-004 establishes endpoint-local asymmetric verification against configured provider public-key trust material.

It does not establish:

- secure provisioning of the provider public key;
- protected trust-anchor storage;
- secure boot;
- endpoint-compromise resistance;
- hardware-backed key custody;
- production PKI lifecycle;
- persistent spent-state across endpoint reboot;
- trusted time or expiration enforcement;
- constant-time cryptographic execution;
- side-channel resistance;
- production Ed25519 performance;
- guaranteed mechanical movement; or
- exactly-once physical execution.

The provider private key remained external to the endpoint.

The endpoint possessed public verification material only.
