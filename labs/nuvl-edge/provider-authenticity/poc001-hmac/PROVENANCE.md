# POC-001 Artifact Provenance

## Purpose

This document records the provenance of surviving artifacts associated with the July 11, 2026 POC-001 HMAC bounded-disconnected-authority test.

The provenance record establishes:

- identity of surviving original test source;
- cross-host correspondence of retained source artifacts;
- publication status of surviving artifacts;
- relationship between retained source and the contemporaneous test record;
- known evidence limitations.

The original interactive terminal transcript is not included in this package. No reconstructed output is represented as original runtime evidence.

## Original Test Environment

The tested path was:

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

POC-001 used HMAC-SHA256 authentication for bounded provider-issued artifacts.

Trust placement was:

    Windows provider
        shared HMAC secret
        artifact issuance
        normal provider validation

    Raspberry Pi
        shared HMAC secret
        bounded-artifact validation
        in-memory used-nonce state

    ESP32-S3
        request endpoint

Because HMAC uses shared secret material, both the provider and boundary possessed cryptographic material capable of generating valid artifact authentication values.

This limitation is intrinsic to the tested POC-001 architecture.

## Surviving Original Source

Two original POC-001 source files were recovered from the Windows test host:

    ddil_provider.py
    ddil_boundary.py

Observed filesystem timestamps were:

    2026-07-11 19:54:47  ddil_provider.py
    2026-07-11 19:56:10  ddil_boundary.py

These timestamps are retained as supporting filesystem metadata and are not treated as cryptographic evidence.

The retained source was identified as follows:

| Artifact | SHA-256 |
|---|---|
| `ddil_provider.py` | `97aad386e48813488047503030de277d165a4a9040d758d7679d330a7ba0ebeb` |
| `ddil_boundary.py` | `7bd3b443caf4c5b8d88b70db9cbb8b4ec28df6fcdbbe301ba7cb402cfbb2905d` |

These values identify the surviving original POC-001 source and are retained as historical provenance values. They are distinct from the publication-integrity manifest maintained in `SHA256SUMS.txt`.

## Cross-Host Source Correspondence

The Raspberry Pi test host independently retained a boundary implementation at:

    /home/seth/nuvl_ddil_poc/ddil_boundary.py

SHA-256 comparison of the independently retained Raspberry Pi and Windows boundary copies produced the same digest:

    7bd3b443caf4c5b8d88b70db9cbb8b4ec28df6fcdbbe301ba7cb402cfbb2905d

**Result: MATCH**

The matching digest establishes byte identity between the surviving Windows and Raspberry Pi copies of the POC-001 boundary source.

It does not independently establish execution time or behavioral test results.

## Source Characteristics

### Provider

The retained provider implementation includes:

- HMAC-SHA256 artifact authentication;
- bounded-artifact issuance;
- action and context restrictions;
- nonce generation;
- issuance and expiration times;
- single-use artifact declaration;
- request binding;
- normal provider validation.

The source contains the laboratory fallback value:

    dev_ddil_lab_secret_change_me

This value is defined as the default used when the `DDIL_SECRET` environment variable is absent.

It is retained because the provider file represents surviving original laboratory source rather than a sanitized derivative. It is not an operational credential.

### Boundary

The retained boundary implementation includes:

- provider-first validation;
- provider-unavailable bounded-artifact validation;
- HMAC verification;
- action binding;
- context binding;
- request-representation binding;
- expiration enforcement;
- single-use enforcement;
- nonce validation;
- in-memory replay tracking;
- fail-closed denial when valid bounded authority is absent.

The boundary implementation is not distributed in the public POC-001 package.

## Publication Status

The public package includes:

    ddil_provider.py

The Raspberry Pi boundary implementation:

    ddil_boundary.py

is intentionally excluded from this publication package.

The original boundary remains represented in this provenance record because independently retained Windows and Raspberry Pi copies were established as byte-identical.

Current integrity values for files distributed through the repository are maintained exclusively in:

    SHA256SUMS.txt

Publication-integrity values are not duplicated in this document.

## HMAC Trust Placement

Both retained implementations use the same `DDIL_SECRET` configuration mechanism.

The provider uses the shared secret to generate artifact authentication values. The boundary uses the shared secret to validate them.

The resulting relationship is:

    provider
        |
        | shared HMAC secret
        |
        +-----------------------+
                                |
                                v
                         NUVL boundary

Possession of the verification material therefore also provides the cryptographic material required to generate valid HMAC authentication values.

POC-001 does not support a claim of exclusive provider cryptographic issuance authority.

POC-002 addresses this limitation by replacing the shared-secret relationship with an Ed25519 private-signing-key/public-verification-key separation.

## Runtime Evidence Status

The original interactive POC-001 terminal transcript was not retained.

Behavioral results documented in `RESULTS.md` derive from the contemporaneous NUVL hardware laboratory record and are not represented as reconstructed raw terminal output.

The surviving implementation is consistent with the recorded test conditions, including:

- provider-first validation;
- bounded disconnected acceptance;
- replay denial;
- missing-artifact denial;
- action and context binding;
- expiration enforcement;
- fail-closed behavior during provider unavailability.

Source consistency does not independently establish execution of those conditions.

Behavioral claims therefore remain grounded in the contemporaneous laboratory record rather than inferred solely from source inspection.

## Evidence Classification

The POC-001 evidence package distinguishes four evidence classes:

**Original tested source**  
Source retained from the July 11 test activity and identified by historical SHA-256 values.

**Independently retained source**  
Source retained on multiple test systems for which byte identity was established through SHA-256 comparison.

**Contemporaneous result record**  
Behavioral observations recorded during or immediately following the original test activity and documented in `RESULTS.md`.

**Publication integrity record**  
Current repository artifact integrity maintained in `SHA256SUMS.txt`.

These evidence classes are intentionally separate. A publication hash change does not alter the identity of an original tested artifact recorded in this provenance document.

## Provenance Assessment

The surviving evidence establishes:

- retention of the original provider source;
- retention of the original boundary source;
- byte identity between independently retained Windows and Raspberry Pi boundary copies;
- consistency between retained implementation and the contemporaneous laboratory record;
- explicit identification of the shared-secret trust limitation.

The evidence does not independently establish execution chronology from cryptographic data alone.

The absence of the original interactive terminal transcript remains an explicit limitation.

Any later reproduction of POC-001 constitutes a separate execution and requires its own date, runtime evidence, artifact identity, and reproduction designation. It does not replace the July 11, 2026 test record.
