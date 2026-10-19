# C03 Provider B Identity Claimed Under Provider A Key

This directory contains the request, the forged authorization, the relay send record, and post-case provider state for MP003 scored case C03.

C03 tests whether a holder of Provider A's compromised issuance key can become Provider B by relabeling: an authorization that claims to be for Provider B, but is signed with Provider A's issuance key.

## Test condition

The attacker used `attacker/mint_forged_b_with_a_key.py` to construct a fresh authorization for the C03 request.

That script is identical to `attacker/mint_compromised_a.py` except for one line: it sets

`provider_id = "PROVIDER_B"`

It signs with the same compromised Provider A issuance private key.

The authorization ID is correctly derived from the forged signed object, so the forgery passes Provider B's identity check (step 6) and authorization-ID check (step 7) and reaches issuance-signature verification (step 8). See contract §11.

The request was sent under:

`CTX_MP003_C03`

Per the locked run manifest:

- `X-Provider-A-Authorization` — absent.
- `X-Provider-B-Authorization` — the forged authorization.

## Contents

- `request.json` — exact request bytes used for the scored C03 submission.
- `forged_provider_b_claim_signed_by_a.json` — forged authorization package claiming `PROVIDER_B`, signed with the compromised Provider A issuance key.
- `forged_provider_b_claim_signed_by_a.json.b64` — encoded forgery transmitted in `X-Provider-B-Authorization`.
- `relay_send_record.txt` — operator send record, including which headers were sent and the HTTP status.
- `provider_a_execution_after_C03.jsonl`, `provider_a_spent_state_after_C03.json` — Provider A state after C03.
- `provider_b_execution_after_C03.jsonl`, `provider_b_spent_state_after_C03.json` — Provider B state after C03.
- `_post_a/`, `_post_b/` — raw `scp` copies of each provider's live state files taken immediately after the case. The `*_after_C03` files are byte-identical copies of these.

## Scored identifiers

Request bytes:

`{"action":"mp003_test","nonce":"MP003-C03"}`

Request representation:

`ec26c89a462ebfbb0ad722ca22df73cf9e8a9b92544bf1e4703cad18f217c6a9`

Operation ID:

`312439e34530f05c22ee33efed6dfe7abad16aebd13a7b4f505284ffe673728b`

Forged authorization (claims `PROVIDER_B`):

`11e016ab2b09c0cb8a1a5349974b9580ea64580d809ee4f76f54e5e6bab0c902`

Authorization nonce:

`a63f6f615167488fe040c65d44c69606`

Forged package SHA-256:

`e42f3ab66287e7440c8b478f186c6016eedab9b7f65747326d53960ebfc98714`

## Result

**PASS**

The relay returned HTTP `204`.

| Record | Provider | Stage | Reason | Authorization |
|---|---|---|---|---|
| 14 | Provider B | `DENY` | `auth_bad_sig` | `11e016ab…` |
| 15 | Provider A | `DENY` | `auth_missing` | none |

Both submissions passed association signature verification and registry key matching.

Provider B:

- accepted the provider identity field (`PROVIDER_B`);
- recomputed the authorization ID and found it correct;
- verified the issuance signature against Provider B's issuance public key, and it failed;
- emitted signed `DENY auth_bad_sig`, naming the forged authorization ID and nonce;
- did not consume, start, execute, or complete anything.

Provider A:

- received no authorization, as specified by the manifest;
- emitted signed `DENY auth_missing`.

Neither provider emitted `START` or `COMPLETE` for this operation.

## Offline verification of the forgery

The forged package was checked offline against the published public keys in this module:

| Check | Result |
|---|---|
| Authorization ID correctly derived from the forged core | true |
| Signature verifies under `provider_a/provider_a_issuance_public.pem` | **valid** |
| Signature verifies under `provider_b/provider_b_issuance_public.pem` | **invalid** |

This confirms the forgery was a genuine Provider A signature over a Provider B claim, and that the `auth_bad_sig` result is the issuance-signature check failing for the right reason, not a malformed or mis-derived package.

## Provider state verification

After C03:

- Provider A spent state (`539ec627…`) and execution log (`f5cc5025…`) are byte-identical to their state after C02.
- Provider B spent state (`818b07c2…`) and execution log (`1703aad4…`) are byte-identical to their state after B01.
- `11e016ab…` does not appear in Provider B's spent state.

The Provider B negatives above were checked against Provider B's own state files, not inferred from the `DENY` event.

## What C03 establishes

C03 demonstrates that changing the claimed provider identity does not convert Provider A signing authority into Provider B signing authority.

Provider B decides what counts as Provider B authority by verifying against its own issuance key. A holder of Provider A's compromised issuance key can write `PROVIDER_B` into an authorization but cannot produce a signature that validates under Provider B's key.

Together with C02:

- C02 — correctly signed Provider A authority is still Provider A authority, and is refused at Provider B on scope.
- C03 — relabeling Provider A authority as Provider B is refused at Provider B on signature.

## What C03 does not establish

C03 does not establish:

- resistance to compromise of Provider B's issuance key, boundary-signing key, or host;
- resistance to compromise of Provider A's boundary-signing key;
- detection, revocation, or rotation of the compromised Provider A key;
- general cryptographic properties of Ed25519 beyond the tested verification path;
- globally synchronized chronology.

## Related evidence

The scored association log:

`../association.jsonl`

Compromised key proven valid at Provider A:

`../C01_COMPROMISED_A_TO_A/`

Provider A authority presented to Provider B:

`../C02_PROVIDER_A_AUTH_TO_B/`

Post-attack Provider B health:

`../B02_POST_ATTACK_B_HEALTH/`

Attacker tooling:

`../../../attacker/`

The scored campaign summary:

`../SCORECARD.txt`

Integrity information for the scored evidence set:

`../SHA256SUMS.txt`
