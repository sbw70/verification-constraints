# B02 Post-Attack Provider B Health

This directory contains the request, the legitimate Provider B authorization, the relay send record, and post-case provider state for MP003 scored case B02.

B02 checks that the rejected cross-provider attempts in C01 through C03 did not consume, replace, or otherwise corrupt Provider B's legitimate execution authority.

## Test condition

After C01, C02, and C03, Provider B was given a fresh legitimate authorization minted with Provider B's own issuance key (`provider_b/mint_authorization_b.py`).

No attacker material was used in B02.

The request was sent under:

`CTX_MP003_B02`

Per the locked run manifest:

- `X-Provider-A-Authorization` — absent.
- `X-Provider-B-Authorization` — the legitimate Provider B authorization.

## Contents

- `request.json` — exact request bytes used for the scored B02 submission.
- `provider_b_authorization.json` — legitimate Provider B authorization package.
- `provider_b_authorization.json.b64` — encoded authorization transmitted in `X-Provider-B-Authorization`.
- `relay_send_record.txt` — operator send record, including which headers were sent and the HTTP status.
- `provider_a_execution_after_B02.jsonl`, `provider_a_spent_state_after_B02.json` — Provider A state after B02.
- `provider_b_execution_after_B02.jsonl`, `provider_b_spent_state_after_B02.json` — Provider B state after B02.
- `_post_a/`, `_post_b/` — raw `scp` copies of each provider's live state files taken immediately after the case. The `*_after_B02` files are byte-identical copies of these, and the same files were copied to `../final_provider_a/` and `../final_provider_b/`.

## Scored identifiers

Request bytes:

`{"action":"mp003_test","nonce":"MP003-B02"}`

Request representation:

`e7eed63cc0d960bdac1abe76076a05975e437cdb38c279db1a81019a1a64003f`

Operation ID:

`b4b827664deba623158a0f6e13816d95c34bdfbcad23d5076d707a770d187b9a`

Provider B authorization:

`8f0e91c818c7bce6e3252244fc59fa404a808bfe4c2da4e1547aa597f75134a1`

Authorization nonce:

`8d45b974433702ff3fb45abffcd799c4`

Authorization package SHA-256:

`915298a336bef0c16b4dbafd9d53f1898e9e0f9a4bf8dadad52aa5f28fd2167b`

## Result

**PASS**

The relay returned HTTP `204`.

| Record | Provider | Stage | Reason | Authorization |
|---|---|---|---|---|
| 16 | Provider A | `DENY` | `auth_missing` | none |
| 17 | Provider B | `START` | — | `8f0e91c8…` |
| 18 | Provider B | `COMPLETE` | — | `8f0e91c8…` |

All three submissions passed association signature verification and registry key matching.

Provider B:

- accepted its legitimate authorization;
- durably consumed it;
- emitted signed `START`;
- recorded local execution (`local_execution_seq` 2);
- emitted signed `COMPLETE`.

Provider A:

- received no authorization, as specified by the manifest;
- emitted signed `DENY auth_missing`.

## Provider state verification

After B02:

- Provider B spent state contains exactly two authorizations: `92a84e45…` (B01) and `8f0e91c8…` (B02). Provider B execution log contains 2 records.
- Provider A spent state (`539ec627…`) and execution log (`f5cc5025…`) are byte-identical to their state after C02.

Provider B's `local_execution_seq` advanced directly from 1 (B01) to 2 (B02). No Provider B execution occurred during C01, C02, or C03. The Provider B console transcript in `../operator_transcripts/provider_b_console.txt` shows the same sequence.

## What B02 establishes

B02 demonstrates that, after Provider A's issuance key was used against Provider B in two different ways, Provider B's own legitimate authorization path still worked normally.

The rejected attempts did not:

- consume a Provider B authorization;
- leave Provider B unable to execute;
- alter Provider B's durable state beyond what B01 and B02 themselves recorded.

## What B02 does not establish

B02 does not establish:

- long-term or post-restart behavior of Provider B state;
- behavior under repeated or high-volume cross-provider attempts;
- availability or denial-of-service resistance;
- recovery from compromise of any Provider B key or host;
- globally synchronized chronology.

## Related evidence

The scored association log:

`../association.jsonl`

Control case:

`../B01_CONTROL/`

The compromised-key cases:

`../C01_COMPROMISED_A_TO_A/`

`../C02_PROVIDER_A_AUTH_TO_B/`

`../C03_CLAIM_B_SIGNED_BY_A/`

Final provider state:

`../final_provider_a/`

`../final_provider_b/`

The scored campaign summary:

`../SCORECARD.txt`

Integrity information for the scored evidence set:

`../SHA256SUMS.txt`
