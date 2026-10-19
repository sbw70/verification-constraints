# C02 Provider A Authority Presented to Provider B

This directory contains the request, the attacker-minted Provider A authorization, the relay send record, and post-case provider state for MP003 scored case C02.

C02 tests provider scope directly: a fully valid Provider A authorization, produced with the compromised Provider A issuance key, is presented to Provider B.

## Test condition

The attacker used the compromised Provider A issuance key (`attacker/mint_compromised_a.py`) to mint a fresh authorization for the C02 request.

The authorization is genuine Provider A authority. It identifies itself as:

`provider_id = "PROVIDER_A"`

and is correctly signed by Provider A's issuance key.

The request was sent under:

`CTX_MP003_C02`

Per the locked run manifest, the same authorization value was placed in both relay headers:

- `X-Provider-A-Authorization` — the Provider A authorization.
- `X-Provider-B-Authorization` — the same Provider A authorization.

The relay forwards each header to its corresponding provider without decoding or verifying it.

## Contents

- `request.json` — exact request bytes used for the scored C02 submission.
- `provider_a_authorization.json` — attacker-minted Provider A authorization package.
- `provider_a_authorization.json.b64` — encoded authorization transmitted in both headers.
- `relay_send_record.txt` — operator send record, including which file was placed in each header and the HTTP status.
- `provider_a_execution_after_C02.jsonl`, `provider_a_spent_state_after_C02.json` — Provider A state after C02.
- `provider_b_execution_after_C02.jsonl`, `provider_b_spent_state_after_C02.json` — Provider B state after C02.
- `_post_a/`, `_post_b/` — raw `scp` copies of each provider's live state files taken immediately after the case. The `*_after_C02` files are byte-identical copies of these.

## Scored identifiers

Request bytes:

`{"action":"mp003_test","nonce":"MP003-C02"}`

Request representation:

`31d07e2a0439fb1b178b55a392472e4bf228c62dbea23958dc3b635f7558b5cb`

Operation ID:

`7632943dc48cc26846bcd85a32a71f2d5f928b88a8bbe0cd939a5980caf9ef85`

Attacker-minted Provider A authorization (sent to both providers):

`0e2ed472caeda2781354e5545f870f70d00910a49019e230e9d7d09edfcb1689`

Authorization nonce:

`c49f7f885902cd61fa594fb9f9e8824c`

Authorization package SHA-256:

`c98c44faefe52a3ab30b7bebed2a50a55b629f7619b8ff15f42509fc71f5edde`

## Result

**PASS**

The relay returned HTTP `204`.

| Record | Provider | Stage | Reason | Authorization |
|---|---|---|---|---|
| 11 | Provider B | `DENY` | `auth_provider_mismatch` | `0e2ed472…` |
| 12 | Provider A | `START` | — | `0e2ed472…` |
| 13 | Provider A | `COMPLETE` | — | `0e2ed472…` |

All three submissions passed association signature verification and registry key matching.

Provider B:

- decoded the authorization package;
- found `provider_id = "PROVIDER_A"`, which does not equal its own identity;
- emitted signed `DENY auth_provider_mismatch`, naming the refused authorization ID and nonce;
- did not consume the authorization;
- did not emit `START`;
- did not record execution;
- did not emit `COMPLETE`.

Provider A:

- accepted the same authorization as valid Provider A authority;
- durably consumed it;
- emitted signed `START`;
- recorded local execution (`local_execution_seq` 3);
- emitted signed `COMPLETE`.

## Provider state verification

After C02:

- Provider A spent state contains three authorizations: `aac7988b…` (B01), `6e3ce147…` (C01), `0e2ed472…` (C02). Provider A execution log contains 3 records.
- Provider B spent state (`818b07c2…`) and execution log (`1703aad4…`) are byte-identical to their state after B01.
- `0e2ed472…` does not appear in Provider B's spent state.

The Provider B negatives above were checked against Provider B's own state files, not inferred from the `DENY` event.

## Where in validation the denial occurred

Provider B's validation order (contract §11) checks provider identity before recomputing the authorization ID or verifying the issuance signature.

C02 was therefore rejected on scope. Provider B did not need to attempt cryptographic verification of a Provider A signature: an authorization addressed to Provider A is not Provider B authority, regardless of whether its signature is valid.

C03 covers the complementary case, where the provider identity field is changed to `PROVIDER_B` so that the request reaches Provider B's signature check.

## What C02 establishes

C02 demonstrates that genuine, correctly signed Provider A authority, including authority produced with a compromised Provider A issuance key, is not accepted as Provider B authority.

In the same operation, the identical authorization was executed by Provider A and refused by Provider B. The compromise affected the provider it belonged to and did not cross into the other provider's execution boundary.

The relay transported the same value to both providers and did not convert it. The association recorded both outcomes and did not authorize either.

## What C02 does not establish

C02 does not establish:

- that relabeling the provider identity is also refused (see C03);
- detection, revocation, or rotation of the compromised Provider A key;
- compromise of any Provider B key, the Provider B host, or Provider A's boundary-signing key;
- cross-provider atomicity: Provider A executed while Provider B denied, as designed;
- globally synchronized chronology.

## Related evidence

The scored association log:

`../association.jsonl`

Compromised key proven valid at Provider A:

`../C01_COMPROMISED_A_TO_A/`

Provider B identity claimed under Provider A's key:

`../C03_CLAIM_B_SIGNED_BY_A/`

Post-attack Provider B health:

`../B02_POST_ATTACK_B_HEALTH/`

The scored campaign summary:

`../SCORECARD.txt`

Integrity information for the scored evidence set:

`../SHA256SUMS.txt`
