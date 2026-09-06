# POC-002 — Ed25519 Provider Authenticity

## Purpose

POC-002 evaluates asymmetric provider authority in the NUVL validation path.

The test replaces the shared-secret HMAC relationship used in POC-001 with an Ed25519 trust model in which the provider retains the private signing key and the Raspberry Pi NUVL boundary holds only the corresponding public verification key.

The objective is to determine whether the boundary can recognize valid provider authority while rejecting stale, modified, unsigned, incorrectly scoped, or incorrectly bound provider output without possessing the provider's private signing authority.

POC-002A extends the same architecture to provider-unavailable recovery and deliberate trust-anchor substitution.

## Test Classification

**Category:** NUVL core — no architecture change  
**Capability:** Provider-authenticated bounded authority  
**Primary objective:** Validate provider-signed decisions at an intermediary enforcement boundary without transferring provider signing authority to that boundary.

## Authority Model

The tested trust relationship was:

    Provider
      |
      | Ed25519 private signing key
      |
      | signed provider decision
      v
    Raspberry Pi NUVL boundary
      |
      | provider public verification key only
      | signature validation
      | expiration validation
      | request-binding validation
      |
      v
    ESP32-S3 endpoint

The provider private signing key was not installed on the Raspberry Pi or ESP32 endpoint.

Ed25519 verification occurred at the Raspberry Pi boundary.

POC-002 does not implement Ed25519 verification directly on the ESP32.

## Test Architecture

The July 19–20, 2026 bench consisted of:

- one ESP32-S3 endpoint;
- GL.iNet Mango GL-MT300N-V2 wireless access point;
- Raspberry Pi 5 running the NUVL verification boundary;
- Windows host running the provider.

The tested request path was:

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

POC-002 was a single-endpoint proof. Repeated matrix execution represents repeated transactions against the same test architecture rather than a multi-endpoint fleet test.

## POC-002 Test Matrix

The test client exercised eight provider-authenticity and request-binding conditions:

| Case | Condition | Expected Result |
|---|---|---|
| 1 | Valid signed acceptance | ACCEPT |
| 2 | Valid signed denial | DENY |
| 3 | Validly signed stale provider artifact | DENY |
| 4 | Provider artifact modified after signing | DENY |
| 5 | Unsigned provider artifact | DENY |
| 6 | Request under unauthorized context | DENY |
| 7 | Signed artifact bound to different context | DENY |
| 8 | Signed artifact bound to different request nonce | DENY |

The initial matrix exercised all eight conditions once.

A separate repeat harness then executed the complete eight-case matrix ten times.

Detailed observations and aggregate results are maintained in `RESULTS.md`.

## Provider-Unavailable Control

POC-002A evaluated whether provider loss could result in acceptance without a verified provider decision.

The tested sequence was:

    provider available
            |
            v
    signed decision verified
            |
            v
    ACCEPT


    provider unavailable
            |
            v
    no verified provider decision
            |
            v
    DENY


    provider restored
            |
            v
    signed decision verified
            |
            v
    ACCEPT

The recovery condition evaluated restoration of normal provider-backed operation without resetting the Raspberry Pi boundary or ESP32 endpoint.

## Trust-Anchor Substitution Control

POC-002A also evaluated behavior when the Raspberry Pi was configured with an unrelated Ed25519 public key while the legitimate provider continued signing with its original private key.

The tested sequence was:

    correct provider public key
            |
            v
    provider signature verifies
            |
            v
    ACCEPT


    unrelated public key configured
            |
            v
    provider signature does not verify
            |
            v
    DENY


    correct public key restored
            |
            v
    provider signature verifies
            |
            v
    ACCEPT

This condition evaluates trust-anchor correctness at the verification boundary.

It does not establish protection of the Raspberry Pi trust-anchor file against privileged modification.

## Security Property Evaluated

POC-002 evaluates separation between provider signing authority and boundary verification authority.

Within the tested architecture:

- the provider retained the Ed25519 private signing key;
- the Raspberry Pi boundary received only the corresponding public verification key;
- provider output was admitted only after successful cryptographic and request-binding validation;
- invalid provider output was rejected without requiring possession of the provider private key at the boundary.

The test therefore evaluates whether provider authority can be recognized without transferring provider signing capability to the enforcement boundary.

## Evidence Package

This directory contains the provider, test clients, verification material, results, provenance record, and integrity manifest associated with POC-002 and POC-002A.

Key published artifacts include:

- `poc002_ed25519_provider.py`
- `poc002_ed25519_public.pem`
- `poc002_wrong_trust_anchor_public.pem`
- `poc002_esp32_test.py`
- `poc002_esp32_matrix_repeat.py`
- `poc002a_esp32_probe.py`
- `RESULTS.md`
- `PROVENANCE.md`
- `SHA256SUMS.txt`

Artifact lineage, original tested-source identity, publication derivatives, and retained cross-host correspondence are documented in `PROVENANCE.md`.

Current repository integrity values are maintained in `SHA256SUMS.txt`.

## Evidence Status

The original interactive terminal transcript from the July 19–20, 2026 execution was not retained.

No reconstructed terminal output is presented as original runtime evidence.

The surviving evidence includes:

- retained test source;
- the eight-case matrix client;
- the repeated-matrix harness;
- contemporaneous laboratory records;
- independently retained verification material;
- retained Raspberry Pi boundary source;
- deliberate wrong-trust-anchor material.

Detailed evidence status and artifact provenance are documented separately in `PROVENANCE.md`.

## Supported Claims

POC-002 supports the bounded claim that, within the tested configuration:

- the provider retained the Ed25519 private signing key;
- the Raspberry Pi boundary verified provider decisions using the corresponding public key;
- the boundary did not require the provider private key to validate signed provider output;
- stale signed provider output was rejected;
- provider output modified after signing was rejected;
- unsigned provider output was rejected;
- unauthorized request context was rejected;
- signed output bound to a different context was rejected;
- signed output bound to a different request nonce was rejected;
- provider signatures that could not be validated against the configured trust anchor were rejected.

POC-002A additionally supports:

- fail-closed behavior when the provider was unavailable;
- restoration of provider-backed acceptance after provider recovery;
- rejection of legitimate provider signatures when an unrelated verification key was configured;
- restoration of valid verification after the correct trust anchor was restored.

## Claim Boundary

POC-002 does not establish that the Raspberry Pi remains trustworthy after arbitrary privileged compromise.

Possession of only a public verification key prevents that key from being used to create a legitimate provider signature, but it does not prevent compromised boundary software from bypassing the verification procedure itself.

POC-002 also does not establish:

- protection of the Raspberry Pi trust-anchor file against privileged replacement;
- direct Ed25519 verification by the ESP32;
- multi-endpoint or fleet behavior;
- persistent single-use disconnected authority;
- crash-safe spent-state persistence;
- exactly-once physical execution.

Those properties require separate evidence.

## Relationship to Subsequent Work

POC-002 establishes the asymmetric trust relationship used by subsequent NUVL experiments:

    provider retains signing authority
                 |
                 v
    boundary receives verification authority
                 |
                 v
    boundary may recognize provider authority
    without receiving the provider private key

POC-003 subsequently combines this asymmetric provider-authenticity model with bounded disconnected single-use authority.

Later persistence, race, crash-window, and actuator tests evaluate properties outside the scope of POC-002.
