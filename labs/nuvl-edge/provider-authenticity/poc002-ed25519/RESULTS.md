# POC-002 / POC-002A Results

## Summary

POC-002 tested Ed25519-authenticated provider decisions using a provider-held private signing key and public-key verification at the Raspberry Pi NUVL boundary.

POC-002A extended the test to provider loss/recovery and deliberate substitution of the configured provider trust anchor.

The original tests were performed July 19–20, 2026.

## POC-002 — Initial Provider-Authenticity Matrix

The initial test exercised eight conditions.

| Case | Condition | Expected | Observed |
|---|---|---|---|
| 1 | Valid signed acceptance | ACCEPT | ACCEPT |
| 2 | Valid signed denial | DENY | DENY |
| 3 | Validly signed stale provider artifact | DENY | DENY |
| 4 | Provider artifact modified after signing | DENY | DENY |
| 5 | Unsigned provider artifact | DENY | DENY |
| 6 | Request made under unauthorized/wrong context | DENY | DENY |
| 7 | Signed provider artifact bound to different context | DENY | DENY |
| 8 | Signed provider artifact bound to different nonce/request | DENY | DENY |

**Result: 8/8 expected outcomes observed.**

Representative denial reasons recorded by the test included:

- `stale_provider_artifact`
- `invalid_provider_signature`
- `missing_signature`
- `wrong_context`
- `provider_binding_mismatch_context`
- `provider_binding_mismatch_nonce`

The test configuration reported:

```text
private_key_on_endpoint=False
signature_verification_location=pi_boundary
```

## POC-002 — Repeated Matrix

The complete eight-case matrix was subsequently repeated ten times.

```text
matrices=10
cases_per_matrix=8
total_cases=80
passed=80
failed=0
transport_failures=0
```

**Result: 80/80 expected outcomes observed with zero recorded transport failures.**

The repeat test exercised the same acceptance, denial, stale-artifact, tampering, unsigned, context, and nonce-binding conditions on each matrix iteration.

## Memory Observation

The repeated matrix also recorded ESP32 free-memory observations.

Recorded values included:

```text
baseline_free=177056
final_free=176128
delta=-928
```

The post-matrix free-memory measurements occupied a range of approximately 176 bytes.

The first matrix showed a free-memory change of approximately -656 bytes.

The tenth matrix showed a change of approximately -832 bytes relative to the original baseline.

The difference between the first and final matrix measurements was approximately 176 bytes.

These observations were consistent with a small initial allocation effect rather than memory consumption growing proportionally with each matrix iteration.

This was an observational memory check, not a dedicated long-duration memory-leak qualification test.

## POC-002A — Provider Unavailable / Recovery

POC-002A changed provider availability while leaving the Raspberry Pi boundary and ESP32 endpoint in place.

### Provider Available

Observed:

```text
decision=accepted
reason=provider_admissible
provider_verified=true
```

The provider was reachable and the boundary obtained and verified a signed provider decision.

**Result: ACCEPT.**

### Provider Unavailable

The provider process was stopped while the Raspberry Pi boundary remained available.

Observed:

```text
decision=denied
reason=provider_unavailable
provider_verified=false
```

No verified provider decision was available.

**Result: DENY.**

No accepted endpoint action was recorded for the unavailable-provider condition.

### Provider Restored

The provider was restarted.

Observed:

```text
decision=accepted
reason=provider_admissible
provider_verified=true
```

Provider-backed acceptance resumed without resetting the Raspberry Pi boundary or ESP32 endpoint.

**Result: ACCEPT.**

### POC-002A Sequence

```text
PROVIDER AVAILABLE
        |
        v
ACCEPT
provider_verified=true

        ↓

PROVIDER UNAVAILABLE
        |
        v
DENY
provider_unavailable
provider_verified=false

        ↓

PROVIDER RESTORED
        |
        v
ACCEPT
provider_verified=true
```

**Result: PASS.**

The unavailable state did not create a fallback acceptance path.

## Trust-Anchor Substitution Test

The provider remained associated with its original Ed25519 signing key while the public verification key configured at the Raspberry Pi boundary was deliberately changed.

### Correct Trust Anchor

The Raspberry Pi was configured with the public key corresponding to the provider private signing key.

