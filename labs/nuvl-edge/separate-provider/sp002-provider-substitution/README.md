# SP-002 — Unauthorized Provider Substitution

## Purpose

SP-002 evaluates whether occupying the expected provider network and service position is sufficient to originate authority accepted by the NUVL verification boundary.

The test replaces the legitimate provider with an unauthorized substitute while leaving the NUVL boundary and its configured Ed25519 public trust anchor unchanged.

The substitute reproduces the expected provider-facing representation but signs with an unrelated Ed25519 private key.

**Overall Result: PASS**

## Test Classification

**Category:** NUVL core — no architecture change  
**Capability:** Separate-provider authenticity enforcement  
**Primary objective:** Determine whether provider position or representation can substitute for cryptographic provider authority.

## Architecture

The tested authority relationship was:

    Legitimate Provider
    trusted Ed25519 private key
            |
            | signed authority
            v
    NUVL Verification Boundary
    legitimate provider public key
            |
            v
    VERIFIED


    Unauthorized Substitute
    unrelated Ed25519 private key
            |
            | structurally valid signed artifact
            v
    SAME NUVL Verification Boundary
    SAME legitimate provider public key
            |
            v
    REJECTED

The boundary trust anchor was not changed during provider substitution.

## Security Property Evaluated

SP-002 isolates provider position and representation from cryptographic provider authority.

The unauthorized substitute reproduced relevant characteristics of the legitimate provider interface, including:

- expected network and service position;
- provider identifier;
- expected context;
- artifact structure;
- Ed25519 algorithm designation;
- bounded-use fields.

The substitute did not possess the private signing key corresponding to the public verification key trusted by the NUVL boundary.

The governing distinction evaluated by SP-002 is:

    provider position != provider authority

    provider representation != cryptographic authority

## Test Sequence

| Phase | Provider Condition | Expected |
|---|---|---|
| Baseline | Legitimate provider | Verified issuance |
| Substitution | Unauthorized provider using unrelated signing key | DENY |
| Restoration | Legitimate provider restored | Verified issuance |

All three expected conditions were observed.

Detailed runtime decisions and evidence are maintained in `RESULTS.md`.

## Distinction from POC-002A

POC-002A and SP-002 exercise different trust conditions.

POC-002A retained the legitimate provider and deliberately replaced the public verification key configured at the boundary.

SP-002 does the inverse:

    POC-002A
    legitimate provider
            +
    incorrect boundary trust anchor


    SP-002
    unauthorized provider
            +
    unchanged legitimate boundary trust anchor

SP-002 therefore evaluates unauthorized provider substitution rather than trust-anchor substitution.

## Evidence Package

This directory contains:

    sp002-provider-substitution/
    ├── README.md
    ├── RESULTS.md
    ├── PROVENANCE.md
    ├── SHA256SUMS.txt
    ├── evidence/
    │   └── sp002_rerun_evidence.log
    ├── provider/
    │   ├── poc003_ed25519_provider_1h.py
    │   ├── sp002_unauthorized_provider.py
    │   └── sp002_unauthorized_private.pem
    ├── boundary/
    │   └── sp001_separate_provider_boundary.py
    └── trust/
        └── poc002_ed25519_public.pem

`RESULTS.md` records the executed conditions and observed outcomes.

`PROVENANCE.md` records artifact lineage, test-host relationships, cryptographic material, and evidence provenance.

`evidence/sp002_rerun_evidence.log` contains the retained runtime record for the baseline, substitution, and restoration sequence.

`SHA256SUMS.txt` is the authoritative integrity manifest for the current published package.

The legitimate provider requires poc002_ed25519_private.pem, which is published in ../sp001-baseline/provider/. It is not duplicated here.

## Supported Claim

SP-002 supports the bounded claim that, within the tested configuration, an unauthorized provider occupying the expected provider position and reproducing the expected provider-facing artifact representation did not obtain accepted provider authority when it lacked the Ed25519 private key corresponding to the boundary's configured trust anchor.

Restoration of the legitimate provider restored verified issuance without changing the boundary trust anchor.

## Claim Boundary

SP-002 does not establish:

- protection of the boundary trust anchor against privileged modification;
- security after arbitrary privileged compromise of the NUVL boundary;
- endpoint-local Ed25519 verification;
- resistance to denial-of-service at the provider network position;
- rejection of every possible malicious intermediary behavior;
- rejection of every possible replay of previously legitimate authority.

Those properties require separate evidence.
