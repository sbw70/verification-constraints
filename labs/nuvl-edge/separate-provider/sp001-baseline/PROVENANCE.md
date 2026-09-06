# SP-001 — Provenance

## Purpose

This document records artifact lineage, cross-host file identity, source derivation, and retained-evidence provenance for the September 2, 2026 SP-001 separate-provider test.

SP-001 placed the provider and its Ed25519 private signing key on a physical host separate from the Raspberry Pi NUVL verification/enforcement boundary.

This record distinguishes among:

- selected working artifacts;
- artifacts transferred to the separate provider host;
- SP-001-specific source derivation;
- cryptographic test material;
- retained runtime evidence;
- publication artifacts.

Behavioral test outcomes are documented separately in `RESULTS.md`.

## Test Date

SP-001 was executed on:

    2026-09-02

## Test Systems

### Windows Working System

Working directory:

    C:\Users\holiw\esp32-main

This system contained the selected provider implementation and laboratory Ed25519 key material used to prepare the separate provider host.

### Separate Provider Host

- Hostname: `Xer0trust2`
- Operating system: Linux Mint
- Working directory: `/home/seth/nuvl-provider`
- Test network address: `192.168.0.240`

The provider service and Ed25519 private signing key were hosted on this system during SP-001.

### NUVL Boundary Host

- Platform: Raspberry Pi 5
- Hostname: `xer0trust-pi`
- Test network address: `192.168.0.94`

The NUVL verification/enforcement boundary executed on this system.

## Artifact Identity

The principal SP-001 artifacts were identified as follows:

| Artifact | Role | Original/Test SHA-256 |
|---|---|---|
| `poc003_ed25519_provider_1h.py` | Provider implementation | `e7206aeb42a4b2f903cdf01d21604e2d19a7d0a2a79962e55982524de69c4d62` |
| `poc002_ed25519_private.pem` | Provider private test key | `cfdd77949cea7df748af6f0c45e9b2b2755a825ce178bc6e51d7fd4671bbc999` |
| `poc002_ed25519_public.pem` | Boundary verification key | `2fd9c44a0579b985bc44722313725c8a6fd532b665b617b3e5082efb14c49f63` |
| `poc004_pi_boundary_persistent_archer.py` | Parent boundary source | `a1ca45bdae628b318d208120c51c25ba8281fdd22fecd6d5e87a993e51a61e26` |
| `sp001_separate_provider_boundary.py` | SP-001 boundary derivative | `f35855d54933ee1f188576d9a8dc0eb9c30f8e7a5de821772f929df9cb801637` |
| `sp001_control_evidence.log` | Captured availability-control evidence | `13ea30307548cc0d4e80e19ce27dbc3b187d1b6bfa29f38572b05b459965b119` |

These values identify the artifacts used or captured during the SP-001 test activity.

They are historical test/provenance values and are distinct from current repository-integrity values maintained in `SHA256SUMS.txt`.

## Cross-Host Correspondence

### Provider Source

The selected Windows working copy of:

    poc003_ed25519_provider_1h.py

and the copy executed on `Xer0trust2` at:

    /home/seth/nuvl-provider/poc003_ed25519_provider_1h.py

both produced:

    e7206aeb42a4b2f903cdf01d21604e2d19a7d0a2a79962e55982524de69c4d62

**Result: MATCH**

This establishes byte identity between the selected Windows provider source and the provider source transferred to the separate provider host.

### Provider Private Test Key

The Windows working copy and `Xer0trust2` copy of:

    poc002_ed25519_private.pem

both produced:

    cfdd77949cea7df748af6f0c45e9b2b2755a825ce178bc6e51d7fd4671bbc999

**Result: MATCH**

This establishes byte identity between the selected laboratory private key and the key transferred to the separate provider host.

## Boundary Derivation

SP-001 used a derivative of the previously tested persistent-replay boundary:

    poc004_pi_boundary_persistent_archer.py

The SP-001 derivative was:

    sp001_separate_provider_boundary.py

