# SP-002 — Provenance

## Purpose

This document records artifact identity, cryptographic relationships, test-host configuration, and runtime-evidence provenance for the SP-002 unauthorized-provider-substitution test.

SP-002 replaced the legitimate provider with an unauthorized substitute while preserving the Raspberry Pi verification boundary and its configured legitimate Ed25519 public trust anchor.

Behavioral test conditions and observed outcomes are documented separately in `RESULTS.md`.

## Test Architecture

SP-002 used:

- a separate Linux provider host;
- a Raspberry Pi NUVL verification boundary;
- an Ed25519 public trust anchor retained by the boundary.

The provider service position was:

    192.168.0.240:8091

The Raspberry Pi boundary was configured to contact:

    http://192.168.0.240:8091

During the substitution condition, the process occupying that provider position changed.

The boundary implementation and configured legitimate trust anchor remained unchanged.

## Provider Host

Provider services executed on:

- Hostname: `Xer0trust2`
- Address: `192.168.0.240`
- Port: `8091`
- Python: `3.12.3`

The legitimate and unauthorized providers occupied the same host and service position sequentially.

Only one provider process occupied port `8091` during each test phase.

This arrangement allowed provider implementation and signing authority to change while preserving the network destination used by the verification boundary.

## Artifact Identity

The principal SP-002 artifacts were identified as follows:

| Artifact | Role | Original/Test SHA-256 |
|---|---|---|
| `sp001_separate_provider_boundary.py` | Verification boundary | `f35855d54933ee1f188576d9a8dc0eb9c30f8e7a5de821772f929df9cb801637` |
| `poc002_ed25519_public.pem` | Legitimate boundary trust anchor | `2fd9c44a0579b985bc44722313725c8a6fd532b665b617b3e5082efb14c49f63` |
| `poc003_ed25519_provider_1h.py` | Legitimate provider implementation | `e7206aeb42a4b2f903cdf01d21604e2d19a7d0a2a79962e55982524de69c4d62` |
| `sp002_unauthorized_provider.py` | Unauthorized substitute provider | `ad049085e8470b3fc17eb9089d3ade85db03bb05b21764f6d304a0c07d2f1703` |
| `sp002_unauthorized_private.pem` | Unauthorized test signing key | `dfb7da42fa074f8f68916f52780e310c3797e4da2caa674c5b0427324f0ad57d` |
| `sp002_rerun_evidence.log` | Retained three-phase runtime evidence | `3420bcd631a0ffeae8d6086467df7c223d9d25c5fd3746b79dfad3ddb07bd148` |

These values identify the artifacts used or captured during the SP-002 test activity.

They are historical test/provenance values and are distinct from current repository-integrity values maintained in `SHA256SUMS.txt`.

## Verification Boundary

SP-002 reused:

    sp001_separate_provider_boundary.py

The boundary was configured for the separate provider at:

    http://192.168.0.240:8091

No SP-002 modification to the boundary verification logic was required.

The same boundary implementation remained in service across:

1. legitimate-provider baseline;
2. unauthorized-provider substitution;
3. legitimate-provider restoration.

## Legitimate Trust Anchor

The Raspberry Pi boundary used:

    poc002_ed25519_public.pem

This public key represented the legitimate provider trust relationship.

The trust anchor was not replaced during the provider-substitution condition.

The unauthorized provider key was not added to the boundary trust configuration.

SP-002 therefore changed the provider-side signing authority while preserving the verifier-side trust relationship.

## Legitimate Provider

The legitimate provider implementation was:

    poc003_ed25519_provider_1h.py

It used the private Ed25519 signing key corresponding to the public verification key configured at the Raspberry Pi boundary.

Relevant provider-facing characteristics included:

    service port: 8091
    provider_id: laptop-ed25519-provider-01
    context: field_led_demo
    algorithm: Ed25519
    max_uses: 1
    offline_allowed: true

The same legitimate provider implementation was used for the baseline and restoration phases.

## Unauthorized Substitute Provider

The substitution condition used:

    sp002_unauthorized_provider.py

The substitute reproduced relevant provider-facing characteristics of the legitimate provider, including:

    service port: 8091
    provider_id: laptop-ed25519-provider-01
    context: field_led_demo
    algorithm: Ed25519
    max_uses: 1
    offline_allowed: true

The substitute signed with:

    sp002_unauthorized_private.pem

This private key was created as disposable laboratory test material for the provider-substitution condition.

It does not correspond to the legitimate public trust anchor configured at the Raspberry Pi boundary.

The provider position and representation could therefore remain substantially constant while the underlying signing authority changed.

## Cryptographic Relationship

