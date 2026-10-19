# MP003 Results

## Result

MP003 passed all five scored cases.

The test demonstrates that compromise of Provider A's authorization-issuance key, in the tested implementation, produced valid Provider A authority but did not produce Provider B execution authority.

The scored campaign contained:

- **B01_CONTROL** — both providers execute their own legitimate authorization.
- **C01_COMPROMISED_A_TO_A** — the compromised Provider A key produces authority Provider A accepts.
- **C02_PROVIDER_A_AUTH_TO_B** — valid Provider A authority presented to Provider B.
- **C03_CLAIM_B_SIGNED_BY_A** — an authorization claiming Provider B, signed with Provider A's key.
- **B02_POST_ATTACK_B_HEALTH** — Provider B's legitimate authority after the attack cases.

The observed result was:

**the compromise stayed inside Provider A's authority boundary.**

Provider A accepted and executed authority minted with its compromised key, as expected.

Provider B refused that authority when presented directly, and refused it when relabeled as Provider B authority.

Provider B's own legitimate authority continued to work.

## Claim under test

MP003 asks:

**If an attacker holds one provider's real authorization-issuance private key, does that confer execution authority at a different provider?**

The scored result supports a narrow answer within the tested implementation: it did not.

MP003 does not claim that compromise is harmless. C01 shows the opposite for Provider A. The claim is that one provider's compromise did not become another provider's compromise.

## Architecture under test

Requester  
→ NUVL relay  
→ Provider A and Provider B  
→ association recorder

The authority model:

- Provider A controls Provider A authorization and execution.
- Provider B controls Provider B authorization and execution.
- The relay transports provider-specific authorization but does not verify, originate, or enlarge it.
- The association verifies and records signed provider evidence but does not authorize execution.

The compromise model:

- The attacker holds a byte-identical copy of Provider A's issuance private key.
- Nothing else is compromised: not Provider A's boundary key, not any Provider B key, not any host, not the relay, not the association.

All implementation code is unchanged from MP002. The only new material is in `attacker/`.

## Scored campaign

Scored session:

`MP003_SCORED_20261015_R2`

The contract and manifest were fixed before execution.

Contract SHA-256:

`ac368500126f3314faa7f5193a07bbb78061c10e1931606778b6414702b9579b`

Manifest SHA-256:

`85ac48ff64f7b94d078ceb0638240980d30013a78cf3d850964abbd895eb7368`

Expected results are taken from the manifest, which also specifies which provider receives no authorization in C01, C03, and B02.

## B01_CONTROL

Both providers received fresh legitimate authorizations for the same request under `CTX_MP003_B01`.

| | Provider A | Provider B |
|---|---|---|
| Authorization | `aac7988b…` | `92a84e45…` |
| Result | `START`, execution, `COMPLETE` | `START`, execution, `COMPLETE` |

Association records 4–7, all signature-valid.

**PASS**

One earlier B01 send in this session failed because of a harness file-naming error. Both providers returned signed `DENY auth_malformed`, recorded as records 2–3. That attempt is retained, not scored, and is not a property failure.

## C01_COMPROMISED_A_TO_A

The attacker minted a fresh `PROVIDER_A` authorization with the compromised key. Only the Provider A header was sent.

| | Provider A | Provider B |
|---|---|---|
| Received | attacker-minted A auth `6e3ce147…` | nothing |
| Result | `START`, execution, `COMPLETE` | `DENY auth_missing` |

Association records 8–10. Provider B state unchanged.

**PASS**

This establishes that the compromised key is real Provider A authority. It is the precondition for C02 and C03, not a containment result.

## C02_PROVIDER_A_AUTH_TO_B

The attacker minted a fresh `PROVIDER_A` authorization with the compromised key, and the same value was sent in both the A and B headers.

| | Provider A | Provider B |
|---|---|---|
| Received | attacker-minted A auth `0e2ed472…` | the same A auth |
| Result | `START`, execution, `COMPLETE` | `DENY auth_provider_mismatch` |

Association records 11–13. Provider B's signed `DENY` names `0e2ed472…`. Provider B did not consume it, start, execute, or complete. Its state files were byte-unchanged.

**PASS**

