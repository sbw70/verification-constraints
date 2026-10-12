# MP001 Configuration

This directory contains the fixed protocol contract and scored-run manifest for MP001.

These files define how MP001 messages, authorizations, provider boundary statements, and scored cases are interpreted.

They are configuration and test-definition artifacts.

They are not execution evidence.

## Files

### `MP001_CONTRACT.md`

Normative wire and cryptographic contract for MP001.

The contract defines:

- canonical JSON encoding
- request representation
- verification context
- mechanical binding
- operation ID derivation
- provider authorization structure
- authorization ID derivation
- Ed25519 authorization signatures
- requester-to-NUVL authorization transport
- NUVL-to-provider artifact structure
- provider validation order
- single-use authorization behavior
- provider boundary-event format
- provider boundary signatures
- boundary key IDs
- `START`, `COMPLETE`, and `DENY` semantics
- provider-local execution evidence
- association semantics
- hostile-relay controls
- authority boundaries

The contract fixes the representation used by the MP001 implementation and evidence.

Its retained SHA-256 is:

`7db3a52907af48d2524995e15b947600e534555758338cc38ce2594ff633ff4e`

## Core authority rule

The contract preserves provider-scoped execution authority.

Provider A and Provider B issue separate authorizations.

An authorization issued by Provider A does not authorize Provider B.

An authorization issued by Provider B does not authorize Provider A.

The NUVL intermediary transports provider-specific authorization but does not:

- validate it
- originate it
- enlarge it
- interpret it as provider policy
- substitute one provider's authorization for another

The association records and verifies provider statements but does not authorize provider execution.

## Request representation

The requester supplies opaque request-body bytes.

The MP001 request representation is:

`SHA-256(raw_request_body)`

The exact bytes therefore matter.

The NUVL intermediary does not need to interpret the request body to derive its representation.

## Verification context

The requester supplies:

`X-Verification-Context`

For the scored MP001 campaign, the fixed context was:

`CTX_ALPHA`

The intermediary transports the context.

Each provider independently determines whether the context matches its own authorization.

## Mechanical binding

The intermediary computes:

`SHA-256("NUVL_BIND_V1|<request_repr>|<verification_context>")`

Each provider independently recomputes the same value.

The binding is non-secret.

It is not provider authority.

A component capable of recomputing the binding does not thereby gain the ability to issue a new valid provider authorization.

## Operation ID

Each provider independently derives an operation ID from its locally recomputed expected binding.

The operation ID exists for correlation.

It does not:

- create authority
- merge provider state
- establish provider agreement
- make one provider dependent on another
- authorize execution

Provider A and Provider B can therefore derive the same correlation identifier while retaining independent authorization and execution authority.

## Provider authorization

Each provider authorization is bound to:

- provider identity
- request representation
- verification context
- provider-generated nonce
- authorization version

The authorization ID is derived from the canonical authorization core using a domain-separated SHA-256 construction.

The authorization object is then signed using the issuing provider's Ed25519 issuance key.

Provider issuance keys are separate from provider boundary-signing keys.

## Provider validation order

The contract fixes the provider validation sequence.

A provider independently checks:

1. relay artifact parsing
2. mechanical binding
3. authorization presence
4. authorization encoding and structure
5. provider identity
6. authorization ID
7. Ed25519 issuance signature
8. request representation
9. verification context
10. prior authorization consumption

Only after those checks pass does the provider durably consume the authorization.

Only after durable consumption does it emit `START`.

The provider then performs its local execution step, records local execution evidence, and emits `COMPLETE`.

## Single use

MP001 provider authorizations are single-use.

Spent state remains local to each provider and is keyed by `authorization_id`.

A later intact replay of an already consumed authorization is expected to produce:

`DENY auth_spent`

MP001 tests ordinary sequential replay.

The contract explicitly does not use MP001 to re-test:

- crash-window replay persistence
- concurrent replay
- power-loss replay persistence

## Boundary statements

Each provider signs its own boundary events using a provider-specific Ed25519 boundary keypair.

Supported stages are:

- `START`
- `COMPLETE`
- `DENY`