The provider network location was changed from:

    PROVIDER_BASE = "http://192.168.0.50:8091"

to:

    PROVIDER_BASE = "http://192.168.0.240:8091"

A source diff performed during SP-001 preparation identified this provider-location change as the only source modification between the selected parent boundary and the SP-001 derivative.

The parent and derivative therefore maintain separate artifact identities, recorded in the artifact table above.

## Cryptographic Material

SP-001 used an Ed25519 laboratory keypair.

The private signing key was transferred to and used by the separate provider host.

The corresponding public verification key was used by the Raspberry Pi boundary.

Boundary startup reported:

    Private key present on Pi: False

The keypair is laboratory test material with no production, operational, account, identity, or external trust relationship.

Publication or withholding of this test material is a repository-packaging decision and does not alter its role in the SP-001 test record.

## Runtime Evidence Provenance

SP-001 contains two distinct runtime-evidence classes.

### Initial Interactive Baseline

The initial separate-provider baseline was observed during the active SP-001 test session.

Recorded observations included provider startup, remote provider communication, boundary startup, provider-authenticated issuance, and bounded spend.

A complete raw terminal transcript of the initial interactive baseline was not retained.

The observations from that execution are documented in `RESULTS.md` and are not represented as reconstructed raw terminal output.

### Captured Availability Control

A subsequent online → unavailable → restored provider-availability control was captured directly to:

    evidence/sp001_control_evidence.log

Test-time SHA-256:

    13ea30307548cc0d4e80e19ce27dbc3b187d1b6bfa29f38572b05b459965b119

The retained transcript records the separate-provider availability-control sequence after the initial interactive baseline.

It is identified as a separate evidence-capture run and is not represented as the original SP-001 terminal transcript.

Detailed behavioral interpretation of this transcript is maintained in `RESULTS.md`.

## Evidence Classification

**Selected working artifact**  
An artifact selected from the existing NUVL test environment for use in SP-001.

**Cross-host verified artifact**  
An artifact retained on multiple SP-001 systems for which byte identity was established through SHA-256 comparison.

**Source derivative**  
A test-specific source file derived from an earlier implementation through an identified source modification.

**Interactive test record**  
Observations recorded during active testing where a complete raw terminal transcript was not retained.

**Captured runtime evidence**  
A retained runtime transcript captured during a subsequent controlled execution.

**Publication integrity record**  
Current repository artifact integrity maintained in `SHA256SUMS.txt`.

These classifications are intentionally separate.

Current publication bytes need not have the same digest as a historical test artifact if a file is subsequently modified for publication. Any modified publication copy must be treated as a derivative rather than represented as the original tested artifact.

## Publication Lineage

The SP-001 publication package may contain the following test artifacts:

    provider/poc003_ed25519_provider_1h.py
    provider/poc002_ed25519_private.pem
    trust/poc002_ed25519_public.pem
    boundary/sp001_separate_provider_boundary.py
    evidence/sp001_control_evidence.log

Documentation files are maintained separately within the same package.

`SHA256SUMS.txt` is the authoritative integrity manifest for the current published bytes.

Historical test-time hashes retained in this provenance record establish artifact lineage and must not be substituted for current publication hashes when the underlying file bytes differ.

## Provenance Assessment

The retained SP-001 evidence establishes:

- identity of the provider implementation selected for SP-001;
- byte identity between the selected Windows provider source and the copy transferred to `Xer0trust2`;
- byte identity between the selected laboratory private key and the copy transferred to `Xer0trust2`;
- identity of the public verification key associated with the test configuration;
- lineage of the SP-001 boundary from the previously tested persistent-replay boundary;
- the source modification used to create the SP-001 derivative;
- identity of the retained availability-control transcript;
- separation between the initial interactive baseline and the later captured evidence run.

SHA-256 correspondence establishes byte identity between retained artifacts.

It does not independently establish execution chronology or prove behavioral test outcomes.

Those outcomes are documented in `RESULTS.md`.
