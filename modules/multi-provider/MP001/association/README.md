# Association

This directory contains the MP001 association recorder, provider registry, and trusted provider boundary public keys.

The association is an evidence and verification role.

It records provider boundary submissions, verifies provider boundary signatures, preserves raw received bytes, identifies duplicates, and maintains a local append-only observation chain.

It does not authorize provider execution.

It does not create provider authority.

It does not combine Provider A and Provider B authority into a shared decision.

## Files

### `association_recorder.py`

MP001 association evidence recorder.

The recorder listens on:

`0.0.0.0:9191`

and accepts provider boundary submissions at:

`POST /boundary`

It also exposes:

`GET /health`

Each recorder session is started with explicit paths for:

- session ID
- provider registry
- MP001 run manifest
- MP001 contract
- output log

The recorder refuses to overwrite an existing log file.

## Session binding

At startup, the recorder hashes and records:

- its own implementation
- the provider registry
- the MP001 run manifest
- the MP001 contract

It writes those hashes into the `SESSION_START` record along with:

- session ID
- host
- registered providers
- local UTC observation
- local monotonic observation

This ties each recorded session to the files used by that recorder instance.

The recorder does not treat those hashes as execution authority.

## Submission capture

For every received boundary submission, the recorder preserves:

- raw received bytes as base64
- SHA-256 of the raw received bytes
- source address
- source port
- local receive sequence
- local UTC receive observation
- local monotonic receive observation
- claimed provider ID
- claimed operation ID
- claimed stage
- claimed boundary key ID
- claimed binding
- claimed boundary value
- claimed authorization ID
- claimed authorization nonce
- claimed denial reason
- signature-verification result
- registry-match result
- duplicate reference when applicable
- unknown top-level or event fields

The recorder returns HTTP 204 after recording the submission.

A 204 response confirms recorder receipt. It does not mean the association authorized or approved provider execution.

## Signature verification

Provider boundary statements use Ed25519.

The recorder verifies the signature over the canonical provider event using the domain separator:

`NUVL-MP-BOUNDARY-v1|`

The provider claimed in the event must exist in the registry.

The event's `key_id` must match the registered key ID for that provider.

The recorder then verifies the boundary signature using that provider's registered boundary public key.

Possible verification outcomes include:

- `ok`
- `bad_sig`
- `unknown_provider`
- `provider_key_mismatch`
- `wrong_algorithm`
- `malformed_json`
- `malformed_envelope`
- verification errors

A valid signature means the recorded event verifies under the registered provider boundary key.

It does not mean the association determined that the provider's policy was correct.

## Duplicate detection

For signature-valid submissions, the recorder derives a hash from the signed event and signature.

The first observed copy is retained as the original.

If the exact same signed provider event is submitted again, the later record receives:

`duplicate_of_seq`

pointing to the first observed copy.

A duplicate can therefore remain cryptographically valid while still being identified as a duplicate observation.

MP001 N04 exercises this behavior.

## Record chain

Each association record contains:

- `record_seq`
- `prev_record_hash`
- `record_hash`

The first record uses an all-zero genesis hash.

Each subsequent record incorporates the prior record hash.

The association log therefore preserves a local append sequence with chained record hashes.

This establishes local recorder ordering.

It does not establish globally synchronized chronology across providers or hosts.

## Session end

On normal shutdown or `KeyboardInterrupt`, the recorder appends a `SESSION_END` record containing:

- session ID
- local UTC observation
- local monotonic observation
- submission count

It then prints the final record hash.

The scored campaign retained that final record hash separately with the evidence.

## `provider_registry.json`

The registry defines the provider identities and boundary keys trusted by the association for MP001.

Registered providers are:

- `PROVIDER_A`
- `PROVIDER_B`

Provider A boundary key ID:

`sha256:e4664ee3b7bb0012fb7d8f763c9df74594d8a6bec8488d97532a5846cc04b6ff`

Provider B boundary key ID:

`sha256:db764408aa319642363057d804f0c2a3d2c7dd22de86ae4a6d6549cb97f60225`

The final registry SHA-256 used for the scored campaign is:

`59d739588427d87313e3434982d943a9c82bad26c3fe3deb7d5488efadb6088d`

The registry maps provider identity to expected boundary key identity and public-key file.

It does not contain provider issuance keys.

It does not confer provider execution authority.

## `trust/`

The `trust/` directory contains the provider boundary public keys used by the association.

It contains:

- `provider_a_public.pem`
- `provider_b_public.pem`

These are verification keys only.

They allow the association to verify signed provider boundary statements.

They do not allow the association to:

- mint Provider A authorization
- mint Provider B authorization
- sign Provider A boundary events
- sign Provider B boundary events
- consume provider authorization
- trigger provider execution

## Separation from provider issuance

The association trusts provider boundary-signing public keys.

Provider authorization issuance uses separate Ed25519 issuance keypairs located in the provider directories.

The association recorder does not require those issuance public keys for MP001 boundary scoring.

This preserves the distinction between:

- provider-issued execution authority
- provider-signed boundary evidence
- association verification of that evidence

## Scored implementation hash

The association recorder used for the scored campaign had SHA-256:

`fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc`

The scored association log, final counts, final record hash, and log hash are retained under:

`../evidence/MP001_SCORED_20261009/`

## Authority boundary

The association can observe that:

- a submission claims a provider identity
- that provider is registered
- the expected boundary key was named
- the signature verifies or fails
- a signed event is a duplicate
- a provider reported `START`, `COMPLETE`, or `DENY`

The association cannot infer from those capabilities that it owns provider execution authority.

It does not:

- issue provider authorization
- decide provider policy
- consume provider authorization
- instruct a provider to execute
- require Provider A to wait for Provider B
- require Provider B to wait for Provider A
- create a joint provider authorization
- turn observation into authority

## Scope

This directory contains the MP001 association implementation and trust material.

It does not by itself establish:

- provider execution
- provider authorization validity at issuance
- intermediary behavior
- physical actuation
- campaign PASS or FAIL status
- global event chronology

Those properties are documented by the corresponding provider, intermediary, configuration, and evidence directories.
