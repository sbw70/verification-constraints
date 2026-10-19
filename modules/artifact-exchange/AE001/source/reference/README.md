# AE001 Architectural Reference Source

This directory preserves the architectural reference implementation associated with the artifact-exchange module.

## Contents

```text
reference/
└── AEBS.py
```

## Role of `AEBS.py`

`AEBS.py` is the architectural reference for the Provider-Controlled Artifact Exchange and Boundary Signaling model.

It illustrates the core separation between:

- requester;
- intermediary conveyance;
- provider-side evaluation;
- provider-side execution initiation; and
- provider-generated execution-boundary signaling.

The reference is intentionally compact.

It is not the complete implementation used for the AE001 scored campaign.

## Relationship to AE001

AE001 tested a stronger, provider-specific composition using the existing MP003 implementation.

The scored campaign required features that the compact architectural reference does not itself provide, including:

- distinct Provider A and Provider B authority domains;
- request-bound provider-specific authorization artifacts;
- Ed25519 authorization signatures;
- provider-specific wrong-provider rejection;
- authenticated provider `START`, `COMPLETE`, and `DENY` packages;
- provider-local spent-authority state;
- provider-local software execution records; and
- independent verification of raw provider boundary signatures.

Those mechanisms were supplied by the copied MP003 source under:

`../MP003/`

AE001 therefore uses `AEBS.py` as an architectural reference, not as the sole scored implementation.

## What the Reference Demonstrates

The reference captures the intended authority boundary:

- the requester presents an operation request and associated verification artifact;
- the intermediary conveys them;
- the intermediary does not become the authorization authority;
- the provider evaluates the verification artifact;
- the provider decides whether to initiate execution; and
- execution-boundary representation remains provider-controlled.

That architectural relationship is the basis of the AE001 campaign.

## Important Distinction

The reference uses a simplified demonstration model.

It must not be read as evidence that every control used in AE001 is implemented by `AEBS.py` itself.

In particular, the scored campaign's provider-specific authorization and signed boundary packages come from the MP003 implementation.

The AE001 result is established by the tested source, locked campaign definition, provider state, raw signed evidence, and scored records—not by the architectural reference alone.

## Source Identity

The preserved `AEBS.py` source is identified in:

`../../configs/AE001_SOURCE_MANIFEST.json`

The manifest records its SHA-256 identity as:

```text
70277ef4a6b9df6c8767a12be01cfcce13e257fdbbbaae184da367172b974fb8
```

The campaign provenance also identifies the repository revision from which the architectural reference was inspected.

See:

`../../PROVENANCE.md`

## Scope

`AEBS.py` is a reference implementation for the architectural model.

It is not independently claimed to establish:

- multi-provider separation;
- authenticated provider boundary packages;
- durable spent-authority state;
- wrong-provider rejection;
- negative-case state preservation;
- physical execution;
- compromised-host resistance; or
- the complete AE001 scored result.

Those claims, where tested, depend on the actual AE001 campaign implementation and evidence.