The signed event binds together:

- provider identity
- operation identity
- mechanical binding
- boundary key identity
- stage
- boundary value
- authorization identity
- authorization nonce
- denial reason when applicable

The association verifies these signed provider statements against the registered provider boundary keys.

Verification does not make the association authoritative over provider execution.

## `MP001_RUN_MANIFEST.json`

Predefined scored-run manifest for MP001.

The manifest identifies:

- test series
- campaign purpose
- contract hash
- association recorder hash
- provider registry hash
- expected providers
- verification context
- explicit claim boundaries
- baseline cases
- negative cases
- expected observations for each case

The retained manifest SHA-256 is:

`37f2cea056bce67c209204467fa574c1d83307ec7e6df59815fb58eae20acf54`

## Expected providers

The manifest fixes the scored provider set as:

- `PROVIDER_A`
- `PROVIDER_B`

The scored campaign does not claim a third provider.

## Claim boundaries

The run manifest explicitly sets the following claims to false:

- physical execution witness
- cross-host clock authority
- implementation diversity
- crash-window replay persistence
- concurrent replay
- power-loss replay persistence

These exclusions are part of the test definition.

They are not omissions to be inferred away from the results.

## Baseline cases

The manifest defines ten baseline cases:

- B01
- B02
- B03
- B04
- B05
- B06
- B07
- B08
- B09
- B10

Each baseline case uses a distinct request nonce.

Expected behavior for both providers is:

- `START`
- local `EXECUTED`
- `COMPLETE`

The expected association result is two verified provider lifecycles.

## Negative cases

The manifest defines six negative cases.

### N01 — bad Provider A authorization

The Provider A authorization signature is corrupted while the Provider B authorization remains intact.

Expected:

- Provider A `DENY`
- Provider A reason `auth_bad_sig`
- no Provider A execution
- Provider B independently reaches `START`, `EXECUTED`, and `COMPLETE`

### N02 — hostile relay

The relay substitutes a different request representation and recomputes the non-secret mechanical binding while retaining the original provider authorizations.

Expected:

- Provider A `DENY auth_request_mismatch`
- Provider B `DENY auth_request_mismatch`
- no provider execution

### N03 — forged boundary

A boundary package claiming Provider A is submitted directly to the association with an invalid boundary signature.

Expected:

- association signature validation false
- verification code `bad_sig`
- no verified provider lifecycle
- no provider execution required for the case

### N04 — duplicate boundary

A valid distributed execution is completed, then the exact raw Provider A `COMPLETE` package is submitted to the association again.

Expected:

- both providers complete normally
- duplicate remains signature-valid
- association detects the duplicate
- the duplicate does not create a third distinct provider lifecycle

### N05 — one provider unavailable

Provider B is unavailable while Provider A remains available.

Expected:

- Provider A independently reaches `START`, `EXECUTED`, and `COMPLETE`
- no Provider B lifecycle is observed
- only one verified provider lifecycle is present
- two-provider completion is not observed

The retained scored evidence records an initial N05 misfire followed by a valid retry. That execution history is documented in the evidence directory rather than altered here.

### N06 — authorization replay

The same request and same intact Provider A and Provider B authorizations are submitted twice sequentially.

Expected first submission:

- Provider A `START`, `EXECUTED`, `COMPLETE`
- Provider B `START`, `EXECUTED`, `COMPLETE`

Expected second submission:

- Provider A `DENY auth_spent`
- Provider B `DENY auth_spent`
- no second execution

## Configuration versus evidence

The files in this directory define what MP001 means and what the campaign expected.

They do not establish that those expectations were met.

Observed behavior is retained under:

`../evidence/`

The scored results are retained under:

`../evidence/MP001_SCORED_20261009/`

The run manifest should therefore be read as preregistered test intent and expected behavior, not as proof of the result.

## Scope

This directory defines the MP001 protocol and scored campaign boundaries.

It does not by itself establish:

- successful provider execution
- association verification
- hostile-relay rejection
- replay rejection
- provider unavailability behavior
- campaign PASS or FAIL status

Those claims require the retained evidence generated during execution.
