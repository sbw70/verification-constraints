# AE001 Association Trust Material

This directory contains the public provider boundary-signing keys used by the AE001 association recorder.

## Contents

```text
trust/
├── provider_a_public.pem
└── provider_b_public.pem
```

These are public Ed25519 keys corresponding to the provider boundary-signing identities used by the copied MP003 implementation.

They are not authorization-issuance keys.

## Purpose

The association recorder receives provider-generated boundary packages and uses the provider registry plus these public keys to verify the claimed provider signature.

For AE001, this allows the recorder to preserve evidence such as:

- Provider A `DENY`;
- Provider B `START`;
- Provider B `COMPLETE`; and
- Provider B `DENY`.

Verification by the recorder does not authorize execution.

The provider remains the authority that evaluates authorization material, determines whether to initiate its software operation, and generates the signed boundary package.

## Provider Separation

Provider A and Provider B use distinct boundary-signing key pairs.

The recorder therefore verifies each provider submission against the public key associated with that provider rather than treating provider identity as interchangeable.

The corresponding provider-side private keys are preserved in the provider source directories because AE001 publishes the laboratory implementation and keys used for reproduction.

## AE001 Use

The relay does not use these keys to authorize requests.

The association recorder is a separate evidentiary process. It receives boundary packages directly from the providers and verifies their signatures for recording purposes.

The scored AE001 harness also independently verifies the raw provider packages and does not rely on the recorder's verification fields as its signature-verification oracle.

## Scope

These files establish the public verification material used by the AE001 laboratory association recorder.

They do not establish:

- trust in a production PKI;
- hardware-backed key custody;
- key revocation behavior;
- post-publication secrecy of laboratory private keys;
- independent timestamping; or
- authorization authority outside the provider.

Exact file identities are recorded in the AE001 source and run manifests.
