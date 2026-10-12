# Provider B

This directory contains the MP001 implementation and cryptographic material for `PROVIDER_B`.

Provider B is an independent execution authority in MP001. It verifies only Provider B authorization, maintains its own spent state, records its own local execution evidence, and signs its own boundary statements.

Provider A authority does not authorize Provider B.

The NUVL intermediary does not decide whether Provider B executes.

The association records and verifies Provider B boundary statements but does not authorize Provider B execution.

## Files

### `provider_b.py`

Provider B runtime.

The runtime listens on:

`0.0.0.0:9090`

and accepts relay artifacts at:

`POST /ingest`

It also exposes:

`GET /health`

The runtime independently validates each received artifact according to the MP001 contract.

Its validation sequence includes:

1. recompute the mechanical binding
2. require Provider B authorization
3. decode the authorization package
4. require `provider_id` to equal `PROVIDER_B`
5. recompute the authorization ID
6. verify the Provider B Ed25519 issuance signature
7. require the authorized request representation to match the received request representation
8. require the authorized verification context to match the received context
9. require the authorization to be unspent
10. durably record the authorization as spent
11. generate a signed `START`
12. perform the provider-local execution step
13. durably append local execution evidence
14. generate a signed `COMPLETE`

A failed validation produces a signed Provider B `DENY` statement with the applicable reason code.

No `START` is generated before durable authorization consumption.

### `mint_authorization_b.py`

Provider B authorization-minting utility.

It accepts:

- a request file
- a verification context
- an output path

It computes the SHA-256 representation of the exact request bytes, creates a fresh Provider B authorization nonce, derives the Provider B authorization ID, and signs the resulting authorization with the Provider B issuance private key.

It writes:

- canonical JSON authorization package
- sibling `.b64` file containing the unpadded base64url transport representation

The output is intended for transport in:

`X-Provider-B-Authorization`

The utility refuses to overwrite an existing output file.

## Issuance keys

Provider B authorization issuance uses:

- `provider_b_issuance_private.pem`
- `provider_b_issuance_public.pem`

The issuance keypair is used to create and verify Provider B authorization packages.

`provider_b.py` loads only the issuance public key for authorization verification.

The issuance keypair is separate from the boundary-signing keypair.

The PEM files published here are the laboratory keys used by MP001 and are retained with the implementation for reproducibility of the published test.

## Boundary-signing keys

Provider B boundary statements use:

- `provider_b_private.pem`
- `provider_b_public.pem`

The private key signs Provider B `START`, `COMPLETE`, and `DENY` events.

The public key corresponds to the Provider B trust anchor registered with the association.

The MP001 Provider B boundary key ID is:

`sha256:db764408aa319642363057d804f0c2a3d2c7dd22de86ae4a6d6549cb97f60225`

The boundary keypair does not issue Provider B authorization. That function remains separate under the issuance keypair.

## Provider-local state

At runtime, Provider B uses two additional local state files:

`provider_b_spent_state.json`

`provider_b_execution.jsonl`

These files are runtime state rather than source files in this directory.

### Spent state

`provider_b_spent_state.json` contains the Provider B authorization IDs already consumed by the runtime.

The runtime requires valid spent state at startup and fails closed if the state file is missing or invalid.

When a fresh authorization is consumed, Provider B writes updated state to a temporary file, flushes and synchronizes it, atomically replaces the existing state file, and synchronizes the containing directory before treating the authorization as consumed.

Spent state is local to Provider B.

Provider A does not read or control it.

### Execution log

`provider_b_execution.jsonl` is the append-only Provider B local execution log.

For each completed provider-local execution, it records:

- provider identity
- local execution sequence
- local UTC observation
- local monotonic observation
- operation ID
- authorization ID
- result

Each appended execution record is flushed and synchronized before the runtime proceeds to the signed `COMPLETE` statement.

The scored campaign's final copies of both Provider B state files are retained under:

`../evidence/MP001_SCORED_20261009/final_provider_b/`

## Boundary statements

Provider B generates signed boundary packages for three stages:

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

Provider B sends these statements to the association endpoint configured in the runtime:

`http://192.168.1.102:9191/boundary`

Failure to deliver a boundary statement to the association does not transfer execution authority to the association. Provider B's authorization decision remains local.

## Denial reasons

The runtime can generate Provider B denials including:

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

A `DENY` is a signed Provider B statement about Provider B's own validation result.

It is not an association decision.

## Single-use behavior

Provider B authorization is single-use in MP001.

After a valid authorization ID has been durably recorded as spent, a later intact replay of that same authorization is denied with:

`auth_spent`

MP001 exercises ordinary sequential replay.

This provider implementation should not be read as independently establishing crash-window, concurrent-contention, or power-loss properties beyond the specific MP001 campaign.

## Correlation versus authority

Provider B independently derives `operation_id` from the expected mechanical binding.

Provider A can derive the same operation ID for the same request representation and verification context.

That common value exists for correlation only.

It does not:

- authorize Provider B
- transfer Provider A authority to Provider B
- require Provider B to trust Provider A
- require Provider B to wait for Provider A
- combine provider spent state
- combine provider execution state

Provider B execution remains conditioned on Provider B's own valid authorization.

## Scored implementation hash

The deployed Provider B runtime used for the scored campaign had SHA-256:

`7759ae8604515ef711ea8cde7b867c3b8faf19e26aedbd48c29d6099fd804fa1`

The deployed Provider B authorization mint had SHA-256:

`1b3ba1314761a5489817c660cdc4d62e65ba77deae2bfce2fdce48c228f98deb`

These values are retained in:

`../evidence/MP001_SCORED_20261009/deployed_implementation_hashes.txt`

## Scope

This directory contains the Provider B implementation and MP001 laboratory key material.

It does not by itself establish:

- scored campaign results
- Provider A behavior
- intermediary behavior
- association behavior
- physical actuation
- independent physical witness confirmation
- globally synchronized chronology

Those results and observations are retained in the corresponding MP001 evidence directories.
