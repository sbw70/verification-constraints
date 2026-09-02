# POC-002 — Ed25519 Provider Authenticity

## Overview

POC-002 tested asymmetric provider authority in the NUVL validation path.

The proof replaced the shared-secret trust model used in the preceding HMAC experiment with an Ed25519 model in which the provider retained the private signing key and the Raspberry Pi NUVL boundary held only the corresponding public verification key.

The objective was to determine whether the boundary could recognize valid provider authority while rejecting stale, modified, unsigned, incorrectly scoped, or incorrectly bound provider output without possessing the provider's private signing authority.

POC-002A extended the same configuration to provider-unavailable recovery and deliberate trust-anchor substitution.

## Test Classification

**Category:** NUVL core — no architecture change.

**Capability:** Provider-authenticated bounded authority.

**Use case:** A constrained endpoint requests an action through an intermediary boundary while the provider remains the source of authoritative signed decisions.

## Authority Placement

The tested authority relationship was:

```text
Provider
  |
  | Ed25519 private signing key retained here
  |
  | signed provider decision
  v
Raspberry Pi NUVL boundary
  |
  | provider public verification key only
  | signature / expiry / request-binding validation
  |
  v
ESP32-S3 endpoint
```

The provider private key was not installed on the Raspberry Pi or ESP32 endpoint.

Ed25519 verification occurred at the Raspberry Pi boundary.

This test did not implement Ed25519 verification directly on the ESP32.

## Hardware

The July 19–20, 2026 bench consisted of:

- one ESP32-S3 endpoint;
- GL.iNet Mango GL-MT300N-V2 wireless access point;
- Raspberry Pi 5 running the NUVL verification boundary;
- Windows laptop running the provider.

The logical request path was:

```text
ESP32-S3
    |
    | Wi-Fi
    v
GL.iNet Mango
    |
    v
Raspberry Pi 5
NUVL boundary
    |
    v
Windows provider
```

POC-002 was a single-endpoint proof. The repeated matrix represents repeated transactions against the test endpoint, not a multi-endpoint fleet test.

## POC-002 Test Matrix

The endpoint test client exercised eight provider-authenticity and request-binding conditions.

| Case | Condition | Expected result |
|---|---|---|
| 1 | Valid signed acceptance | ACCEPT |
| 2 | Valid signed denial | DENY |
| 3 | Validly signed stale provider artifact | DENY |
| 4 | Provider artifact modified after signing | DENY |
| 5 | Unsigned provider artifact | DENY |
| 6 | Request made under an unauthorized/wrong context | DENY |
| 7 | Signed provider artifact bound to a different context | DENY |
| 8 | Signed provider artifact bound to a different nonce/request | DENY |

The initial matrix exercised all eight conditions once.

A separate repeat harness then exercised the complete eight-case matrix ten times.

Detailed observed results are recorded in `RESULTS.md`.

## POC-002A — Provider Unavailable / Recovery

POC-002A tested whether loss of the provider could cause the boundary to accept an action without a verified provider decision.

The sequence was:

```text
Provider available
    |
    v
signed provider decision verified
    |
    v
ACCEPT

Provider unavailable
    |
    v
no verified provider decision
    |
    v
DENY / provider_unavailable

Provider restored
    |
    v
signed provider decision verified
    |
    v
ACCEPT
```

The recovery portion tested restoration of normal provider-backed acceptance without resetting the Raspberry Pi boundary or ESP32 endpoint.

## Trust-Anchor Substitution

The same POC-002 configuration was used to test an intentionally incorrect verification key.

The configured provider public key on the Raspberry Pi was replaced with an unrelated Ed25519 public key while the provider continued signing with its original private key.

The sequence was:

```text
Correct provider public key
    |
    v
provider signature verifies
    |
    v
ACCEPT

Unrelated public key substituted
    |
    v
provider signature cannot be verified
    |
    v
DENY / invalid_provider_signature

Correct provider public key restored
    |
    v
provider signature verifies
    |
    v
ACCEPT
```

The alternate public key retained from this test is included as:

`poc002_wrong_trust_anchor_public.pem`

The private key associated with that deliberately unrelated test keypair is not published.

