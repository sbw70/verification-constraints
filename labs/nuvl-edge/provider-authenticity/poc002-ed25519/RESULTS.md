# POC-002 / POC-002A Results

## Summary

POC-002 evaluated Ed25519-authenticated provider decisions using a provider-held private signing key and public-key verification at the Raspberry Pi NUVL boundary.

POC-002A extended the same configuration to provider unavailability/recovery and deliberate substitution of the configured provider trust anchor.

The original tests were performed July 19–20, 2026.

## POC-002 — Initial Provider-Authenticity Matrix

The initial test exercised eight provider-authenticity and request-binding conditions.

| Case | Condition | Expected | Observed |
|---|---|---|---|
| 1 | Valid signed acceptance | ACCEPT | ACCEPT |
| 2 | Valid signed denial | DENY | DENY |
| 3 | Validly signed stale provider artifact | DENY | DENY |
| 4 | Provider artifact modified after signing | DENY | DENY |
| 5 | Unsigned provider artifact | DENY | DENY |
| 6 | Request under unauthorized context | DENY | DENY |
| 7 | Signed provider artifact bound to different context | DENY | DENY |
| 8 | Signed provider artifact bound to different nonce/request | DENY | DENY |

**Result: PASS — 8/8 expected outcomes observed.**

Representative recorded denial reasons included:

    stale_provider_artifact
    invalid_provider_signature
    missing_signature
    wrong_context
    provider_binding_mismatch_context
    provider_binding_mismatch_nonce

The test configuration reported:

    private_key_on_endpoint=False
    signature_verification_location=pi_boundary

Ed25519 verification therefore occurred at the Raspberry Pi boundary rather than at the ESP32 endpoint.

## POC-002 — Repeated Matrix

The complete eight-case matrix was subsequently executed ten times.

Recorded aggregate results were:

    matrices=10
    cases_per_matrix=8
    total_cases=80
    passed=80
    failed=0
    transport_failures=0

**Result: PASS — 80/80 expected outcomes observed with zero recorded transport failures.**

The repeated execution covered the same acceptance, denial, stale-artifact, modification, unsigned-artifact, context, and nonce-binding conditions as the initial matrix.

## Memory Observation

The repeated matrix also recorded ESP32 free-memory measurements.

Recorded values included:

    baseline_free=177056
    final_free=176128
    delta=-928

Post-matrix free-memory measurements occupied a range of approximately 176 bytes.

The first matrix showed a change of approximately -656 bytes relative to the original baseline. The tenth matrix showed a change of approximately -832 bytes.

The difference between the first and final matrix measurements was approximately 176 bytes.

These observations are consistent with a small initial allocation effect rather than memory consumption increasing proportionally with matrix count.

This was an observational check during repeated execution, not a dedicated long-duration memory-leak qualification test.

## POC-002A — Provider Unavailable / Recovery

POC-002A changed provider availability while leaving the Raspberry Pi boundary and ESP32 endpoint in service.

### Provider Available

Observed:

    decision=accepted
    reason=provider_admissible
    provider_verified=true

**Result: ACCEPT**

The boundary obtained and verified a provider decision while the provider was available.

### Provider Unavailable

The provider process was stopped while the Raspberry Pi boundary remained available.

Observed:

    decision=denied
    reason=provider_unavailable
    provider_verified=false

**Result: DENY**

No accepted endpoint action was recorded for the provider-unavailable condition.

The unavailable state therefore did not create an acceptance fallback.

### Provider Restored

The provider process was restarted.

Observed:

    decision=accepted
    reason=provider_admissible
    provider_verified=true

**Result: ACCEPT**

Provider-backed acceptance resumed without resetting the Raspberry Pi boundary or ESP32 endpoint.

### Provider-Availability Result

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
    provider_verified=false

            ↓

    PROVIDER RESTORED
            |
            v
    ACCEPT
    provider_verified=true

**Result: PASS**

## Trust-Anchor Substitution

The provider continued using its original Ed25519 signing key while the public verification key configured at the Raspberry Pi boundary was deliberately changed.

### Correct Trust Anchor

With the public key corresponding to the provider signing key configured at the boundary:

    decision=accepted
    provider_verified=true

**Result: ACCEPT**

### Incorrect Trust Anchor

The configured provider public key was replaced with an unrelated Ed25519 public key.

The provider continued signing with its original private key.

Observed:

    decision=denied
    reason=invalid_provider_signature
    provider_verified=false

**Result: DENY**

The provider signature was not admitted under the unrelated verification key.

### Correct Trust Anchor Restored

The original provider public key was restored and the Raspberry Pi boundary restarted with the correct verification key.

Observed:

    decision=accepted
    reason=provider_admissible
    provider_verified=true

**Result: ACCEPT**

The ESP32 endpoint did not require a reset.

### Trust-Anchor Result

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

**Result: PASS**

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
| Provider unavailable | PASS — denied |
| Provider recovery | PASS — acceptance restored |
| Wrong trust anchor | PASS — signature rejected |
| Correct trust anchor restored | PASS |
| Signature verification location | Raspberry Pi boundary |

## Evidence Status

The original interactive terminal transcript from the July 19–20, 2026 execution was not retained.

The numerical and behavioral results documented here derive from the contemporaneous NUVL hardware laboratory record.

No reconstructed terminal output is represented as original runtime evidence.

Artifact identity, retained-source correspondence, publication status, and cryptographic file provenance are documented separately in `PROVENANCE.md`.

## Result Assessment

POC-002 demonstrated, within the tested configuration, that provider decisions could be authenticated at the Raspberry Pi NUVL boundary using Ed25519 signatures without placing the provider private signing key at the endpoint.

The initial and repeated matrices established the expected handling of:

- valid signed acceptance;
- valid signed denial;
- stale signed provider output;
- modification after signing;
- unsigned provider output;
- unauthorized request context;
- signed context-binding mismatch;
- signed nonce-binding mismatch.

The results also establish that a valid cryptographic signature was not, by itself, sufficient for acceptance. Temporal validity and request binding were evaluated as part of the provider-decision validation path.

POC-002A demonstrated that provider unavailability resulted in denial rather than fallback acceptance and that provider-backed acceptance resumed after provider restoration.

The trust-anchor substitution condition demonstrated rejection when the configured verification key did not correspond to the provider signing key.

## Claim Boundary

These results support configured asymmetric provider authenticity at the tested Raspberry Pi NUVL boundary.

They do not establish that the Raspberry Pi remains trustworthy after arbitrary privileged compromise.

The trust-anchor substitution condition establishes fail-closed behavior while the boundary executes the tested verification logic using a public key that does not correspond to the provider signing key. It does not establish protection against privileged replacement of the trust-anchor file, modification of verification code, bypass of verification, or direct manipulation of the boundary result.

The tests also do not establish:

- direct Ed25519 verification on the ESP32;
- multi-endpoint behavior;
- persistent disconnected spend-state;
- crash-safe persistence;
- exactly-once physical execution.

Those properties require separate evidence.
