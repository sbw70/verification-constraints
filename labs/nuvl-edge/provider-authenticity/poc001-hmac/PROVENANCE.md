# POC-001 Artifact Provenance

## Purpose

This document records the provenance of surviving artifacts associated with the July 11, 2026 POC-001 HMAC bounded-disconnected-authority test.

The provenance record distinguishes among:

1. original tested source retained from the July execution;
2. artifacts independently retained on the Raspberry Pi and Windows test host;
3. contemporaneously recorded test results;
4. files included in the public repository;
5. files intentionally excluded from publication.

The original interactive terminal transcript is not included in this package.

No reconstructed output is represented as original runtime evidence.

## Original Test Environment

The tested path was:

```text
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
```

POC-001 used HMAC-SHA256 authentication for bounded provider-issued artifacts.

Trust placement was:

```text
Windows provider:
    shared HMAC secret
    artifact issuance
    normal provider validation

Raspberry Pi:
    same shared HMAC secret
    bounded-artifact validation
    in-memory used-nonce state

ESP32-S3:
    request endpoint
```

Because HMAC uses shared secret material, the provider and boundary both possessed cryptographic material capable of calculating valid artifact authentication values.

This trust-placement limitation is part of the original POC-001 architecture and is preserved in the evidence record.

## Surviving Windows Test-Host Artifacts

The following original POC-001 source files were recovered from the Windows test host:

```text
ddil_provider.py
ddil_boundary.py
```

Observed Windows filesystem timestamps were:

```text
2026-07-11 19:54:47  ddil_provider.py
2026-07-11 19:56:10  ddil_boundary.py
```

These timestamps are retained as provenance metadata. They are not treated as cryptographic evidence.

## Original Source SHA-256

The retained Windows test-host files have the following SHA-256 digests:

```text
97aad386e48813488047503030de277d165a4a9040d758d7679d330a7ba0ebeb  ddil_provider.py
7bd3b443caf4c5b8d88b70db9cbb8b4ec28df6fcdbbe301ba7cb402cfbb2905d  ddil_boundary.py
```

These hashes identify the surviving original POC-001 implementation.

## Independently Retained Raspberry Pi Artifact

The original Raspberry Pi test host retained a POC-001 boundary implementation at:

```text
/home/seth/nuvl_ddil_poc/ddil_boundary.py
```

Its SHA-256 digest is:

```text
7bd3b443caf4c5b8d88b70db9cbb8b4ec28df6fcdbbe301ba7cb402cfbb2905d  /home/seth/nuvl_ddil_poc/ddil_boundary.py
```

The independently retained Windows copy has:

```text
7bd3b443caf4c5b8d88b70db9cbb8b4ec28df6fcdbbe301ba7cb402cfbb2905d  ddil_boundary.py
```

**Result: SHA-256 match.**

The surviving Windows and Raspberry Pi copies of the POC-001 boundary implementation are byte-identical.

This cross-host correspondence establishes independent preservation of the same boundary source on the two systems.

## Provider Source

The surviving original provider implementation has SHA-256:

```text
97aad386e48813488047503030de277d165a4a9040d758d7679d330a7ba0ebeb  ddil_provider.py
```

The source implements:

- HMAC-SHA256 artifact authentication;
- bounded-artifact issuance;
- action binding;
- context binding;
- unique nonce generation;
- issuance time;
- expiration time;
- `max_uses=1`;
- request representation;
- normal provider validation.

The retained provider source contains the laboratory default:

```text
dev_ddil_lab_secret_change_me
```

This value is explicitly defined in the source as the fallback value used when the `DDIL_SECRET` environment variable is absent.

It is retained because the public provider file is published as the surviving original source rather than as a sanitized derivative.

No production credential is represented by this value.

## Boundary Source

The surviving boundary implementation has SHA-256:

```text
7bd3b443caf4c5b8d88b70db9cbb8b4ec28df6fcdbbe301ba7cb402cfbb2905d  ddil_boundary.py
```

The implementation contains:

- provider-first validation;
- provider-unavailable bounded-artifact validation;
- HMAC verification;
- action binding;
- context binding;
- request-representation binding;
- expiration enforcement;
- `max_uses=1` enforcement;
- nonce validation;
- in-memory replay tracking;
- fail-closed denial when no valid bounded artifact is available.

The boundary source is intentionally excluded from the public POC-001 package.

Its SHA-256 digest and cross-host correspondence are retained here as provenance for the tested implementation.

