# POC-002 / POC-002A Artifact Provenance

## Purpose

This document records the provenance of surviving artifacts associated with the July 19–20, 2026 POC-002 and POC-002A Ed25519 provider-authenticity tests.

The provenance record distinguishes among:

1. original tested source retained from the July execution;
2. artifacts independently retained on the Raspberry Pi and Windows test host;
3. sanitized derivatives prepared for public distribution;
4. contemporaneously recorded test results;
5. files intentionally excluded from publication.

The original interactive terminal transcript was not retained.

No reconstructed output is represented as original runtime evidence.

No sanitized derivative is represented as byte-identical to an original tested artifact when its SHA-256 digest differs.

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
NUVL verification boundary
    |
    v
Windows provider
```

Trust placement was:

```text
Windows provider:
    Ed25519 private signing key

Raspberry Pi:
    provider public verification key

ESP32-S3:
    no provider private signing key
```

Ed25519 provider-signature verification occurred at the Raspberry Pi boundary.

## Surviving Raspberry Pi Artifacts

Examination of the original Raspberry Pi test host identified the following surviving POC-002 artifacts:

```text
/home/seth/poc002_ed25519_pi_boundary.py
/home/seth/poc002_ed25519_public.pem
/home/seth/poc002_ed25519_public_correct.pem
/home/seth/poc002_ed25519_public_wrong.pem
```

Observed filesystem timestamps were:

```text
2026-07-19 20:59:01  /home/seth/poc002_ed25519_pi_boundary.py
2026-07-20 13:59:44  /home/seth/poc002_ed25519_public_wrong.pem
2026-07-20 14:04:14  /home/seth/poc002_ed25519_public_correct.pem
2026-07-20 14:12:13  /home/seth/poc002_ed25519_public.pem
```

These timestamps are retained as provenance metadata. They are not treated as cryptographic evidence.

## Cross-Host SHA-256 Correspondence

### Raspberry Pi Boundary

Raspberry Pi artifact:

```text
956e83b03b71c693641a8eee30e9dc8e2db6b8a71de008d052447ce5a06fafc9  /home/seth/poc002_ed25519_pi_boundary.py
```

Windows test-host copy:

```text
956e83b03b71c693641a8eee30e9dc8e2db6b8a71de008d052447ce5a06fafc9  poc002_ed25519_pi_boundary.py
```

**Result: SHA-256 match.**

The independently retained Raspberry Pi and Windows copies of the original boundary source are byte-identical.

The boundary implementation is not included in the public POC-002 package.

### Correct Provider Public Key

Raspberry Pi active public key:

```text
2fd9c44a0579b985bc44722313725c8a6fd532b665b617b3e5082efb14c49f63  /home/seth/poc002_ed25519_public.pem
```

Raspberry Pi preserved correct-key copy:

```text
2fd9c44a0579b985bc44722313725c8a6fd532b665b617b3e5082efb14c49f63  /home/seth/poc002_ed25519_public_correct.pem
```

Windows test-host copy:

```text
2fd9c44a0579b985bc44722313725c8a6fd532b665b617b3e5082efb14c49f63  poc002_ed25519_public.pem
```

**Result: SHA-256 match across all three retained copies.**

### Deliberately Incorrect Trust Anchor

Raspberry Pi wrong-key artifact:

```text
95eb0d5089b5ceda23e3cadc7cfb3c0f4af3fb787712716cfab46671216311b9  /home/seth/poc002_ed25519_public_wrong.pem
```

Publication copy:

```text
95eb0d5089b5ceda23e3cadc7cfb3c0f4af3fb787712716cfab46671216311b9  poc002_wrong_trust_anchor_public.pem
```

**Result: SHA-256 match.**

The deliberately incorrect trust anchor is cryptographically distinct from the correct provider public key.

## Original Windows Test-Host Source Hashes

The following SHA-256 values identify the retained original test sources before publication sanitization:

```text
956E83B03B71C693641A8EEE30E9DC8E2DB6B8A71DE008D052447CE5A06FAFC9  poc002_ed25519_pi_boundary.py
8D0430FF07FC938090D43E112B7276B481612491044D7D1F3F68BCB1EF1CD3EE  poc002_ed25519_provider.py
2FD9C44A0579B985BC44722313725C8A6FD532B665B617B3E5082EFB14C49F63  poc002_ed25519_public.pem
463D9FDF193ED7B37A99C8EDF1D7BDC5CEB282622E9990B383196CBD9E44A337  poc002_esp32_matrix_repeat.py
53C1CD04F9F2A51D83F88DC2231663738F51727D23401F17F40C538B974F6C7E  poc002_esp32_test.py
7D1C97E44C66A0BED6C3D53DDE25D22FB7532FB9237B67511E715509760CB242  poc002a_esp32_probe.py
```

The deliberately incorrect public verification key is identified by:

```text
95EB0D5089B5CEDA23E3CADC7CFB3C0F4AF3FB787712716CFAB46671216311B9  poc002_wrong_trust_anchor_public.pem
```

## Publication Sanitization

Environment-specific public network addressing was replaced in publication copies where required.

No test logic was intentionally changed as part of this sanitization.

Files modified by sanitization have different SHA-256 digests from their original tested versions and are classified as sanitized publication derivatives.

### Provider

Original tested source:

```text
8D0430FF07FC938090D43E112B7276B481612491044D7D1F3F68BCB1EF1CD3EE  poc002_ed25519_provider.py
```

Sanitized publication copy:

```text
32C5141E240EE812A1FB8073EDA0D96E586829A272FB8F1E613B64EAD8E04001  poc002_ed25519_provider.py
```

The publication copy is therefore not byte-identical to the July tested source.

### Boundary

Original tested source:

```text
956E83B03B71C693641A8EEE30E9DC8E2DB6B8A71DE008D052447CE5A06FAFC9  poc002_ed25519_pi_boundary.py
```

A sanitized derivative prepared during evidence recovery has SHA-256:

```text
B982C8939CFC52B15B54B17D821474BA4BEAC1C2B829F9B93B8E7EDC31461ED0  poc002_ed25519_pi_boundary.py
```

The boundary implementation is intentionally excluded from the public POC-002 package.

The sanitized derivative hash is retained only as part of the recovery record.

### Test Clients

The following publication files required no modification and remain byte-identical to the retained original test-host copies:

```text
53C1CD04F9F2A51D83F88DC2231663738F51727D23401F17F40C538B974F6C7E  poc002_esp32_test.py
463D9FDF193ED7B37A99C8EDF1D7BDC5CEB282622E9990B383196CBD9E44A337  poc002_esp32_matrix_repeat.py
7D1C97E44C66A0BED6C3D53DDE25D22FB7532FB9237B67511E715509760CB242  poc002a_esp32_probe.py
```

### Public-Key Artifacts

The correct provider public key required no publication modification:

```text
2FD9C44A0579B985BC44722313725C8A6FD532B665B617B3E5082EFB14C49F63  poc002_ed25519_public.pem
```

The deliberately incorrect trust anchor also required no publication modification:

```text
95EB0D5089B5CEDA23E3CADC7CFB3C0F4AF3FB787712716CFAB46671216311B9  poc002_wrong_trust_anchor_public.pem
```

Both files contain public verification material only.

## Private-Key Exclusion

The original test environment contained the provider's Ed25519 private signing key.

A separate private key existed for the unrelated keypair used during the trust-anchor substitution test.

Neither private key is included in the public repository.

The public package contains only the corresponding public verification material required to document the tested trust relationships.

Private-key exclusion is intentional and is not treated as missing evidence.

## Runtime Evidence Status

No original interactive POC-002 terminal transcript was located during evidence recovery.

The Raspberry Pi was examined for POC-002 and POC-002A artifacts and for files associated with the July 19–20 test period.

The surviving Pi-side artifacts identified were:

```text
poc002_ed25519_pi_boundary.py
poc002_ed25519_public.pem
poc002_ed25519_public_correct.pem
poc002_ed25519_public_wrong.pem
```

No retained POC-002 runtime-output file was identified.

The Raspberry Pi shell history contained extensive later NUVL test activity but did not identify a retained POC-002 terminal log or redirected POC-002 runtime-output file.

Accordingly, `RESULTS.md` records the observed results preserved in the contemporaneous laboratory record.

`RESULTS.md` is not a reconstructed terminal transcript and is not represented as raw runtime evidence.

## Evidence Classification

### Original Tested Source

Source retained from the July 19–20 execution and identified by its original SHA-256 digest.

### Independently Retained Artifact

An artifact preserved on more than one test system for which byte identity is established through matching SHA-256 digests.

The original Raspberry Pi boundary source and correct provider public key fall into this category.

### Sanitized Publication Derivative

A post-test copy modified solely for publication sanitation.

A sanitized derivative has its own SHA-256 digest and is not represented as the original tested artifact.

### Contemporaneous Result Record

Behavioral and numerical results recorded in the laboratory record during or immediately following the original test activity.

### Publication Manifest

`SHA256SUMS.txt` identifies the exact files distributed in the public GitHub directory.

The publication manifest is distinct from the original tested-source hashes preserved in this provenance record.

## Provenance Limitations

Matching SHA-256 digests establish byte identity between retained artifacts.

They do not independently establish execution time or prove a behavioral test result.

The POC-002 behavioral record therefore consists of the combined evidence provided by:

- surviving original test source;
- independently retained artifacts;
- contemporaneous laboratory results;
- consistency between the recorded test conditions and surviving test implementation.

The absence of the original interactive terminal transcript remains an explicit evidence limitation.

Any later reproduction of POC-002 constitutes a separate execution and requires its own date, runtime evidence, artifact hashes, and reproduction designation. It does not replace or become the original July 19–20, 2026 test record.