Provider B rejected the authorization at its provider-identity check (contract §11, step 6), before any signature evaluation. In the same operation, the identical authorization executed at Provider A and was refused at Provider B.

## C03_CLAIM_B_SIGNED_BY_A

The attacker built a fresh authorization claiming `PROVIDER_B`, with a correctly derived authorization ID, and signed it with the compromised Provider A key. Only the Provider B header was sent.

| | Provider A | Provider B |
|---|---|---|
| Received | nothing | forged `PROVIDER_B` claim `11e016ab…` |
| Result | `DENY auth_missing` | `DENY auth_bad_sig` |

Association records 14–15. No `START` or `COMPLETE` from either provider. Both providers' state files were byte-unchanged.

**PASS**

The forgery passed Provider B's identity and authorization-ID checks and failed at issuance-signature verification (step 8). Offline checking confirms the signature is valid under Provider A's issuance public key and invalid under Provider B's.

## B02_POST_ATTACK_B_HEALTH

Provider B received a fresh legitimate authorization after C01–C03. Only the Provider B header was sent.

| | Provider A | Provider B |
|---|---|---|
| Received | nothing | legitimate B auth `8f0e91c8…` |
| Result | `DENY auth_missing` | `START`, execution, `COMPLETE` |

Association records 16–18.

**PASS**

Provider B's `local_execution_seq` went directly from 1 (B01) to 2 (B02). No Provider B execution occurred during the attack cases.

## Final state

| | Executions | Spent authorizations |
|---|---|---|
| Provider A | 3 — B01, C01, C02 | 3 |
| Provider B | 2 — B01, B02 | 2 |

Neither the C02 authorization nor the C03 forgery appears in Provider B's spent state.

Association: 19 records, hash chain verified, all 17 submissions signature-valid. Final record hash:

`4c3282924708f504323bbd2cb1188bd0f2071e54a66b5bdb928e344abaa0a906`

## Interpretation

### Why "different keys" is not the whole answer

Provider A and Provider B use different issuance keys, so it is expected that a Provider A key does not produce a valid Provider B signature. MP003 tests whether anything in the tested path converts one provider's authority into the other's despite that:

- **The relay** forwarded attacker-supplied authorization to Provider B in C02 and C03 without decoding, verifying, or re-signing it. It holds no provider keys.
- **The association** recorded Provider B's refusals and Provider A's executions as signed statements from each provider. It authorizes nothing, and holds only boundary public keys.
- **Provider B** decides what counts as Provider B authority using only its own issuance public key. It loads no Provider A key.
- **The authorization format** binds provider identity into the signed object and into the authorization ID. Relabeling (C03) therefore required a new signature that the attacker could not produce under Provider B's key.

No shared trust root, intermediary verification step, or aggregation point exists in the tested path through which Provider A authority could be accepted as Provider B authority.

### What the compromise did do

Provider A executed both authorizations minted with its compromised key. In this implementation, Provider A cannot distinguish attacker-minted authority from legitimately minted authority. Detecting or recovering from that is outside MP003.

## Limitations

MP003 does not establish:

- that a compromised Provider A remains trustworthy;
- compromise of Provider A's boundary-signing key (an attacker with it could forge Provider A boundary evidence);
- compromise of any Provider B key or host;
- compromise of the relay or association host;
- detection, revocation, rotation, or recovery;
- denial-of-service resistance;
- crash-window, concurrent-use, power-loss, or restart behavior;
- cross-provider atomicity;
- globally synchronized chronology;
- implementation diversity (both providers run the same code base);
- physical actuation or independent hardware-witness evidence;
- independent association re-verification.

## Where MP003 sits in the series

- **MP001** — authority separation held when roles were split across real independent hosts.
- **MP002** — providers holding valid authorization for the same operation reached independent decisions.
- **MP003** — compromise of one provider's issuance authority did not cross into the other provider's execution boundary.

Next: **MP004** — independent offline re-verification of the recorded provider evidence, without relying on the recorder's own verification results.

## Evidence

- Scored evidence: `evidence/scored/`
- Campaign history and staging: `PROVENANCE.md`
- Locked definition: `configs/`
- Attacker material: `attacker/`