## Public Files

### `poc002_ed25519_provider.py`

Provider implementation used to create Ed25519-signed provider decisions.

The publication copy has environment-specific addressing sanitized where required.

### `poc002_ed25519_public.pem`

Public verification key corresponding to the provider signing key used for the test.

The provider private key is intentionally excluded.

### `poc002_wrong_trust_anchor_public.pem`

Unrelated public verification key used during the deliberate trust-anchor substitution test.

Its corresponding private key is intentionally excluded.

### `poc002_esp32_test.py`

ESP32-side eight-case POC-002 matrix client.

### `poc002_esp32_matrix_repeat.py`

Repeat harness that executes the eight-case matrix ten times.

### `poc002a_esp32_probe.py`

Endpoint probe used while externally changing provider availability and the configured Pi trust anchor.

### `RESULTS.md`

Recorded POC-002 and POC-002A results and evidence limitations.

### `PROVENANCE.md`

Artifact provenance, original tested-source hashes, publication-copy distinctions, and independently retained Raspberry Pi artifact hashes.

### `SHA256SUMS.txt`

SHA-256 manifest for the files actually published in this directory.

## Publication Boundary

The Raspberry Pi enforcement-boundary implementation is not published in this directory.

Its original tested source was independently retained on both the Windows test host and Raspberry Pi. Matching SHA-256 digests are recorded in `PROVENANCE.md`.

This allows the surviving tested artifact to be identified without publishing the boundary implementation.

Private Ed25519 signing keys are also excluded.

Publication copies of files containing environment-specific public addressing were sanitized before publication.

A sanitized derivative must not be represented as byte-identical to the original tested source when its SHA-256 digest differs.

## Evidence Status

The original interactive terminal transcript from the July 19–20, 2026 execution was not retained.

No replacement or reconstructed terminal log is presented as original evidence.

The surviving evidence includes:

- original test source retained from the July execution;
- the test matrix and repeat harness;
- contemporaneous laboratory records of the observed results;
- the original Raspberry Pi boundary source independently retained on the Pi and Windows test host;
- the original provider public verification key independently retained on both systems;
- the deliberately incorrect public trust anchor retained on the Raspberry Pi;
- SHA-256 correspondence between independently retained artifacts.

See `RESULTS.md` and `PROVENANCE.md` for the evidence record.

## What POC-002 Supports

POC-002 supports the narrower claim that a NUVL boundary configured with the provider's public verification key can validate provider-signed decisions without possessing the provider's private signing key.

The test also demonstrates rejection of:

- stale signed provider output;
- provider output modified after signing;
- unsigned provider output;
- unauthorized request context;
- signed output bound to a different context;
- signed output bound to a different request nonce;
- signatures that cannot be validated against the configured provider trust anchor.

POC-002A additionally demonstrates fail-closed behavior when the provider is unavailable and restoration of provider-backed acceptance after provider service recovery.

## What POC-002 Does Not Support

POC-002 does not demonstrate that a Raspberry Pi remains trustworthy after arbitrary privileged compromise.

Possession of only a public verification key prevents that key from being used to generate a valid provider signature. It does not, by itself, prevent privileged malicious software on the enforcement boundary from bypassing the verification procedure entirely.

The trust-anchor substitution test demonstrates rejection when the configured public key does not correspond to the provider signing key.

It does not demonstrate protection of the mutable Raspberry Pi trust-anchor file against privileged replacement.

POC-002 also does not demonstrate:

- direct Ed25519 verification by the ESP32;
- multi-endpoint or fleet behavior;
- persistent single-use disconnected authority;
- crash-safe spent-state persistence;
- exactly-once physical execution.

Those properties require separate tests.

## Relationship to Subsequent Work

POC-002 established the asymmetric trust relationship used by subsequent NUVL experiments:

```text
provider retains signing authority
             |
             v
boundary receives verification authority
             |
             v
boundary may recognize provider authority
but does not receive the provider private key
```

The subsequent POC-003 work combined this asymmetric provider-authenticity model with bounded disconnected single-use authority.

Later persistence and race tests address properties outside the scope of POC-002.
