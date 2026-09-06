# NUVL Provider Authenticity Validation

## Purpose

This directory contains validation of provider authenticity within the NUVL bounded-authority architecture.

The objective is to determine whether the NUVL verification boundary accepts authority only when that authority is attributable to the configured provider trust relationship.

The validation progression moves from a shared-secret laboratory baseline to asymmetric Ed25519 provider signing.

## Architecture

The provider-authenticity path is:

    Provider
    authority source
            |
            | authenticated decision / bounded artifact
            v
    NUVL Verification Boundary
            |
            v
    accepted or denied execution path

The provider originates authority within configured scope.

The verification boundary evaluates whether received authority satisfies the configured provider-authenticity and request-binding conditions before admitting it to the bounded execution path.

## Validation Set

### POC-001 — HMAC Provider Authenticity

`poc001-hmac/`

POC-001 established the initial provider-authenticated bounded-authority path using HMAC-SHA256.

The test evaluated:

- provider-backed authorization;
- bounded provider-issued artifact use during provider unavailability;
- single-use enforcement;
- replay denial;
- request-context and action binding;
- expiry enforcement;
- fail-closed behavior when no admissible provider authority was available.

**Result: PASS**

POC-001 established the behavioral model but retained a shared-secret limitation: the verification boundary possessed the same HMAC secret used to authenticate provider authority.

That trust placement was removed in POC-002.

### POC-002 — Ed25519 Provider Authenticity

`poc002-ed25519/`

POC-002 replaced the shared HMAC trust relationship with asymmetric Ed25519 signing.

The provider retained the private signing key.

The Raspberry Pi NUVL boundary retained only the corresponding public verification key.

The test evaluated:

- valid provider-signed acceptance;
- signed provider denial;
- stale provider artifacts;
- modified artifacts;
- unsigned artifacts;
- request-context mismatches;
- provider artifact binding mismatches;
- repeated execution of the provider-authenticity matrix;
- provider-unavailable fail-closed behavior;
- rejection under an incorrect public trust anchor;
- restoration under the correct trust anchor.

**Result: PASS**

Ed25519 verification in POC-002 occurred at the Raspberry Pi NUVL boundary.

POC-002 did not demonstrate direct Ed25519 verification on the ESP32 endpoint.

## Experimental Progression

The provider-authenticity work isolates a specific trust transition:

    POC-001
    shared HMAC secret
    provider <----> boundary
            |
            v
    provider authenticity demonstrated
    but verifier can also possess minting secret


    POC-002
    provider private signing key
            |
            | Ed25519
            v
    boundary public verification key
            |
            v
    provider authenticity without
    transferring signing authority

The progression removes the verification boundary's need to possess provider signing material.

## Authority Model

### Provider

The provider:

- originates authority;
- defines the permitted request scope;
- authenticates that authority;
- retains private signing material in the asymmetric configuration.

### NUVL Boundary

The boundary:

- receives provider decisions or artifacts;
- verifies provider authenticity;
- evaluates request and artifact binding;
- enforces validity and bounded-use conditions;
- rejects authority that fails configured admission checks.

In the Ed25519 configuration, possession of the public verification key does not confer the cryptographic ability to generate a valid provider signature.

## Evidence Structure

Each validation directory maintains its own evidence package.

Typical contents include:

    README.md
    RESULTS.md
    PROVENANCE.md
    SHA256SUMS.txt
    provider/
    boundary/
    evidence/

Document responsibilities are separated as follows:

- `README.md` — test purpose, architecture, scope, and supported claim;
- `RESULTS.md` — executed conditions and observed outcomes;
- `PROVENANCE.md` — artifact lineage, historical test identity, and evidence provenance;
- `SHA256SUMS.txt` — authoritative integrity manifest for current published bytes;
- `evidence/` — retained runtime evidence where available.

Historical test-time hashes and current publication hashes are intentionally treated as separate records.

## Supported Claims

The provider-authenticity validation supports the bounded claim that, within the tested configurations:

- provider-originated authority was distinguishable from unauthenticated or invalid authority;
- stale, modified, unsigned, or improperly bound provider artifacts were denied;
- provider unavailability did not produce accepted new authority through the tested fail-closed path;
- Ed25519 allowed the provider to retain private signing authority while the Raspberry Pi boundary performed verification using public-key material;
- an incorrect verification key caused otherwise legitimate provider authority to fail verification;
- restoration of the configured provider trust relationship restored accepted provider-backed authorization.

## Claim Boundary

The provider-authenticity validation does not, by itself, establish:

- protection of mutable boundary trust-anchor files against privileged modification;
- security after arbitrary privileged compromise of the Raspberry Pi boundary;
- endpoint-local Ed25519 verification;
- transport-layer authentication of the provider connection;
- resistance to every malicious intermediary condition;
- production key-management security;
- production provider infrastructure security.

A compromised verification boundary with arbitrary code-execution capability remains outside the demonstrated trust boundary. Public-key-only possession prevents that boundary from generating a legitimate provider signature, but does not by itself prevent malicious boundary software from bypassing its own verification logic.

## Relationship to Subsequent NUVL Evidence

Provider-authenticity validation establishes the trust foundation used by later NUVL tests.

Subsequent work extends this model into:

- disconnected bounded authority;
- persistent spent-state enforcement;
- concurrent double-spend controls;
- crash-window durability;
- physically separate provider infrastructure;
- unauthorized provider substitution.

The governing trust relationship established by POC-002 is:

    provider retains signing authority
                |
                v
    boundary receives verification authority
                |
                v
    accepted authority remains provider-authenticated
