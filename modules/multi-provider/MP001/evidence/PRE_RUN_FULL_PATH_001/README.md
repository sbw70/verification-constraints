# Pre-Run Full-Path Smoke Test

This directory contains the retained artifacts from `PRE_RUN_FULL_PATH_001`, a pre-run end-to-end smoke test performed before the MP001 scored campaign.

Its purpose was to verify that the complete deployed path was functioning together before scored execution began:

requester → NUVL intermediary → Provider A / Provider B → association

This run was a setup and integration check. It is **not part of the scored MP001 campaign**.

## Request

`request.json` contains the raw request body used for the smoke test.

The request was:

`{"action":"mp001_smoke","nonce":"PRE_RUN_FULL_PATH_001"}`

Its request representation was:

`68c2719a17b74a0091b2fb4133cee701ffc4e1ede98ab59ea1501c5787a30355`

The request representation is the SHA-256 digest of the exact raw request bytes.

The verification context was:

`CTX_ALPHA`

## Provider A authorization

`provider_a_auth.json` contains the Provider A authorization package issued for the smoke-test request.

`provider_a_auth.json.b64` contains its base64url transport representation.

Provider A authorization ID:

`022953157598699dffc95c4bf8e37be1f093280fcd804b0ec59931f833b1857d`

Provider A authorization nonce:

`c06f6b67720091a8af7df269e3210d2a`

The authorization was issued specifically by Provider A and did not confer authority on Provider B.

## Provider B authorization

`provider_b_auth.json` contains the separate Provider B authorization package issued for the same request representation and verification context.

`provider_b_auth.json.b64` contains its base64url transport representation.

Provider B authorization ID:

`fe7c5898bc657b1a308995b500a3e78a21eb278a578e88edd371254281e84f43`

Provider B authorization nonce:

`8c236ed1a58d2c8535b8ae0a7100f801`

The Provider B authorization was independently issued and was distinct from the Provider A authorization.

## Provider-local execution evidence

`provider_a_execution.jsonl` contains one Provider A local execution record.

`provider_b_execution.jsonl` contains one Provider B local execution record.

Both providers independently derived the same correlation operation ID:

`8f7ad52a6a8ee3bfdbb58f933160416acd692e6c54e4d016826efcdadb170ac2`

The shared operation ID is correlation material. It does not combine or transfer authority between providers.

Each provider recorded its own execution under its own authorization ID.

## Provider-local spent state

`provider_a_spent_state_POST.json` contains Provider A's post-run spent state.

It records the Provider A authorization as consumed.

`provider_b_spent_state_POST.json` contains Provider B's post-run spent state.

It records the separate Provider B authorization as consumed.

Spent state remained provider-local.

Provider A did not depend on Provider B's spent state, and Provider B did not depend on Provider A's spent state.

## Association evidence

`association.jsonl` contains the association recorder session for this smoke test.

The session ID is:

`PRE_RUN_FULL_PATH_001`

The association retained four provider boundary submissions:

- Provider A `START`
- Provider B `START`
- Provider A `COMPLETE`
- Provider B `COMPLETE`

All four submissions:

- matched registered providers
- carried the expected provider boundary key identity
- passed Ed25519 boundary-signature verification
- were retained in the association record chain

The session ended with:

`submission_count: 4`

The association observed and verified these provider statements. It did not authorize either provider's execution.

## Correlation

All four signed provider boundary events carried the same operation ID and binding.

Binding:

`624ef1a70c9bed344f6830995bd1a109b96854d9723f35127df78892fffa9aac`

Operation ID:

`8f7ad52a6a8ee3bfdbb58f933160416acd692e6c54e4d016826efcdadb170ac2`

Provider A and Provider B nevertheless retained different:

- authorization IDs
- authorization nonces
- issuance keys
- boundary-signing keys
- spent state
- local execution records

The common correlation values therefore did not create shared provider authority.

## Contract and recorder state

The association session records the following frozen components:

MP001 contract SHA-256:

`7db3a52907af48d2524995e15b947600e534555758338cc38ce2594ff633ff4e`

MP001 run manifest SHA-256:

`37f2cea056bce67c209204467fa574c1d83307ec7e6df59815fb58eae20acf54`

Association recorder SHA-256:

`fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc`

Provider registry SHA-256:

`59d739588427d87313e3434982d943a9c82bad26c3fe3deb7d5488efadb6088d`

The normative protocol rules are defined in:

`../../configs/MP001_CONTRACT.md`

The scored campaign definition is retained in:

`../../configs/MP001_RUN_MANIFEST.json`

## What this smoke test established

`PRE_RUN_FULL_PATH_001` verified before scoring that the deployed components could complete the intended full path with:

- a real request entering the intermediary
- separate Provider A and Provider B authorizations
- independent provider authorization verification
- provider-local authorization consumption
- provider-local execution
- signed provider `START` and `COMPLETE` boundary statements
- association receipt and signature verification of both providers' statements

This provided an end-to-end integration check before the scored evidence set was created.

## Limits

This directory does not establish a scored MP001 result.

It does not test:

- corrupted authorization
- hostile relay mutation
- forged boundary submission
- duplicate boundary submission
- provider unavailability
- authorization replay
- crash behavior
- concurrent contention
- power-loss persistence
- physical actuation
- independent physical witness confirmation

Those properties, where applicable to MP001, were tested separately in the scored campaign retained under:

`../MP001_SCORED_20261009/`

This directory should therefore be read as pre-run validation evidence, not as a substitute for the scored campaign.
