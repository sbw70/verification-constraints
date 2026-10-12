# Provider A

This directory contains the MP001 implementation and cryptographic material for `PROVIDER_A`.

Provider A is an independent execution authority in MP001. It verifies only Provider A authorization, maintains its own spent state, records its own local execution evidence, and signs its own boundary statements.

Provider B authority does not authorize Provider A.

The NUVL intermediary does not decide whether Provider A executes.

The association records and verifies Provider A boundary statements but does not authorize Provider A execution.

## Files

### `provider_a.py`

Provider A runtime.

The runtime listens on:

`0.0.0.0:9090`

and accepts relay artifacts at:

`POST /ingest`

It also exposes:

`GET /health`

The runtime independently validates each received artifact according to the MP001 contract.

Its validation sequence includes:

1. recompute the mechanical binding
2. require Provider A authorization
3. decode the authorization package
4. require `provider_id` to equal `PROVIDER_A`
5. recompute the authorization ID
6. verify the Provider A Ed25519 issuance signature
7. require the authorized request representation to match the received request representation
8. require the authorized verification context to match the received context
9. require the authorization to be unspent
10. durably record the authorization as spent
11. generate a signed `START`
12. perform the provider-local execution step
13. durably append local execution evidence
14. generate a signed `COMPLETE`

A failed validation produces a signed Provider A `DENY` statement with the applicable reason code.

No `START` is generated before durable authorization consumption.

### `mint_authorization_a.py`

Provider A authorization-minting utility.

It accepts:

- a request file
- a verification context
- an output path

It computes the SHA-256 representation of the exact request bytes, creates a fresh Provider A authorization nonce, derives the Provider A authorization ID, and signs the resulting authorization with the Provider A issuance private key.

It writes:

- canonical JSON authorization package
- sibling `.b64` file containing the unpadded base64url transport representation

The output is intended for transport in:

`X-Provider-A-Authorization`

The utility refuses to overwrite an existing output file.

## Issuance keys

Provider A authorization issuance uses:

- `provider_a_issuance_private.pem`
- `provider_a_issuance_public.pem`

The issuance keypair is used to create and verify Provider A authorization packages.

`provider_a.py` loads only the issuance public key for authorization verification.

The issuance keypair is separate from the boundary-signing keypair.

The PEM files published here are the laboratory keys used by MP001 and are retained with the implementation for reproducibility of the published test.

## Boundary-signing keys

Provider A boundary statements use:

- `provider_a_private.pem`
- `provider_a_public.pem`

The private key signs Provider A `START`, `COMPLETE`, and `DENY` events.

The public key corresponds to the Provider A trust anchor registered with the association.

The MP001 Provider A boundary key ID is:

`sha256:e4664ee3b7bb0012fb7d8f763c9df74594d8a6bec8488d97532a5846cc04b6ff`

The boundary keypair does not issue Provider A authorization. That function remains separate under the issuance keypair.

## Provider-local state

At runtime, Provider A uses two additional local state files:

`provider_a_spent_state.json`

`provider_a_execution.jsonl`

These files are runtime state rather than source files in this directory.

### Spent state

`provider_a_spent_state.json` contains the Provider A authorization IDs already consumed by the runtime.

The runtime requires valid spent state at startup and fails closed if the state file is missing or invalid.

When a fresh authorization is consumed, Provider A writes updated state to a temporary file, flushes and synchronizes it, atomically replaces the existing state file, and synchronizes the containing directory before treating the authorization as consumed.

Spent state is local to Provider A.

Provider B does not read or control it.

### Execution log

`provider_a_execution.jsonl` is the append-only Provider A local execution log.

For each completed provider-local execution, it records:

- provider identity
- local execution sequence
- local UTC observation
- local monotonic observation
- operation ID
- authorization ID
- result

Each appended execution record is flushed and synchronized before the runtime proceeds to the signed `COMPLETE` statement.

The scored campaign's final copies of both Provider A state files are retained under:

`../evidence/MP001_SCORED_20261009/final_provider_a/`

## Boundary statements

Provider A generates signed boundary packages for three stages:

- `START`
- `COMPLETE`
- `DENY`

Each signed event includes:

- operation ID
- mechanical binding
- provider ID
- boundary key ID
- stage
- fresh boundary value
- authorization ID when available
- authorization nonce when available
- denial reason when applicable

The entire event is signed using the MP001 boundary-signing domain separator.

Provider A sends these statements to the association endpoint configured in the runtime:

`http://192.168.1.102:9191/boundary`

Failure to deliver a boundary statement to the association does not transfer execution authority to the association. Provider A's authorization decision remains local.

## Denial reasons

The runtime can generate Provider A denials including:

- `binding_mismatch`
- `auth_missing`
- `auth_malformed`
- `auth_provider_mismatch`
- `auth_id_mismatch`
- `auth_bad_sig`
- `auth_request_mismatch`
- `auth_context_mismatch`
- `auth_spent`
- `auth_state_error`

A `DENY` is a signed Provider A statement about Provider A's own validation result.

It is not an association decision.

## Single-use behavior

Provider A authorization is single-use in MP001.

After a valid authorization ID has been durably recorded as spent, a later intact replay of that same authorization is denied with:

`auth_spent`

MP001 exercises ordinary sequential replay.

This provider implementation should not be read as independently establishing crash-window, concurrent-contention, or power-loss properties beyond the specific MP001 campaign.

## Correlation versus authority

Provider A independently derives `operation_id` from the expected mechanical binding.

Provider B can derive the same operation ID for the same request representation and verification context.

That common value exists for correlation only.

It does not:

- authorize Provider A
- transfer Provider B authority to Provider A
- require Provider A to trust Provider B
- require Provider A to wait for Provider B
- combine provider spent state
- combine provider execution state

Provider A execution remains conditioned on Provider A's own valid authorization.

## Scored implementation hash

The deployed Provider A runtime used for the scored campaign had SHA-256:

`c875582b275f270b8e68af69ed4ee84896e83815cdf33b7d7c5ccc813fe2e606`

The deployed Provider A authorization mint had SHA-256:

`1a485e8a5d3de854cb31303b8d3bf1339ef72cb9b42f308490bd02519e76d7ec`

These values are retained in:

`../evidence/MP001_SCORED_20261009/deployed_implementation_hashes.txt`

## Scope

This directory contains the Provider A implementation and MP001 laboratory key material.

It does not by itself establish:

- scored campaign results
- Provider B behavior
- intermediary behavior
- association behavior
- physical actuation
- independent physical witness confirmation
- globally synchronized chronology

Those results and observations are retained in the corresponding MP001 evidence directories.
