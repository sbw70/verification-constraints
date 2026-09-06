# POC-002 / POC-002A Artifact Provenance

## Purpose

This document records the provenance of surviving artifacts associated with the July 19–20, 2026 POC-002 and POC-002A Ed25519 provider-authenticity tests.

The provenance record distinguishes among:

- original tested source retained from the July execution;
- artifacts independently retained on multiple test systems;
- post-test publication derivatives;
- contemporaneous behavioral records;
- artifacts intentionally excluded from publication.

The original interactive terminal transcript was not retained.

No reconstructed output is represented as original runtime evidence.

A publication derivative is not represented as byte-identical to an original tested artifact when its contents and SHA-256 digest differ.

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
    NUVL verification boundary
        |
        v
    Windows provider

Trust placement was:

    Windows provider
        Ed25519 private signing key

    Raspberry Pi
        provider public verification key

    ESP32-S3
        no provider private signing key

Provider-signature verification occurred at the Raspberry Pi boundary.

## Surviving Raspberry Pi Artifacts

The original Raspberry Pi test host retained:

    /home/seth/poc002_ed25519_pi_boundary.py
    /home/seth/poc002_ed25519_public.pem
    /home/seth/poc002_ed25519_public_correct.pem
    /home/seth/poc002_ed25519_public_wrong.pem

Observed filesystem timestamps were:

    2026-07-19 20:59:01  /home/seth/poc002_ed25519_pi_boundary.py
    2026-07-20 13:59:44  /home/seth/poc002_ed25519_public_wrong.pem
    2026-07-20 14:04:14  /home/seth/poc002_ed25519_public_correct.pem
    2026-07-20 14:12:13  /home/seth/poc002_ed25519_public.pem

These timestamps are retained as supporting filesystem metadata and are not treated as cryptographic evidence.

## Original Tested Artifact Identity

The retained Windows test-host artifacts were identified as follows:

| Artifact | SHA-256 |
|---|---|
| `poc002_ed25519_pi_boundary.py` | `956e83b03b71c693641a8eee30e9dc8e2db6b8a71de008d052447ce5a06fafc9` |
| `poc002_ed25519_provider.py` | `8d0430ff07fc938090d43e112b7276b481612491044d7d1f3f68bcb1ef1cd3ee` |
| `poc002_ed25519_public.pem` | `2fd9c44a0579b985bc44722313725c8a6fd532b665b617b3e5082efb14c49f63` |
| `poc002_esp32_matrix_repeat.py` | `463d9fdf193ed7b37a99c8edf1d7bdc5ceb282622e9990b383196cbd9e44a337` |
| `poc002_esp32_test.py` | `53c1cd04f9f2a51d83f88dc2231663738f51727d23401f17f40c538b974f6c7e` |
| `poc002a_esp32_probe.py` | `7d1c97e44c66a0bed6c3d53dde25d22fb7532fb9237b67511e715509760cb242` |
| `poc002_wrong_trust_anchor_public.pem` | `95eb0d5089b5ceda23e3cadc7cfb3c0f4af3fb787712716cfab46671216311b9` |

These values identify retained original test artifacts.

They are historical provenance values and are distinct from current repository-integrity values maintained in `SHA256SUMS.txt`.

## Cross-Host Correspondence

### Boundary Source

The Raspberry Pi retained:

    /home/seth/poc002_ed25519_pi_boundary.py

Its SHA-256 matched the independently retained Windows copy:

    956e83b03b71c693641a8eee30e9dc8e2db6b8a71de008d052447ce5a06fafc9

**Result: MATCH**

This establishes byte identity between the surviving Windows and Raspberry Pi copies of the original POC-002 boundary source.

The boundary implementation is not included in the public POC-002 package.

### Correct Provider Trust Anchor

Three independently retained copies of the correct provider public key were identified:

    /home/seth/poc002_ed25519_public.pem
    /home/seth/poc002_ed25519_public_correct.pem
    Windows: poc002_ed25519_public.pem

All three produced:

    2fd9c44a0579b985bc44722313725c8a6fd532b665b617b3e5082efb14c49f63

**Result: MATCH**

This establishes byte identity among the retained copies of the provider public verification key used by the tested trust relationship.

### Deliberately Incorrect Trust Anchor

The Raspberry Pi retained the unrelated public key used for the trust-anchor substitution condition.

The Pi copy and retained publication-source copy produced:

    95eb0d5089b5ceda23e3cadc7cfb3c0f4af3fb787712716cfab46671216311b9

