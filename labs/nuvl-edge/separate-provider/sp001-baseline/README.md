# NUVL Separate-Provider Validation

This directory contains validation of NUVL with provider authority hosted on infrastructure physically separate from the NUVL verification/enforcement boundary.

The objective is to test whether provider-controlled bounded authority remains intact when the provider and its private signing key execute on a separate host.

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

The NUVL boundary may authenticate, evaluate, and enforce that authority, but does not acquire the provider private signing key merely because the provider is remote.


## Authority Model

Physical separation of the provider does not change the underlying NUVL authority model.

The provider may originate authority within its configured scope.

The NUVL boundary may:

- receive provider authority;
- verify provider signatures;
- evaluate request and artifact bindings;
- enforce existing limits;
- reject inadmissible authority;
- enforce replay and use restrictions.

The boundary does not gain authority to originate or enlarge provider authority simply because the provider is located on another system.

## Test Key Material

Laboratory Ed25519 key material may be included in individual test packages for reproducibility.

Any published key material in this directory is test-only material with no production, operational, account, identity, or external trust relationship.

Published test private keys are intentionally non-secret and exist solely to reproduce the laboratory authority relationship.

## Evidence

Individual test directories contain their own:

- test description;
- results;
- provenance;
- source files;
- test key material where applicable;
- captured evidence where available;
- SHA-256 manifests.

Evidence generated during later validation should be identified separately from evidence produced during an original interactive run.

Current validation:

- `sp001-baseline/` — physically separate Ed25519 provider baseline, including provider-unavailable fail-closed behavior and restoration.

## Scope

The separate-provider work evaluates provider placement, trust separation, and the preservation of bounded provider authority across that separation.

A completed test supports only the properties actually exercised by that test.

This directory does not, by itself, establish:

- resistance to arbitrary compromise of the NUVL boundary;
- endpoint-side Ed25519 verification;
- resistance to all malicious intermediaries;
- production infrastructure security;
- production key-management security;
- provider high availability.

Additional conditions may be tested independently without requiring a predetermined numbered test schedule.

## Relationship to Existing NUVL Evidence

Separate-provider validation builds on the existing NUVL provider-authenticity and bounded-authority evidence.

The principal architectural variable introduced by SP-001 is physical separation of the provider authority source from the verification/enforcement boundary.

The bounded-authority invariant remains unchanged.
