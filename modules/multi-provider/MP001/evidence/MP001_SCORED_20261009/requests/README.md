# Scored Request Inputs

This directory contains the raw request bodies used during the MP001 scored campaign.

These files are request inputs only. Provider-issued authorization packages are retained separately in the sibling `auth_a/` and `auth_b/` directories.

## Baseline requests

`B01.json` through `B10.json` are the ten baseline request bodies.

Each request uses the same action with a unique nonce:

`{"action":"mp001_test","nonce":"MP001-B01"}`

The raw bytes of each request are significant. MP001 defines the request representation as the SHA-256 hash of the raw request bytes.

The ten baseline request hashes are recorded in:

`../baseline_request_hashes.txt`

The baseline request set is also retained as:

`../baseline_requests.tar`

## Negative-test requests

The directory also contains request bodies associated with the scored negative cases:

- `N01.json`
- `N02.json`
- `N02_TAMPERED.json`
- `N04.json`
- `N05.json`
- `N06.json`

Not every negative case required a distinct request mutation. Some tests altered authorization material, provider availability, boundary submissions, or replay behavior while retaining an otherwise ordinary request body.

### `N01.json`

Request body used for the corrupted Provider A authorization-signature case.

The request itself was not the invalid component. Provider A received a corrupted authorization signature while Provider B received intact authorization.

### `N02.json`

Original request body associated with the hostile-relay mutation case.

### `N02_TAMPERED.json`

Changed request body used to construct the hostile-relay artifacts for N02.

The relay-side attack changed the request representation and recomputed the public mechanical binding while retaining the original provider authorizations.

Because those authorizations remained bound to the original request representation, both providers denied the altered artifacts with `auth_request_mismatch`.

### `N04.json`

Request body used for the valid-execution and exact-boundary-replay case.

The replayed object in N04 was not this request file. After valid execution, an exact previously accepted Provider A `COMPLETE` boundary submission was sent to the association again.

### `N05.json`

Request body associated with the provider-unavailability case.

The initial N05 attempt did not satisfy the intended Provider B unavailable precondition and was retained as a misfire.

The scored retry used fresh provider authorizations after Provider B unavailability was verified.

### `N06.json`

Request body used for the sequential authorization-replay case.

The same request and intact provider authorization pair were submitted twice.

The first submission executed normally. The second was denied by both providers because the corresponding authorizations had already been consumed.

## Encoding significance

The request representation used by MP001 is:

`SHA-256(raw request bytes)`

This means changes to the raw file can change the request representation even when the decoded JSON appears semantically equivalent.

Examples include:

- whitespace changes
- line-ending changes
- field-order changes
- added or removed bytes
- changed nonce or action values

The normative encoding, request-representation, binding, and authorization rules are defined in:

`../../../configs/MP001_CONTRACT.md`

## Scope

This directory establishes the request inputs retained for the MP001 scored campaign.

It does not by itself establish:

- provider authorization validity
- provider execution
- authorization consumption
- intermediary behavior
- association verification
- campaign PASS or FAIL status

Those properties are documented by the corresponding authorization artifacts, requester logs, provider-local state, association records, and campaign scorecard elsewhere in `MP001_SCORED_20261009/`.
