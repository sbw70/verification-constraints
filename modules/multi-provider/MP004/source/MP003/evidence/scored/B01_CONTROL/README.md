# B01 Control

This directory contains the request, provider-specific authorization artifacts, and post-case provider state for the MP003 scored control case.

B01 establishes the expected behavior when both independent providers receive their own legitimate authorization for the same operation, before any compromised-key case is run.

## Test condition

Both providers received the same request representation under:

`CTX_MP003_B01`

Each provider was given a fresh legitimate authorization minted by its own provider-side issuance key:

- Provider A authorization minted with `provider_a/mint_authorization_a.py`.
- Provider B authorization minted with `provider_b/mint_authorization_b.py`.

No attacker material was used in B01.

## Contents

- `request.json` — exact request bytes used for the scored B01 submission.
- `provider_a_authorization.json` — Provider A authorization package.
- `provider_a_authorization.json.b64` — encoded Provider A authorization transmitted in `X-Provider-A-Authorization`.
- `provider_b_authorization.json` — Provider B authorization package.
- `provider_b_authorization.json.b64` — encoded Provider B authorization transmitted in `X-Provider-B-Authorization`.
- `provider_a_execution_after_B01.jsonl` — Provider A execution log after B01.
- `provider_a_spent_state_after_B01.json` — Provider A spent state after B01.
- `provider_b_execution_after_B01.jsonl` — Provider B execution log after B01.
- `provider_b_spent_state_after_B01.json` — Provider B spent state after B01.

## Scored identifiers

Request bytes:

`{"action":"mp003_test","nonce":"MP003-B01"}`

Request representation:

`882a7d207f5b1ab04754204d7cef48050a22ac6dc718d407313fe6d28b3187a3`

Operation ID (derived independently by each provider):

`d54eb3b904fd9c9a619dc59130ea48c9e193845c2c4fdc0eab17e56c2e0f2d7e`

Provider A authorization:

`aac7988b08e14b382105470d20c9cc3b15abf50ff288cba615cb962e5d12cfc1`

Provider B authorization:

`92a84e45db900b5ce25807cb8d16267657a922f29ded3a11908f6ef7d8c1771b`

## Result

**PASS**

The association recorded valid signed boundary events for both providers:

| Record | Provider | Stage | Authorization |
|---|---|---|---|
| 4 | Provider A | `START` | `aac7988b…` |
| 5 | Provider B | `START` | `92a84e45…` |
| 6 | Provider A | `COMPLETE` | `aac7988b…` |
| 7 | Provider B | `COMPLETE` | `92a84e45…` |

All four submissions passed association signature verification and registry key matching.

The post-case provider state shows exactly one execution and one consumed authorization at each provider, each matching that provider's own B01 authorization.

## Retained harness misfire before the scored attempt

The first B01 transmission in this session did not deliver usable authorizations.

The sending harness referenced `provider_a_authorization.b64` and `provider_b_authorization.b64`, but the mint utilities write sibling files named `provider_a_authorization.json.b64` and `provider_b_authorization.json.b64`. The values forwarded in the authorization headers were non-empty but could not be decoded as authorization packages.

Both providers correctly emitted signed:

`DENY auth_malformed`

These are association records 2 and 3. They carry the same operation ID as the scored B01 attempt because the request bytes and context were identical. Neither record names an authorization, and nothing was consumed or executed.

The operator notes originally described these headers as empty. That description was later corrected: the provider code returns `auth_missing` for an empty value, so the observed `auth_malformed` shows the values were non-empty and undecodable. The original note is retained alongside the correction.

This is a harness/precondition misfire. The intended B01 condition was not reached on that attempt. It is not a B01 failure and not an authority-boundary failure. The records remain in the hash-chained association log and are not scored.

## Evidence gaps

- The relay returns HTTP `204` for every accepted request and has no response body. The HTTP status of the scored B01 send was not retained in a file, unlike C01 through B02, which each include `relay_send_record.txt`.
- The requester host for the scored B01 send was not recorded in a file. All later scored cases were sent from the OmniBook operator host.
- The B01 post-case provider state was captured before the R2 per-case `scp` procedure was adopted, so there are no raw `_post_a/` or `_post_b/` drops here. The live provider state was later re-read over SSH immediately before C01 and was byte-identical to these files.

## What B01 establishes

B01 is the control for MP003.

It shows that, with the MP003 deployment in place, both providers independently validate their own legitimate authorization and execute the same operation.

This is the baseline against which the compromised-key cases are compared. The relay, association recorder, provider runtimes, and authorization format were not changed between B01 and the attack cases.

## What B01 does not establish

B01 does not by itself demonstrate:

- containment of a compromised Provider A issuance key;
- cross-provider atomicity;
- globally synchronized event ordering;
- implementation diversity;
- crash-window, concurrent-use, or power-loss behavior;
- physical actuation or independent hardware-witness evidence.

## Related evidence

The scored association log:

`../association.jsonl`

The compromised-key cases:

`../C01_COMPROMISED_A_TO_A/`

`../C02_PROVIDER_A_AUTH_TO_B/`

`../C03_CLAIM_B_SIGNED_BY_A/`

Post-attack Provider B health:

`../B02_POST_ATTACK_B_HEALTH/`

The scored campaign summary:

`../SCORECARD.txt`

Integrity information for the scored evidence set:

`../SHA256SUMS.txt`