## Publication Status

### Published Original Artifact

The public POC-001 package includes:

```text
ddil_provider.py
```

Published SHA-256:

```text
97aad386e48813488047503030de277d165a4a9040d758d7679d330a7ba0ebeb  ddil_provider.py
```

The publication copy is byte-identical to the surviving original Windows test-host source represented by that digest.

No publication sanitation changed this file.

### Unpublished Original Artifact

The public POC-001 package does not include:

```text
ddil_boundary.py
```

The tested boundary implementation is identified by:

```text
7bd3b443caf4c5b8d88b70db9cbb8b4ec28df6fcdbbe301ba7cb402cfbb2905d  ddil_boundary.py
```

The same digest was independently reproduced from the copy retained on the Raspberry Pi.

Exclusion from the public repository is intentional and does not indicate loss of the artifact.

## HMAC Trust-Placement Record

Both surviving implementations reference the same `DDIL_SECRET` configuration mechanism.

The provider uses the secret to generate artifact authentication values.

The boundary uses the secret to validate artifact authentication values.

The resulting cryptographic relationship is:

```text
provider
    |
    | shared HMAC secret
    |
    +-----------------------+
                            |
                            v
                     NUVL boundary
```

This arrangement means that possession of the verification material also provides the material necessary to calculate valid HMAC authentication values.

POC-001 therefore cannot support a claim that cryptographic artifact origination was exclusively retained by the provider.

This limitation is intrinsic to the tested HMAC design rather than a publication artifact or evidence-recovery limitation.

POC-002 subsequently replaced this shared-secret relationship with an Ed25519 private-key/public-key split.

## Runtime Evidence Status

No original interactive POC-001 terminal transcript is included in the recovered artifact set.

The behavioral results recorded in `RESULTS.md` derive from the contemporaneous NUVL hardware laboratory record.

They are not represented as reconstructed raw terminal output.

The surviving source is consistent with the recorded POC-001 conditions, including:

- provider-first validation;
- valid bounded disconnected acceptance;
- replay denial;
- missing-artifact denial;
- wrong-context denial;
- wrong-action denial;
- expiration denial;
- fail-closed provider-unavailable behavior.

Source consistency does not independently prove that each path executed during the original test.

The behavioral execution record remains the contemporaneous laboratory record.

## Evidence Classification

### Original Tested Source

Source retained from the July 11 execution and identified by its SHA-256 digest.

The surviving POC-001 provider and boundary implementations fall into this category.

### Independently Retained Artifact

An artifact preserved on more than one test system for which byte identity is established through matching SHA-256 digests.

The POC-001 boundary implementation falls into this category.

### Contemporaneous Result Record

Behavioral results recorded during or immediately following the original test activity.

The POC-001 behavioral results documented in `RESULTS.md` fall into this category.

### Publication Manifest

`SHA256SUMS.txt` identifies the exact files distributed in the public POC-001 directory.

The publication manifest is distinct from the original tested-source hashes preserved in this provenance record.

## Provenance Summary

| Artifact | Status | SHA-256 |
|---|---|---|
| `ddil_provider.py` | Original tested source; public | `97aad386e48813488047503030de277d165a4a9040d758d7679d330a7ba0ebeb` |
| `ddil_boundary.py` | Original tested source; unpublished | `7bd3b443caf4c5b8d88b70db9cbb8b4ec28df6fcdbbe301ba7cb402cfbb2905d` |
| Pi `ddil_boundary.py` | Independently retained original | `7bd3b443caf4c5b8d88b70db9cbb8b4ec28df6fcdbbe301ba7cb402cfbb2905d` |

The boundary cross-host hash match establishes byte identity between the independently retained Windows and Raspberry Pi copies.

## Provenance Limitations

Matching SHA-256 digests establish byte identity between retained artifacts.

They do not independently establish when an artifact executed or prove a behavioral test result.

The POC-001 evidence record therefore consists of the combined support provided by:

- surviving original provider source;
- surviving original boundary source;
- independent cross-host preservation of the boundary source;
- contemporaneous laboratory results;
- consistency between the recorded test conditions and surviving implementation.

The absence of an original interactive terminal transcript remains an explicit evidence limitation.

Any later reproduction of POC-001 constitutes a separate execution and requires its own date, runtime evidence, artifact hashes, and reproduction designation. It does not replace or become the original July 11, 2026 test record.
