# SP-001 — Separate-Provider Baseline

## Purpose

SP-001 evaluates whether the existing NUVL provider-controlled bounded-authority path continues to operate when the provider and its Ed25519 private signing key are moved to a physically separate host from the Raspberry Pi verification/enforcement boundary.

The test changes provider placement without changing the underlying provider-authenticity or bounded-authority model.

**Overall Result: PASS**

## Test Classification

**Category:** NUVL core with deployment variation — no architecture change  
**Capability:** Separate-provider operation  
**Primary objective:** Validate remote provider operation, fail-closed provider loss, and restoration without transferring provider signing authority to the boundary.

## Architecture

The tested topology was:

    Separate Provider Host
    Ed25519 private signing key
            |
            | network
            v
    Raspberry Pi NUVL Boundary
    Ed25519 public verification key
            |
            v
    Bounded authority / spend path

The provider executed on a separate Linux host.

The Raspberry Pi boundary retained the corresponding public verification key and did not hold the provider private signing key.

## Authority Model

The provider:

- originates bounded authority;
- retains private Ed25519 signing authority.

The NUVL boundary:

- contacts the provider for new authority;
- verifies provider signatures;
- evaluates artifact and request binding;
- enforces bounded-use and replay conditions;
- does not require possession of the provider private signing key.

SP-001 evaluates whether this authority relationship remains intact when provider execution is moved to separate infrastructure.

## Test Sequence

SP-001 exercised three principal conditions:

| Phase | Provider Condition | Expected |
|---|---|---|
| Baseline | Separate provider online | Verified issuance and bounded spend |
| Unavailable | Separate provider stopped | New issuance denied |
| Restoration | Same provider restored | Verified issuance resumes |

All expected conditions were observed.

Detailed runtime observations are maintained in `RESULTS.md`.

## Separate-Provider Baseline

The separate provider successfully issued Ed25519-signed bounded authority across the network to the Raspberry Pi boundary.

The boundary verified that authority using the configured public trust anchor.

A fresh bounded artifact was subsequently accepted through the spend path without contacting the provider for the spend.

The existing persistent spent-state enforcement remained in use.

## Provider-Unavailable Control

The provider process was stopped while the Raspberry Pi boundary remained operational.

A new authority request was denied with:

    decision: denied
    provider_verified: false
    reason: provider_unavailable

No new artifact was returned through the tested issuance path.

**Result: PASS**

## Provider Restoration

The same provider implementation was restarted on the separate host.

The Raspberry Pi boundary was not restarted or reprovisioned.

Verified provider issuance resumed through the same running boundary.

**Result: PASS**

## Evidence Package

This directory contains:

    sp001-baseline/
    ├── README.md
    ├── RESULTS.md
    ├── PROVENANCE.md
    ├── SHA256SUMS.txt
    ├── evidence/
    │   └── sp001_control_evidence.log
    ├── provider/
    │   ├── poc003_ed25519_provider_1h.py
    │   └── poc002_ed25519_private.pem
    ├── boundary/
    │   └── sp001_separate_provider_boundary.py
    └── trust/
        └── poc002_ed25519_public.pem

`RESULTS.md` records executed conditions and observed outcomes.

`PROVENANCE.md` records source lineage, test-time artifact identity, host correspondence, and evidence provenance.

`evidence/sp001_control_evidence.log` contains the retained provider-availability control record.

`SHA256SUMS.txt` is the integrity manifest for the published package.

## Supported Claim

SP-001 supports the bounded claim that, within the tested configuration:

- provider signing authority operated on a host physically separate from the NUVL verification/enforcement boundary;
- the boundary verified provider-signed authority using public verification material;
- bounded authority could be consumed without contacting the provider during the spend operation;
- loss of the separate provider prevented acquisition of new provider authority through the tested issuance path;
- restoration of the same provider restored verified issuance without restarting or reprovisioning the boundary.

## Claim Boundary

SP-001 does not establish:

- rejection of an unauthorized substitute provider;
- protection against a compromised or malicious network intermediary;
- security after arbitrary privileged compromise of the Raspberry Pi boundary;
- protection of mutable boundary trust configuration against privileged modification;
- endpoint-local Ed25519 verification;
- production key-management security;
- production provider infrastructure security;
- provider high availability.

Unauthorized provider substitution is evaluated separately by SP-002.

## Relationship to SP-002

SP-001 establishes the separate-provider baseline.

SP-002 then preserves the same verification boundary and legitimate trust anchor while replacing the provider with an unauthorized substitute using an unrelated signing key.

The progression is:

    SP-001
    physically separate legitimate provider
            |
            v
    verified authority preserved


    SP-002
    unauthorized provider at expected position
            |
            v
    authority rejected
