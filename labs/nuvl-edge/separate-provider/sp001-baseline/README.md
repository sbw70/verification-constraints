# NUVL Separate-Provider Validation

## Purpose

This directory contains validation of NUVL with provider authority hosted on infrastructure physically separate from the NUVL verification/enforcement boundary.

The objective is to determine whether the existing provider-controlled bounded-authority model remains enforceable when the provider and its private signing key execute on a separate host.

## Architecture

The separate-provider configuration places the provider and verification/enforcement boundary on different physical systems:

    Separate Provider Host
    Ed25519 private signing key
            |
            | network
            v
    NUVL Verification / Enforcement Boundary
    Ed25519 public verification key
            |
            v
    Bounded execution path

The provider originates signed authority.

The NUVL boundary receives and evaluates provider-signed authority using public verification material. Physical separation does not require transfer of the provider private signing key to the boundary.

## Authority Model

The separate-provider configuration preserves the existing NUVL authority split:

**Provider**
- originates authority within configured scope;
- retains private signing authority.

**NUVL boundary**
- verifies provider signatures;
- evaluates request and artifact binding;
- enforces scope, validity, replay, and use restrictions;
- rejects authority that does not satisfy the configured admission conditions.

The boundary is not intended to originate or enlarge provider authority within the tested architecture.

Separate-provider testing evaluates whether that authority relationship remains intact when the provider is moved to independent infrastructure.

## Validation Set

Current validation includes:

- `sp001-baseline/` — physically separate provider baseline, including provider-unavailable fail-closed behavior and restoration;
- `sp002-provider-substitution/` — unauthorized provider substitution using the expected provider position and artifact representation but a different Ed25519 signing key.

Each test directory contains its own scope, results, provenance, evidence, source artifacts, and integrity manifest.

Detailed behavioral claims are maintained within the individual test packages rather than in this parent directory.

## Evidence Model

Individual test packages may contain:

- `README.md` — test purpose, architecture, scope, and claim boundary;
- `RESULTS.md` — observed test conditions and outcomes;
- `PROVENANCE.md` — artifact lineage and original/tested-source identity;
- source and configuration artifacts required for reproduction;
- captured runtime evidence where retained;
- `SHA256SUMS.txt` — integrity manifest for the published package.

Later reproduction or validation evidence is identified separately from original test-time evidence.

No reconstructed output is represented as original runtime evidence.

## Test Key Material

Laboratory Ed25519 key material included in an individual test package is test-only material.

It has no production, operational, account, identity, or external trust relationship.

Publication of test key material is a reproducibility decision and does not alter the authority model evaluated by the test.

## Scope

Separate-provider validation evaluates:

- physical separation of provider and enforcement infrastructure;
- retention of provider private signing authority on the provider host;
- public-key verification at the NUVL boundary;
- behavior during provider unavailability and restoration;
- behavior when an unauthorized provider occupies the expected provider position but cannot produce signatures valid under the configured trust anchor.

A completed test supports only the properties directly exercised by that test.

This validation set does not, by itself, establish:

- security after arbitrary privileged compromise of the NUVL boundary;
- endpoint-local Ed25519 verification;
- resistance to every malicious-intermediary condition;
- production infrastructure security;
- production key-management security;
- provider high availability;
- protection of mutable trust configuration against privileged modification.

## Relationship to Existing NUVL Evidence

Separate-provider validation builds on the provider-authenticity and bounded-authority properties established by earlier NUVL proofs.

The principal variable introduced by SP-001 is physical separation of the provider authority source from the verification/enforcement boundary.

SP-002 then evaluates a distinct condition: whether occupying the expected provider network position is sufficient to obtain authority without possession of signing material trusted by the boundary.

Across both tests, the governing invariant remains:

    provider originates bounded authority
                 |
                 v
    boundary may verify and enforce
                 |
                 v
    boundary does not receive provider signing authority
