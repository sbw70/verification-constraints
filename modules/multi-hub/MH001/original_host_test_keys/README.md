
# MH001 — Original Provider Test Signing Keys

## Purpose

This directory preserves the original Ed25519 signing-key pairs generated on Provider A and Provider B during the MH001 R4.3 scored experiment.

These are the actual test keys used during session `MH001_R43_RUN001`, not replacements or regenerated equivalents.

The keys are published intentionally to permit independent verification of the original authorization artifacts, provider signatures, and recorded evidence.

## Directory Contents

```text
original_host_test_keys/
├── provider_a/
│   ├── provider_a_issuance_private.pem
│   ├── provider_a_issuance_public.pem
│   ├── provider_a_private.pem
│   └── provider_a_public.pem
└── provider_b/
    ├── provider_b_issuance_private.pem
    ├── provider_b_issuance_public.pem
    ├── provider_b_private.pem
    └── provider_b_public.pem
```

Each provider has two independent keypairs.

**Issuance keypair:** Used by the provider-controlled authorization issuance process.

**Boundary-signing keypair:** Used to sign provider-generated boundary events, including execution and denial evidence.

The two providers maintain separate cryptographic identities.

## Original File Integrity

The following SHA-256 values were verified against the files retrieved from their original provider hosts.

### Provider A — Dell

| File | SHA-256 |
|---|---|
| `provider_a_issuance_private.pem` | `a46c71f1fc5c3b8b8e9091831ec8d14f053ecc5bac392999af3270eb04c5488f` |
| `provider_a_issuance_public.pem` | `b47771c0cbc64d22f60e84982062c434a8090546f7360b6c1e3f3b2c4662d2a2` |
| `provider_a_private.pem` | `e608499899b573685c1aaea59e9236e5c7c03e6918f03caac80d81fa848cc0d5` |
| `provider_a_public.pem` | `4575b0b5fe2b4b6bf90c80313c889dc44b415e9bf73af0bcbc39b8ac1e4dee6c` |

### Provider B — HP

| File | SHA-256 |
|---|---|
| `provider_b_issuance_private.pem` | `5c2d55091418526cc87c527cddb24cdd70c3f9e7386ed775d96f109198767a82` |
| `provider_b_issuance_public.pem` | `b65128e2e111cab1591a2e6dfd94159447b62a1d989ffc70202a0c53a9ebad7e` |
| `provider_b_private.pem` | `0ee5a74647181c054bda28f9d648fef583758cb3a5f3485592a07fb9227804d6` |
| `provider_b_public.pem` | `f6255b7402eeebb16b92917ce47e48cc03ecee003530816f2951e1f17b5d75af` |

These hashes identify the complete PEM file bytes. They should not be confused with the provider key identifiers recorded by the test's trust registry.

## Public Disclosure and Trust Status

**All eight files are laboratory test materials.**

The private keys are publicly disclosed and must be treated as compromised by publication.

They must never be used for production systems, operational authorization, or any environment that depends on their secrecy.

Their disclosure is deliberate and does not represent an accidental credential leak.

The original files are retained unchanged because their identities are part of the reproducible historical experiment.

## Reproduction Requirements

For examination of the recorded MH001 evidence, use the original public keys and recorded identities.

For exact reproduction of historical signatures and authorization artifacts, preserve the original key bytes.

For a new independent execution experiment, establish fresh provider-controlled signing identities and fresh persistent state.

Do not reuse these publicly disclosed private keys as trusted authority for a new operational environment.

Do not replace the published historical keys or modify the original signatures to make verification succeed.

## Evidence Boundary

These eight files were collected from their original provider hosts after the scored experiment and added as supplemental publication materials.

They are not members of the original 132-file scored-run manifest.

The separation preserves the original scored evidence inventory while making the signing material available for reproducibility.

No passwords or unrelated operational credentials are included in this directory.