Observed:

```text
decision=accepted
provider_verified=true
```

**Result: ACCEPT.**

### Incorrect Trust Anchor

The configured provider public key was replaced with an unrelated Ed25519 public key.

The provider continued signing with its original private key.

Observed:

```text
decision=denied
reason=invalid_provider_signature
provider_verified=false
```

**Result: DENY.**

### Correct Trust Anchor Restored

The original provider public key was restored and the Raspberry Pi boundary restarted with the correct verification key.

Observed:

```text
decision=accepted
reason=provider_admissible
provider_verified=true
```

**Result: ACCEPT.**

The ESP32 endpoint did not require a reset for restoration.

### Trust-Anchor Sequence

```text
CORRECT PUBLIC KEY
        |
        v
ACCEPT
provider_verified=true

        ↓

UNRELATED PUBLIC KEY
        |
        v
DENY
invalid_provider_signature
provider_verified=false

        ↓

CORRECT PUBLIC KEY RESTORED
        |
        v
ACCEPT
provider_verified=true
```

**Result: PASS.**

## Consolidated Results

| Test | Result |
|---|---|
| Initial eight-case Ed25519 matrix | PASS — 8/8 |
| Ten repeated matrices | PASS — 80/80 |
| Repeat transport failures | 0 |
| Valid signed acceptance | PASS |
| Valid signed denial | PASS |
| Stale signed artifact rejection | PASS |
| Modified-after-signing rejection | PASS |
| Unsigned artifact rejection | PASS |
| Wrong-context rejection | PASS |
| Signed context-binding mismatch rejection | PASS |
| Signed nonce-binding mismatch rejection | PASS |
| Provider unavailable | PASS — fail closed |
| Provider recovery | PASS — acceptance restored |
| Wrong trust anchor | PASS — signature rejected |
| Correct trust anchor restored | PASS |
| Provider private key absent from endpoint | Confirmed by test configuration |
| Signature verification location | Raspberry Pi boundary |

## Evidence Record

The original interactive terminal transcript from the July 19–20, 2026 execution was not retained.

The numerical and behavioral results above are transcribed from the contemporaneous NUVL hardware laboratory record and are consistent with the surviving test-source logic.

They are not presented as a reconstructed raw terminal log.

The surviving source includes:

- the eight-case ESP32 test client;
- the ten-matrix repeat harness;
- the POC-002A probe;
- the provider implementation;
- the provider public verification key;
- the deliberately incorrect public verification key used for trust-anchor substitution.

The original Raspberry Pi boundary implementation also survives independently on the Raspberry Pi and Windows test host.

Its independently retained copies have matching SHA-256 digests.

The correct provider public key likewise survives independently on both systems with matching SHA-256 digests.

See `PROVENANCE.md` for the artifact-level record.

## Interpretation

POC-002 demonstrated that provider decisions could be authenticated at the NUVL boundary using asymmetric signatures while the provider retained the private signing key.

A valid signature alone was not sufficient for acceptance. The boundary also evaluated temporal validity and request binding.

The tested implementation rejected provider output when it was stale, modified, unsigned, associated with an unauthorized context, or bound to a different context or request nonce.

POC-002A demonstrated that loss of provider availability did not create an acceptance fallback. In the tested unavailable state, the request was denied because no verified provider decision was available.

The trust-anchor substitution test demonstrated that a signature generated by the provider was not accepted when verification was attempted against an unrelated configured public key.

Restoring the correct public key restored provider-backed acceptance.

## Claim Boundary

These results support configured asymmetric provider authenticity at the tested Raspberry Pi NUVL boundary.

They do not establish that the Raspberry Pi remains trustworthy after arbitrary privileged compromise.

The wrong-trust-anchor test establishes fail-closed behavior when the boundary executes the tested verification logic using a public key that does not correspond to the provider signing key.

It does not establish that a privileged attacker is unable to replace the trust-anchor file, modify the verification code, bypass verification, or directly alter the boundary's returned decision.

The test also does not establish:

- direct Ed25519 verification on the ESP32;
- multi-endpoint behavior;
- persistent disconnected spend-state;
- crash-safe persistence;
- exactly-once physical execution.

Those properties are addressed, where applicable, by separate NUVL proofs.