**Result: MATCH**

This artifact is cryptographically distinct from the correct provider public key and represents the intentionally incorrect trust anchor used during POC-002A.

## Publication Derivatives

Environment-specific public network addressing was removed or replaced in publication copies where required.

No test logic was intentionally changed as part of that process.

Files modified for publication are treated as derivatives and retain separate artifact identity from the original tested source.

### Provider Derivative

The original provider source was modified for publication sanitation.

Original tested artifact:

    poc002_ed25519_provider.py
    SHA-256: 8d0430ff07fc938090d43e112b7276b481612491044d7d1f3f68bcb1ef1cd3ee

Sanitized derivative prepared for publication:

    SHA-256: 32c5141e240ee812a1fb8073eda0d96e586829a272fb8f1e613b64ead8e04001

The publication derivative is not represented as byte-identical to the July tested provider source.

### Boundary Derivative

A sanitized boundary derivative was also prepared during evidence recovery.

Original tested artifact:

    SHA-256: 956e83b03b71c693641a8eee30e9dc8e2db6b8a71de008d052447ce5a06fafc9

Sanitized recovery derivative:

    SHA-256: b982c8939cfc52b15b54b17d821474ba4beac1c2b829f9b93b8e7edc31461ed0

The boundary implementation is not distributed in this POC-002 publication package.

The derivative digest is retained only to distinguish the recovery copy from the original tested source.

### Unmodified Publication Artifacts

The following retained artifacts required no content modification during publication preparation:

- `poc002_esp32_test.py`
- `poc002_esp32_matrix_repeat.py`
- `poc002a_esp32_probe.py`
- `poc002_ed25519_public.pem`
- `poc002_wrong_trust_anchor_public.pem`

Their original tested identities are recorded in the artifact table above.

Current repository-integrity values are maintained in `SHA256SUMS.txt` and are not duplicated here.

## Private Signing Material

The original test environment contained the provider Ed25519 private signing key.

A separate private key existed for the unrelated keypair used during the trust-anchor substitution condition.

Private signing material is not required to establish the retained public-key correspondence or the observed verification behavior documented in this evidence package.

Publication status of cryptographic test material is a repository-packaging decision and does not alter the original POC-002 test result.

## Runtime Evidence Status

No original interactive POC-002 terminal transcript was located during evidence recovery.

The original Raspberry Pi was examined for POC-002 artifacts and retained runtime output associated with the July 19–20 test period.

Surviving Pi-side artifacts included:

- the original boundary source;
- the active provider public verification key;
- a preserved correct-key copy;
- the deliberately incorrect trust anchor.

No retained POC-002 runtime-output file was identified.

The Raspberry Pi shell history contained later NUVL activity but did not identify a retained POC-002 terminal transcript or redirected runtime-output file.

Behavioral and numerical observations in `RESULTS.md` therefore derive from the contemporaneous laboratory record.

`RESULTS.md` is not represented as reconstructed raw terminal evidence.

## Evidence Classification

**Original tested source**  
Source retained from the July 19–20 test activity and identified by historical artifact identity.

**Independently retained artifact**  
An artifact preserved on more than one test system for which byte identity was established through cryptographic comparison.

**Publication derivative**  
A post-test copy modified for publication. A derivative maintains separate artifact identity and is not represented as the original tested source.

**Contemporaneous result record**  
Behavioral and numerical observations recorded during or immediately following the original test activity.

**Publication integrity record**  
Current repository artifact integrity maintained in `SHA256SUMS.txt`.

These evidence classes are intentionally separate.

A change to repository representation does not alter the historical identity of the original tested artifacts recorded here.

## Provenance Assessment

The surviving evidence establishes:

- identity of retained original POC-002 test source;
- byte identity between independently retained Windows and Raspberry Pi boundary copies;
- byte identity among independently retained copies of the correct provider public verification key;
- identity of the deliberately incorrect trust anchor used during POC-002A;
- explicit separation between original tested source and later publication derivatives;
- consistency between retained implementation and the contemporaneous laboratory record.

SHA-256 correspondence establishes byte identity between retained artifacts.

It does not independently establish execution chronology or prove behavioral test outcomes.

The absence of the original interactive terminal transcript remains an explicit evidence limitation.

Any later reproduction of POC-002 or POC-002A constitutes a separate execution and requires its own date, runtime evidence, artifact identity, and reproduction designation. It does not replace the July 19–20, 2026 test record.
