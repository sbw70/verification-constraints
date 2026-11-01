# MP005 — Association Trust Keys

## Purpose

This directory contains the frozen Ed25519 public keys used by the MP005 association recorder to verify provider-originated boundary events.

The keys are retained as part of MP006's unchanged MP005 reference dependencies.

They support verification of provider identity and event authenticity.

They do not grant execution authority.

## Directory Contents

| File | Purpose |
|---|---|
| [provider_a_public.pem](provider_a_public.pem) | Verify Provider A boundary signatures |
| [provider_b_public.pem](provider_b_public.pem) | Verify Provider B boundary signatures |

Both files contain public keys only.

No private signing keys belong in this directory.

## Registered Provider Identities

The parent [provider_registry.json](../provider_registry.json) associates each provider with its expected public key.

### Provider A

**Provider ID:** `PROVIDER_A`

**Key ID:**

`sha256:e4664ee3b7bb0012fb7d8f763c9df74594d8a6bec8488d97532a5846cc04b6ff`

**Public-key file:**

`provider_a_public.pem`

### Provider B

**Provider ID:** `PROVIDER_B`

**Key ID:**

`sha256:db764408aa319642363057d804f0c2a3d2c7dd22de86ae4a6d6549cb97f60225`

**Public-key file:**

`provider_b_public.pem`

The key identifiers are calculated from the raw Ed25519 public-key bytes.

They are not SHA-256 hashes of the PEM file contents.

## Signature Verification

The association recorder loads the provider registry and its referenced public keys.

During registry initialization, it:

1. Reads each registered public-key file.
2. Confirms the key uses Ed25519.
3. Calculates the public-key identifier.
4. Compares that identifier with the registry.
5. Rejects mismatched identities.

For a submitted boundary event, the recorder verifies the signature against the registered provider key.

The boundary signature domain is:

`NUVL-MP-BOUNDARY-v1|`

The verification result is preserved in the association evidence.

A valid signature establishes that an event verifies against the registered key.

It does not independently prove physical execution or authorize another operation.

## Key Identity Verification

The two public-key files match their corresponding frozen provider reference files.

| Association key | Provider reference |
|---|---|
| `provider_a_public.pem` | `../../provider_a/provider_a_public.pem` |
| `provider_b_public.pem` | `../../provider_b/provider_b_public.pem` |

### Provider A PEM SHA-256

`4f9f01b0296f75a7acf8c3fd11bf7f27d75f0526e7912a02d0a725b1e6fbaa19`

### Provider B PEM SHA-256

`bcb4441a3ad143b5a3d646189d15ba806340c52530ba9b5ef4e19f30e0c59e47`

These values are preserved in the original MP006 build inventory.

## Authority Separation

These public keys belong to the boundary-observation verification process.

They must not be confused with the separate authorization-issuance key pairs.

The distinction is essential:

**Authorization issuance**

The provider verifies authorization artifacts using its configured issuance public key.

**Boundary signaling**

The provider signs boundary events using its boundary private key.

The association recorder verifies those events using the corresponding boundary public key.

The association recorder cannot create valid provider signatures using these public keys.

It also cannot authorize provider execution.

## Preservation Rules

- Do not replace these keys with newly generated keys.
- Do not modify the provider registry to accommodate mismatches.
- Do not substitute issuance keys for boundary keys.
- Do not copy provider private keys into this directory.
- Do not disable signature verification to make tests pass.
- Do not treat successful signature verification as proof of execution.

If a registered key identity does not match the expected value, preserve the failure.

Do not repair historical evidence or frozen reference material.

## Evidence Boundary

These files establish the public-key identities used for association-event verification.

They do not independently establish that a particular event was received, verified, or acted upon.

Those observations are recorded in the corresponding association evidence.

The original MP006-R01 experiment preserves its signed boundary records separately.

## Related Documentation

- [Association recorder](../README.md)
- [Provider registry](../provider_registry.json)
- [Provider A reference](../../provider_a/README.md)
- [Provider B reference](../../provider_b/README.md)
- [MP006 evidence](../../../../evidence/)