The SP-002 trust relationships were:

    LEGITIMATE PROVIDER

    legitimate private key
            |
            | Ed25519
            v
    poc002_ed25519_public.pem
    configured at boundary


    UNAUTHORIZED PROVIDER

    sp002_unauthorized_private.pem
            |
            | Ed25519
            v
    unrelated public-key relationship
            |
            X
    poc002_ed25519_public.pem
    configured at boundary

The unauthorized private key was intentionally outside the configured provider trust relationship.

## Execution Provenance

SP-002 was executed as a sequential three-phase control:

    legitimate provider
            |
            v
    unauthorized substitute
            |
            v
    legitimate provider restored

The same provider service position was used throughout.

The Raspberry Pi verification boundary and legitimate public trust anchor remained unchanged across the three conditions.

Detailed requests, artifact identifiers, decisions, verification states, and reason strings are documented in `RESULTS.md`.

## Runtime Evidence Provenance

The retained SP-002 runtime record is:

    evidence/sp002_rerun_evidence.log

Test-time SHA-256:

    3420bcd631a0ffeae8d6086467df7c223d9d25c5fd3746b79dfad3ddb07bd148

The transcript captures the sequential legitimate-provider, unauthorized-substitution, and legitimate-restoration conditions.

The recording was closed after completion of the three-phase sequence and subsequently hashed.

This file is the retained runtime evidence for the SP-002 test execution documented in `RESULTS.md`.

## Superseded Evidence Record

An earlier recording named:

    sp002_substitution_evidence.log

was generated during prior SP-002 activity.

That recording remained active during subsequent evidence-recovery work. Commands used to inspect the recording were consequently captured into the same file, introducing unrelated material and recursive reproductions of portions of the recording.

That file is not used as the canonical publication evidence for SP-002.

It was superseded by:

    sp002_rerun_evidence.log

The superseded recording is not used to reconstruct or supplement the retained rerun transcript.

## Relationship to Prior Trust-Anchor Testing

SP-002 is distinct from the earlier trust-anchor substitution condition.

The earlier condition preserved the legitimate provider while replacing the verification key configured at the boundary.

SP-002 preserved the legitimate boundary trust anchor while replacing the provider and its signing key.

The relationship is:

    PRIOR TRUST-ANCHOR TEST

    legitimate provider
            +
    incorrect boundary trust anchor


    SP-002

    unauthorized provider
            +
    unchanged legitimate boundary trust anchor

The two tests therefore exercise opposite sides of the provider/verifier trust relationship.

## Evidence Classification

**Test artifact**  
Source, configuration, or cryptographic material used during the SP-002 execution and identified by its test-time artifact identity.

**Trust anchor**  
Public verification material retained by the NUVL boundary to establish the legitimate provider signing relationship.

**Unauthorized test key**  
Disposable laboratory signing material deliberately excluded from the legitimate provider trust relationship.

**Captured runtime evidence**  
The retained terminal transcript recording the controlled three-phase SP-002 execution.

**Superseded evidence**  
An earlier recording excluded from the canonical evidence package because its capture boundary was not cleanly terminated.

**Publication integrity record**  
Current repository artifact integrity maintained in `SHA256SUMS.txt`.

These classifications are intentionally separate.

Current publication bytes may differ from historical test-time artifacts if repository preparation modifies a file. Any modified copy must retain separate publication identity rather than being represented as byte-identical to the tested artifact.

## Publication Lineage

The SP-002 publication package may contain:

    provider/poc003_ed25519_provider_1h.py
    provider/sp002_unauthorized_provider.py
    provider/sp002_unauthorized_private.pem
    boundary/sp001_separate_provider_boundary.py
    trust/poc002_ed25519_public.pem
    evidence/sp002_rerun_evidence.log

Documentation files are maintained separately within the same package.

`SHA256SUMS.txt` is the authoritative integrity manifest for the current published bytes.

Historical test-time hashes retained in this provenance record establish test-artifact lineage and must not be substituted for current publication hashes when the underlying bytes differ.

## Provenance Assessment

The retained SP-002 evidence establishes:

- identity of the verification boundary used during SP-002;
- identity of the legitimate public trust anchor;
- identity of the legitimate provider implementation;
- identity of the unauthorized substitute implementation;
- identity of the unauthorized signing key;
- separation between the legitimate and unauthorized signing relationships;
- preservation of the boundary and legitimate trust anchor across the substitution sequence;
- use of the same provider service position by the legitimate and unauthorized providers;
- identity of the retained three-phase runtime transcript;
- exclusion of the earlier contaminated recording from the canonical evidence package.

SHA-256 values establish artifact identity and, where independently compared, byte correspondence.

They do not independently prove the behavioral outcome of the provider-substitution test.

Observed decisions and the resulting security claim are documented in `RESULTS.md`.
