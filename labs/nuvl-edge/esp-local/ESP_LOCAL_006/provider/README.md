# ESP-LOCAL-006 Provider Material

This directory contains the provider-issued authority artifacts and wrong-provider control material used during ESP-LOCAL-006.

The material supports inspection of the signed authority objects presented through the hostile relay and the comparison between trusted-provider and untrusted-provider signatures over identical canonical authority bytes.

## Contents

### `ESP_LOCAL_006_AUTH1.txt`

Metadata for Authority #1.

It preserves:

- the authority nonce,
- the canonical authority representation,
- the SHA-256 authority identifier,
- the provider signature,
- the trusted provider raw Ed25519 public key.

Authority #1 was used for the relay-mutation matrix and the subsequent untouched positive control and replay case.

### `ESP_LOCAL_006_AUTH1_REQUEST.json`

The request envelope carrying Authority #1 and its trusted-provider signature.

The request contains:

```json
{
  "authority_b64": "<base64 canonical authority bytes>",
  "signature_b64": "<base64 Ed25519 signature>"
}
```

The same Authority #1 request was used as the source object for relay mutation cases and later forwarded unchanged for the positive-control execution and replay test.

### `ESP_LOCAL_006_AUTH2.txt`

Metadata for Authority #2.

It preserves:

- the authority nonce,
- the canonical authority representation,
- the SHA-256 authority identifier,
- the trusted-provider raw public key,
- the wrong-provider raw public key,
- the trusted-provider signature,
- the wrong-provider signature.

Authority #2 was used for the different-provider-key control.

### `ESP_LOCAL_006_AUTH2_TRUSTED_REQUEST.json`

Request envelope containing the trusted-provider signature over Authority #2.

### `ESP_LOCAL_006_AUTH2_WRONG_PROVIDER_REQUEST.json`

Request envelope containing the wrong-provider signature over the same canonical Authority #2 bytes.

### `ESP_LOCAL_006_WRONG_PROVIDER_PUBLIC.pem`

Public key corresponding to the independent wrong-provider Ed25519 keypair generated for the Auth2 negative control.

The endpoint did not trust this key.

The corresponding private key is intentionally not included in the publication package.

## Authority Semantics

Both tested authorities used the same bounded semantics apart from their independent nonces:

```json
{
  "action": "move_servo",
  "context": "esp_local_006",
  "device_id": "esp32-xiao-servo-02",
  "max_uses": 1,
  "nonce": "<authority-specific nonce>"
}
```

The authority identifier is the SHA-256 digest of the canonical authority bytes.

## Trusted Provider Identity

The trusted provider raw Ed25519 public key used by the tested endpoint was:

```text
48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1
```

Authority #1 identifier:

```text
f72ade66cea3c93c2cb57944e03d69e185a061a59f83c3705a8e6977dfddc7d6
```

Authority #2 identifier:

```text
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc
```

## Wrong-Provider Control

A separate Ed25519 keypair was generated specifically for the Auth2 negative control.

Its raw public key was:

```text
4c0baa6a6df7637dbb78aec1262c142be80f66d68eac3fd91f7ee41ee003a2de
```

This key was distinct from the trusted provider key and was not configured as a trusted verification key at the endpoint.

The control was constructed so that the trusted and wrong-provider requests contained identical canonical Authority #2 bytes.

Only the signatures differed.

The preserved relationship is:

```text
same canonical authority bytes
        ↓
trusted-provider signature
        ↓
trusted request
```

and:

```text
same canonical authority bytes
        ↓
independent wrong-provider signature
        ↓
wrong-provider request
```

During verification of the published test artifacts, the two requests were confirmed to satisfy:

```text
authority_bytes_equal: True

authority_sha256:
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc

signatures_equal: False
```

This control isolates provider-key trust from authority-content differences.

## Relationship to the Hostile Relay

The relay did not hold the trusted provider private key.

For mutation cases, it altered fields inside Authority #1 while retaining the original trusted-provider signature.

That produced modified authority content for which the relay could not generate a replacement trusted signature.

For the wrong-provider case, the relay forwarded the separately signed Auth2 request without changing its bytes.

The endpoint remained responsible for deciding whether the presented signature corresponded to trusted provider authority.

## Publication Boundary

The trusted provider private key is not included in this ESP-LOCAL-006 publication directory.

The wrong-provider private key is also not included.

The wrong-provider public key and signed wrong-provider request are sufficient to preserve and inspect the negative-control relationship used in the test.

The publication package therefore exposes the authority objects, signatures, request envelopes, trusted provider identity, and wrong-provider public key without publishing private signing material.

## Test Relationship

Authority #1 was used to exercise:

- relay mutation of `action`,
- relay mutation of `context`,
- relay mutation of `device_id`,
- relay enlargement of `max_uses`,
- untouched trusted positive control,
- replay after successful consumption.

Authority #2 was used to exercise:

- wrong-provider signature rejection,
- trusted-provider positive control over the same authority bytes,
- replay after successful trusted execution.

Observed endpoint and relay outcomes are documented in:

```text
../RESULTS.md
```

Relay transaction evidence is stored in:

```text
../evidence/ESP_LOCAL_006_RELAY_AUTH1.jsonl
../evidence/ESP_LOCAL_006_RELAY_AUTH2.jsonl
```

Endpoint decision evidence is stored in:

```text
../evidence/ESP_LOCAL_006_ENDPOINT_COM15_CURATED.txt
```

Persistent-state captures are stored in:

```text
../evidence/ESP_LOCAL_006_AUTH1_SPENT_FINAL.bin
../evidence/ESP_LOCAL_006_AUTH2_UNSPENT.bin
../evidence/ESP_LOCAL_006_AUTH2_SPENT_FINAL.bin
```

Artifact lineage is documented in:

```text
../PROVENANCE.md
```

Published artifact hashes are recorded in:

```text
../SHA256SUMS.txt
```
