# POC-001 — HMAC Bounded Disconnected Authority

## Purpose

POC-001 evaluates bounded authorization during temporary provider unavailability.

The test establishes an initial NUVL disconnected-authority model in which normal authorization remains provider-first while a previously issued, request-bound artifact may authorize one matching request during a temporary loss of provider connectivity.

POC-001 uses HMAC-SHA256 authentication. The shared-secret trust model is an intentional limitation of this proof and is superseded by the asymmetric provider-authenticity architecture introduced in POC-002.

## Test Classification

**Category:** NUVL core — no architecture change  
**Capability:** Bounded disconnected authority  
**Primary objective:** Determine whether temporary provider loss can be accommodated without introducing unrestricted local fallback authority.

## Architecture

The tested topology was:

    ESP32-S3
        |
        | Wi-Fi
        v
    GL.iNet Mango GL-MT300N-V2
        |
        v
    Raspberry Pi 5
    NUVL boundary
        |
        v
    Windows provider

During normal operation, authorization followed the provider-first path:

    endpoint request
          |
          v
    NUVL boundary
          |
          v
    provider validation
          |
          +---- admissible ----> ACCEPT
          |
          +---- inadmissible --> DENY

During provider unavailability, the boundary could evaluate a previously issued bounded artifact:

    provider unavailable
          |
          v
    NUVL boundary
          |
          v
    validate bounded artifact
          |
          +---- invalid ----> DENY
          |
          +---- valid ------> ACCEPT ONCE

Provider unavailability alone did not create authorization.

## Bounded Authority Model

The provider-issued artifact was authenticated using HMAC-SHA256 and bound to:

- requested action;
- context;
- request representation;
- unique nonce;
- issuance time;
- expiration time;
- maximum-use count.

The tested artifact specified a maximum use count of one.

During provider unavailability, acceptance required successful validation of the complete bounded-artifact constraints. Missing, malformed, expired, mismatched, or previously consumed artifacts were denied.

Single-use replay state was maintained by the Raspberry Pi boundary for the lifetime of the running boundary process.

## Test Matrix

POC-001 exercised the following conditions:

| Condition | Expected Result |
|---|---|
| Provider reachable; admissible request | ACCEPT |
| Provider unavailable; valid bounded artifact | ACCEPT once |
| Consumed artifact replay | DENY |
| Missing artifact | DENY |
| Wrong context | DENY |
| Wrong action | DENY |
| Expired artifact | DENY |
| Provider restored | Provider-backed operation restored |

Detailed observations and recorded outcomes are maintained in `RESULTS.md`.

## Security Property Evaluated

POC-001 evaluates whether provider unavailability can be handled through previously bounded authority rather than unrestricted local fallback.

The tested implementation required affirmative validation of an existing bounded artifact before admitting a request while the provider was unavailable.

The disconnected path therefore remained constrained by previously established provider parameters rather than treating provider loss as an implicit authorization condition.

## Trust-Model Limitation

POC-001 uses a shared HMAC secret between the provider and Raspberry Pi boundary.

This permits the boundary to authenticate provider-issued artifacts, but possession of the shared secret also provides the cryptographic capability required to generate valid HMAC authentication values.

POC-001 therefore does **not** establish exclusive provider cryptographic issuance authority.

This limitation motivated the transition to Ed25519 asymmetric signatures in POC-002:

    POC-001
    shared HMAC secret
    provider + boundary
            |
            v
    POC-002
    provider private signing key
    boundary public verification key
            |
            v
    POC-003
    asymmetric bounded disconnected
    single-use authority

POC-002 separates signing authority from verification capability. POC-003 applies that asymmetric trust model to bounded disconnected authorization.

## Evidence Package

This directory contains:

- `ddil_provider.py` — provider implementation used by POC-001;
- `RESULTS.md` — test conditions, observed behavior, and result assessment;
- `PROVENANCE.md` — source lineage and retained-artifact provenance;
- `SHA256SUMS.txt` — integrity manifest for published artifacts.

The Raspberry Pi boundary implementation used for the original test is not published in this directory.

The original interactive terminal transcript was not retained. No reconstructed terminal output is represented as original runtime evidence.

## Supported Claims

POC-001 supports the bounded claim that, within the tested configuration:

- normal authorization remained provider-first while the provider was available;
- a previously issued bounded artifact could authorize one matching request during provider unavailability;
- missing, invalid, expired, mismatched, and replayed artifacts were denied;
- provider unavailability did not independently create authorization;
- provider-backed operation resumed after provider restoration.

## Limitations

POC-001 does not establish:

- exclusive provider cryptographic issuance authority;
- asymmetric provider authenticity;
- endpoint-local cryptographic verification;
- persistent spent-state across boundary restart or power loss;
- crash-safe spend persistence;
- multi-boundary double-spend resistance;
- exactly-once physical execution;
- protection against arbitrary privileged compromise of the Raspberry Pi boundary.

These properties require separate evidence and are addressed, where applicable, by subsequent NUVL tests.

## Result

**PASS**

POC-001 demonstrated bounded, single-use disconnected authorization during temporary provider unavailability while retaining fail-closed behavior when valid bounded authority was absent.

The experiment also identified the shared-secret trust limitation that motivated the asymmetric provider-authenticity architecture evaluated beginning with POC-002.
