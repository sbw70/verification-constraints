# Provider A Authorization Evidence

This directory contains Provider A authorization packages retained from the MP001 scored campaign.

Each authorization was issued independently by Provider A for a specific request representation and verification context. Provider A authorization does not authorize Provider B, and the NUVL intermediary does not mint, validate, or enlarge these authorizations.

## File forms

Most authorization cases are retained in two representations.

Files ending in `_auth.json` contain the Provider A authorization package as canonical JSON.

Files ending in `_auth.json.b64` contain the same package encoded as unpadded base64url for transport in the `X-Provider-A-Authorization` request header.

The decoded authorization package contains:

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

`mint_baseline.log` records Provider A minting output for B01 through B10, including:

- request representation
- authorization ID
- authorization nonce
- package SHA-256
- original package path
- original base64url header-file path

The baseline request hashes are retained in `../baseline_request_hashes.txt`.

## Negative-test authorizations

This directory also contains Provider A authorization packages used for:

- `N01`
- `N02`
- `N04`
- `N05`
- `N05_RETRY_001`
- `N06`

### N01

N01 tests a corrupted Provider A authorization signature.

The directory retains both:

- the original valid Provider A authorization
- the deliberately corrupted-signature derivative

The files are:

- `N01_auth.json`
- `N01_auth.json.b64`
- `N01_auth_CORRUPT_SIG.json`
- `N01_auth_CORRUPT_SIG.json.b64`

The authorization body, authorization ID, request representation, verification context, and nonce remain unchanged between the valid and corrupted JSON packages.

The signature is altered in the corrupted derivative.

Provider A rejected the corrupted package with `auth_bad_sig`.

The malformed signature submission did not create new Provider A authority and did not consume the valid authorization represented by the original package.

### N02

The N02 Provider A authorization remained unchanged while the hostile relay case altered the request representation and recomputed the non-secret mechanical binding.

Because the authorization remained bound to the original request representation, Provider A denied the altered artifact with `auth_request_mismatch`.

### N04

The N04 authorization was used for a valid Provider A execution.

After that execution completed, an exact copy of the signed Provider A `COMPLETE` boundary package was submitted to the association again.

The duplicate observed in N04 is therefore a replay of a boundary submission, not a replay of the authorization file in this directory.

### N05

`N05_auth.json` and its base64url representation belong to the initial N05 attempt.

The intended Provider-B-unavailable precondition was not satisfied during that attempt, but Provider A remained available and independently processed its own authorization.

The attempt was retained rather than deleted.

### N05_RETRY_001

`N05_RETRY_001_auth.json` and its base64url representation contain the fresh Provider A authorization created for the scored N05 retry.

Provider A remained available during the retry and independently executed under this fresh authorization while Provider B was verified unavailable.

### N06

The N06 authorization was submitted twice without alteration.

The first submission was accepted and consumed.

The second submission was denied by Provider A with `auth_spent`, demonstrating ordinary sequential single-use enforcement for the same intact authorization.

## Authorization identity

For MP001, Provider A computes `authorization_id` from the canonical authorization core using the domain-separated SHA-256 construction defined in the contract.

The authorization is then signed with Provider A's Ed25519 issuance key.

The issuance keypair is separate from Provider A's boundary-signing keypair.

The NUVL intermediary does not possess or use the Provider A issuance private key.

The association does not use Provider A's issuance key to verify boundary submissions. It verifies Provider A boundary events using the separate boundary public key registered with the association.

## Relationship to request files

The corresponding raw request bodies are retained in:

`../requests/`

The authorization's `request_repr` is the SHA-256 digest of the exact raw request bytes.

Changing the request bytes does not change an already-issued authorization. A changed request therefore cannot acquire new Provider A authority merely by recomputing the public mechanical binding.

## Integrity

All files in this directory that formed part of the scored campaign are covered by:

`../SHA256SUMS.txt`

The baseline authorization set is also preserved in:

`../B01_B10_auth_a.tar`

The negative-case Provider A authorization set is preserved in:

`../N_NEG_auth_a.tar`

These archive copies provide an additional retained representation of the authorization material used during the campaign.

## Scope

This directory establishes the Provider A authorization artifacts retained for MP001.

It does not by itself establish:

- that Provider A executed
- that an authorization was consumed
- that a boundary signature was accepted by the association
- intermediary behavior
- Provider B authorization
- campaign PASS or FAIL status

Those properties are established by the corresponding provider-local state, requester logs, association records, and campaign scorecard elsewhere in `MP001_SCORED_20261009/`.
