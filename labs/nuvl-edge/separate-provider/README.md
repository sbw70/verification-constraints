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

The separate-provider configuration preserves the existing NUVL authority split.

### Provider

The provider:

- originates authority within configured scope;
- retains private signing authority.

### NUVL Boundary

The boundary:

- verifies provider signatures;
- evaluates request and artifact binding;
- enforces scope, validity, replay, and use restrictions;
- rejects authority that does not satisfy configured admission conditions.

The boundary is not intended to originate or enlarge provider authority within the tested architecture.

Separate-provider validation evaluates whether this authority relationship remains intact when the provider is moved to independent infrastructure.

## Validation Set

### SP-001 — Separate-Provider Baseline

`sp001-baseline/`

SP-001 moves the existing Ed25519 provider and its private signing key to a physically separate host while retaining public-key verification at the Raspberry Pi boundary.

The test evaluates:

- remote provider operation;
- provider-authenticated bounded issuance;
- bounded artifact consumption;
- provider-unavailable fail-closed behavior;
- restoration without boundary restart or reprovisioning.

**Result: PASS**

### SP-002 — Unauthorized Provider Substitution

`sp002-provider-substitution/`

SP-002 retains the verification boundary and legitimate public trust anchor while replacing the legitimate provider with an unauthorized substitute at the expected provider service position.

The substitute reproduces the expected provider-facing representation but signs with an unrelated Ed25519 key.

The test evaluates whether provider position or representation can substitute for cryptographic provider authority.

**Result: PASS**

Detailed conditions, observations, evidence, and claim boundaries are maintained within the individual test directories.

## Experimental Progression

The validation sequence isolates two distinct questions:

    SP-001
    Can provider authority remain separate
    when the provider moves to another host?
            |
            v
           PASS

    SP-002
    Can another provider obtain authority
    merely by occupying the expected position?
            |
            v
           DENIED

SP-001 establishes the separate-provider baseline.

SP-002 then holds the boundary trust relationship constant while replacing the provider-side implementation and signing authority.

Together, the tests evaluate physical separation and provider substitution without changing the underlying bounded-authority model.

## Evidence Structure

Each test directory maintains its own evidence package.

Typical contents include:

    README.md
    RESULTS.md
    PROVENANCE.md
    SHA256SUMS.txt
    evidence/
    provider/
    boundary/
    trust/

Document responsibilities are separated as follows:

- `README.md` — test purpose, architecture, scope, and supported claim;
- `RESULTS.md` — executed conditions and observed outcomes;
- `PROVENANCE.md` — artifact lineage, test-time identity, and evidence provenance;
- `SHA256SUMS.txt` — authoritative integrity manifest for current published bytes;
- `evidence/` — retained runtime evidence where available.

Historical test-time artifact identity and current publication integrity are treated separately.

A later reproduction or evidence-capture run does not replace an earlier execution record and must be identified independently.

## Test Key Material

Ed25519 key material included within an individual test package is laboratory test material.

It has no production, operational, account, identity, or external trust relationship.

Publication of test key material is a reproducibility decision and does not alter the authority relationship evaluated by the tests.

## Supported Claims

The completed separate-provider validation supports the bounded claim that, within the tested configurations:

- provider signing authority operated on infrastructure physically separate from the NUVL verification/enforcement boundary;
- the boundary verified provider authority using public verification material without requiring the provider private signing key;
- loss of the separate provider prevented acquisition of new provider authority through the tested issuance path;
- provider-backed issuance resumed after restoration without restarting the boundary;
- an unauthorized provider occupying the expected provider service position did not obtain accepted authority when it lacked signing material corresponding to the boundary's configured trust anchor;
- restoration of the legitimate provider restored verified issuance without changing that trust anchor.

## Claim Boundary

The separate-provider validation does not, by itself, establish:

- security after arbitrary privileged compromise of the NUVL boundary;
- protection of mutable boundary trust configuration against privileged modification;
- endpoint-local Ed25519 verification;
- resistance to every malicious network intermediary condition;
- transport-layer authentication of the provider connection;
- resistance to denial-of-service at the provider position;
- production infrastructure security;
- production key-management security;
- provider high availability.

Those properties require separate evidence.

## Relationship to Existing NUVL Evidence

Separate-provider validation builds on the provider-authenticity and bounded-authority properties evaluated by earlier NUVL proofs.

The principal architectural variable introduced by SP-001 is physical separation of the provider authority source from the verification/enforcement boundary.

SP-002 introduces a provider-substitution condition while holding the boundary and legitimate trust anchor constant.

The governing invariant remains:

    provider originates bounded authority
                 |
                 v
    boundary may verify and enforce
                 |
                 v
    boundary does not receive provider signing authority
