# Provider B Authorization Evidence

This directory contains Provider B authorization packages retained from the MP001 scored campaign.

Each authorization was issued independently by Provider B for a specific request representation and verification context. Provider B authorization does not authorize Provider A, and the NUVL intermediary does not mint, validate, or enlarge these authorizations.

## File forms

Most authorization cases are retained in two representations.

Files ending in `_auth.json` contain the Provider B authorization package as canonical JSON.

Files ending in `_auth.json.b64` contain the same package encoded as unpadded base64url for transport in the `X-Provider-B-Authorization` request header.

The decoded authorization package has three top-level fields:

- `alg`
- `authorization`
- `signature`

For MP001, `alg` is `Ed25519`.

The signed `authorization` object contains:

- `version`
- `provider_id`
- `authorization_id`
- `request_repr`
- `verification_context`
- `nonce`

The normative construction and signature rules are defined in `../../../configs/MP001_CONTRACT.md`.

## Baseline authorizations

The baseline series is represented by:

- `B01_auth.json` and `B01_auth.json.b64`
- `B02_auth.json` and `B02_auth.json.b64`
- `B03_auth.json` and `B03_auth.json.b64`
- `B04_auth.json` and `B04_auth.json.b64`
- `B05_auth.json` and `B05_auth.json.b64`
- `B06_auth.json` and `B06_auth.json.b64`
- `B07_auth.json` and `B07_auth.json.b64`
- `B08_auth.json` and `B08_auth.json.b64`
- `B09_auth.json` and `B09_auth.json.b64`
- `B10_auth.json` and `B10_auth.json.b64`

Each baseline authorization is bound to the SHA-256 representation of its corresponding request body and to the verification context `CTX_ALPHA`.

`mint_baseline.log` records the Provider B minting output for B01 through B10, including:

- request representation
- authorization ID
- authorization nonce
- package SHA-256
- original package path
- original base64url header-file path

The baseline request hashes are retained in `../baseline_request_hashes.txt`.

## Negative-test authorizations

This directory also contains the Provider B authorization packages used for:

- `N01`
- `N02`
- `N04`
- `N05`
- `N05_RETRY_001`
- `N06`

### N01

Provider B received an intact authorization during N01.

The corrupted authorization-signature condition applied only to Provider A. Provider B therefore retained and processed its own valid authorization independently.

### N02

The N02 Provider B authorization remained unchanged while the hostile relay case altered the request representation and recomputed the non-secret mechanical binding.

Because the retained authorization remained bound to the original request representation, Provider B denied the altered artifact with `auth_request_mismatch`.

### N04

The N04 authorization supported the valid Provider B execution in the duplicate-boundary case.

The later duplicate submitted to the association was an exact replay of a Provider A `COMPLETE` boundary package. It was not a replay of this Provider B authorization.

### N05

`N05_auth.json` and its base64url representation belong to the initial N05 attempt.

That attempt did not satisfy the intended Provider-B-unavailable precondition because Provider B was still running.

The attempt was retained rather than removed from the evidence.

### N05_RETRY_001

`N05_RETRY_001_auth.json` and its base64url representation contain the fresh Provider B authorization created for the scored N05 retry.

Provider B unavailability was verified before the retry was submitted.

Because Provider B was unavailable during the scored retry, this authorization was not consumed during that retry.

### N06

The N06 authorization was submitted twice without alteration.

The first submission was accepted and consumed.

The second submission was denied by Provider B with `auth_spent`, demonstrating ordinary sequential single-use enforcement for the same intact authorization.

## Authorization identity

For MP001, Provider B computes `authorization_id` from the canonical authorization core using the domain-separated SHA-256 construction defined in the contract.

The authorization is then signed with Provider B's Ed25519 issuance key.

The issuance keypair is separate from Provider B's boundary-signing keypair.

The NUVL intermediary does not possess or use the Provider B issuance private key.

The association does not use Provider B's issuance key to score boundary submissions. It verifies Provider B boundary events using the separate boundary public key registered with the association.

## Relationship to request files

The corresponding raw request bodies are retained in:

`../requests/`

The authorization's `request_repr` is the SHA-256 digest of the exact raw request bytes.

Changing the request bytes does not change an already-issued authorization. A changed request therefore cannot acquire new Provider B authority merely by recomputing the public mechanical binding.

## Integrity

All files in this directory that formed part of the scored campaign are covered by:

`../SHA256SUMS.txt`

The baseline authorization set is also preserved in:

`../B01_B10_auth_b.tar`

The negative-case Provider B authorization set is preserved in:

`../N_NEG_auth_b.tar`

These archive copies provide an additional retained representation of the authorization material used during the campaign.

## Scope

This directory establishes the Provider B authorization artifacts retained for MP001.

It does not by itself establish:

- that Provider B executed
- that an authorization was consumed
- that a boundary signature was accepted by the association
- intermediary behavior
- Provider A authorization
- campaign PASS or FAIL status

Those properties are established by the corresponding provider-local state, requester logs, association records, and campaign scorecard elsewhere in `MP001_SCORED_20261009/`.
