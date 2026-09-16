# ESP-LOCAL-005 Provider Material

This directory contains the Ed25519 provider test key pair used for ESP-LOCAL-005 reproduction.

## Contents

- `ESP_LOCAL_005_private.pem`
- `ESP_LOCAL_005_public.pem`

These files contain the same Ed25519 test key material originally used for ESP-LOCAL-004.

For ESP-LOCAL-005 publication, the files were renamed to match the ESP-LOCAL-005 test package. The underlying key bytes and cryptographic identity were not changed.

## Role in ESP-LOCAL-005

The provider private key is used to generate signed bounded-authority objects.

The endpoint does not require the provider private key for execution. Endpoint-side verification uses the corresponding provider public key.

The authority relationship is:

Provider private key → signed bounded authority → endpoint-local verification → endpoint-local enforcement.

Possession of the public key permits verification but does not permit creation of new provider-signed authority.

## Key Identity

Raw Ed25519 public key:

`48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1`

Original private-key file SHA-256:

`DA0A36F274EFC6E3CE1C7643800B952B1AA2895201E5A6D6852D308729466509`

Original public-key PEM SHA-256:

`B9B33C65DDA94C39D8E48A2C563F18A24B6B9B460280184F81882BFA5C97C7ED`

Because the ESP-LOCAL-005 publication copies contain the same key bytes, their SHA-256 values remain unchanged.

## Test-Only Material

This key pair is published as test material for inspection and reproduction of ESP-LOCAL-005.

It does not protect a live or production deployment.

Authority instances generated with this key during ESP-LOCAL-005 are preserved separately in the `evidence/` directory.

Artifact lineage is documented in `../PROVENANCE.md`.

Published artifact hashes are recorded in `../SHA256SUMS.txt`.
