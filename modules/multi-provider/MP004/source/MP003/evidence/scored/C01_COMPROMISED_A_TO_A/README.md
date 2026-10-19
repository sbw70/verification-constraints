# C01 Compromised Provider A Key Used Against Provider A

This directory contains the request, the attacker-minted Provider A authorization, the relay send record, and post-case provider state for MP003 scored case C01.

C01 establishes that the compromised credential used in MP003 is genuine Provider A issuance authority, not a simulated, malformed, or otherwise invalid attacker key.

## Test condition

For MP003, Provider A's real Ed25519 authorization-issuance private key is treated as stolen.

The attacker holds a byte-identical copy:

`attacker/compromised_provider_a_issuance_private.pem`

SHA-256 `37f808b6901f5020fb7b68924217d76f7923d898e44913a6338008d85ac15fd8` — identical to `provider_a/provider_a_issuance_private.pem`.

The attacker used `attacker/mint_compromised_a.py` to mint a fresh authorization for the C01 request. The authorization truthfully identifies itself as:

`provider_id = "PROVIDER_A"`

The request was sent under:

`CTX_MP003_C01`

Per the locked run manifest, only the Provider A authorization header was sent. The Provider B header was absent.

## Contents

- `request.json` — exact request bytes used for the scored C01 submission.
- `provider_a_authorization.json` — attacker-minted Provider A authorization package.
- `provider_a_authorization.json.b64` — encoded authorization transmitted in `X-Provider-A-Authorization`.
- `relay_send_record.txt` — operator send record: local send time, relay endpoint, context, which headers were sent, request hash, and HTTP status.
- `provider_a_execution_after_C01.jsonl`, `provider_a_spent_state_after_C01.json` — Provider A state after C01.
- `provider_b_execution_after_C01.jsonl`, `provider_b_spent_state_after_C01.json` — Provider B state after C01.
- `_post_a/`, `_post_b/` — raw `scp` copies of each provider's live state files taken immediately after the case. The `*_after_C01` files are byte-identical copies of these, renamed to match the B01 naming.

## Scored identifiers

Request bytes:

`{"action":"mp003_test","nonce":"MP003-C01"}`

Request representation:

`df7e42b3cef18610fe16e2c8fb2b55a6b7674b70391d92a7da470fceee1f7005`

Operation ID:

`54791a1682b73664b437a898f811ff010ebf6fafdec734893efd0f4c1b472d58`

Attacker-minted Provider A authorization:

`6e3ce147b1337f74451823a78cef40011378c88e2e4103f2ffcd82845dc7de1a`

Authorization nonce:

`4323797ff618e83c8821ca21fa819294`

Authorization package SHA-256:

`2ed0222f966b2219a11b33cccee2a348e07ae77de63a2284b86b96cbd335f23c`

## Result

**PASS**

The relay returned HTTP `204`.

| Record | Provider | Stage | Reason | Authorization |
|---|---|---|---|---|
| 8 | Provider B | `DENY` | `auth_missing` | none |
| 9 | Provider A | `START` | — | `6e3ce147…` |
| 10 | Provider A | `COMPLETE` | — | `6e3ce147…` |

All three submissions passed association signature verification and registry key matching.

Provider A:

- accepted the attacker-minted authorization;
- durably consumed it;
- emitted signed `START`;
- recorded local execution (`local_execution_seq` 2);
- emitted signed `COMPLETE`.

Provider B:

- received no authorization, as specified by the manifest;
- emitted signed `DENY auth_missing`;
- did not consume, start, execute, or complete anything.

## Provider state verification

Provider state before C01 was re-read over SSH and was byte-identical to the B01 post-case files.

After C01:

- Provider A spent state contains `aac7988b…` (B01) and `6e3ce147…` (C01). Provider A execution log contains 2 records.
- Provider B spent state (`818b07c2…`) and execution log (`1703aad4…`) are byte-identical to their state after B01.

## What C01 establishes

C01 demonstrates that possession of Provider A's issuance private key is sufficient to originate Provider A authority that Provider A accepts and acts on.

This is the expected result. Once a provider's issuance key is compromised, that provider's authority boundary is compromised.

C01 is not a containment result. It is the precondition that gives C02 and C03 their meaning: the key used against Provider B in those cases is proven here to be real Provider A authority.

## What C01 does not establish

C01 does not establish:

- that Provider B rejects Provider A authority (see C02 and C03);
- detection, revocation, or rotation of the compromised key;
- that a compromised Provider A remains trustworthy;
- compromise of Provider A's boundary-signing key or host;
- cross-provider atomicity or globally synchronized chronology.

## Note on local timestamps

Provider-local execution timestamps are local observational evidence only. Host clocks are not synchronized in MP003. For example, Provider A's local execution timestamp for C01 (`2026-10-16T03:20:22.391630Z`) is earlier than the operator's local send time (`2026-10-15 23:20:22.923 -04:00`). No cross-host ordering is inferred from timestamps.

## Related evidence

The scored association log:

`../association.jsonl`

Control case:

`../B01_CONTROL/`

Provider A authority presented to Provider B:

`../C02_PROVIDER_A_AUTH_TO_B/`

Provider B identity claimed under Provider A's key:

`../C03_CLAIM_B_SIGNED_BY_A/`

Attacker tooling and key copy:

`../../../attacker/`

The scored campaign summary:

`../SCORECARD.txt`

Integrity information for the scored evidence set:

`../SHA256SUMS.txt`
