# Configuration

This directory contains the locked MP003 contract and run manifest. Both were fixed before scoring and define the campaign the scored evidence is interpreted against.

## Contents

- `MP003_CONTRACT.md` — normative test contract for MP003.
- `MP003_RUN_MANIFEST.json` — machine-readable description of the scored campaign: expected cases, fixed implementation, key, and attacker-utility hashes, compromise scope, and declared claim boundaries.

## Locked contract

`MP003_CONTRACT.md` SHA-256:

`ac368500126f3314faa7f5193a07bbb78061c10e1931606778b6414702b9579b`

The contract carries forward the MP001/MP002 wire format: canonical JSON, request representation, mechanical binding, operation ID, provider authorization with a separate issuance keypair, signed boundary events, and provider-local single-use spent state.

Its provider validation order (§11) is the basis for interpreting the MP003 rejections:

1. Parse relay artifact.
2. Recompute mechanical binding.
3. Supplied binding differs → `binding_mismatch`
4. Require provider authorization → `auth_missing`
5. Decode and parse authorization package → `auth_malformed`
6. Require authorization `provider_id` to equal the local provider → `auth_provider_mismatch`
7. Recompute authorization ID → `auth_id_mismatch`
8. Verify Ed25519 issuance signature with the local provider's issuance key → `auth_bad_sig`
9. Require authorized `request_repr` to equal received → `auth_request_mismatch`
10. Require authorized context to equal received → `auth_context_mismatch`
11. Apply provider-local policy → `policy_denied`
12. Require authorization unspent → `auth_spent`
13. Durably record authorization as spent.
14. Generate signed `START`.
15. Perform provider-local execution.
16. Durably record local execution evidence.
17. Generate signed `COMPLETE`.

Step numbers match the contract. Case READMEs refer to them: C02 is rejected at step 6, C03 at step 8, and `auth_missing` denials at step 4.

All MP003 rejections occur before durable consumption. No `START` is generated before consumption.

§20 defines the MP003 compromise scope and the five scored cases. §20 also defines the claim boundary.

## Run manifest

`MP003_RUN_MANIFEST.json` SHA-256:

`85ac48ff64f7b94d078ceb0638240980d30013a78cf3d850964abbd895eb7368`

Compromise scope declared in the manifest:

`PROVIDER_A_ISSUANCE_PRIVATE_KEY_ONLY`

### Scored cases as specified

| Case | Context | Provider A header | Provider B header | Expected A | Expected B |
|---|---|---|---|---|---|
| B01 | `CTX_MP003_B01` | legitimate | legitimate | `START`, execution, `COMPLETE` | `START`, execution, `COMPLETE` |
| C01 | `CTX_MP003_C01` | compromised-key A auth | absent | `START`, execution, `COMPLETE` | `DENY auth_missing` |
| C02 | `CTX_MP003_C02` | compromised-key A auth | the same A auth | `START`, execution, `COMPLETE` | `DENY auth_provider_mismatch`, not consumed |
| C03 | `CTX_MP003_C03` | absent | auth claiming `PROVIDER_B`, signed with A key | `DENY auth_missing` | `DENY auth_bad_sig`, not consumed |
| B02 | `CTX_MP003_B02` | absent | legitimate | `DENY auth_missing` | `START`, execution, `COMPLETE` |

The manifest also fixes the exact request bytes for each case.

The "absent" header positions are part of the locked specification. Scoring followed the manifest, including the `auth_missing` denials at the provider that received no authorization.

### Fixed hashes

The manifest fixes SHA-256 values for:

- contract;
- association recorder and provider registry;
- relay;
- Provider A runtime and mint utility;
- Provider B runtime and mint utility;
- Provider A and Provider B issuance private and public keys;
- the attacker's copy of the Provider A issuance private key, and the Provider A issuance public key in `attacker/`;
- both attacker mint utilities.

All of these were verified against the published files in this module before publication. The attacker's private key copy is byte-identical to `provider_a/provider_a_issuance_private.pem` (`37f808b6…`).

The association log's `SESSION_START` record independently carries the contract, manifest, recorder, and registry hashes the recorder loaded at session start.

## Relationship to MP002

Every implementation file was reused byte-for-byte from MP002:

- relay;
- Provider A runtime and mint utility;
- Provider B runtime and mint utility;
- association recorder and provider registry.

The experimental delta for MP003 is the attacker material in `../attacker/` and the scored case design, not a code change.

The Provider B runtime therefore still contains the MP002 local-policy gate (`POLICY_DENY_CONTEXT = "CTX_MP002_DIVERGE"`). No MP003 case used that context, so the gate was never triggered.

## Claim boundaries

The manifest declares as **claimed**:

- `compromised_provider_a_issuance_claimed`

It declares as **not claimed**:

- physical execution witness;
- cross-host clock authority;
- implementation diversity;
- crash-window, concurrent, or power-loss replay persistence;
- provider host compromise;
- boundary key compromise;
- key revocation or recovery;
- independent association re-verification.

## Integrity discipline

The contract and manifest were fixed before the scored campaign and were not edited afterward.

The first scored attempt and the R2 campaign both ran under the same contract and manifest hashes, as recorded in both sessions' `SESSION_START` records.

Differences between this specification and earlier informal descriptions of MP003 are resolved in favor of these locked files.

The configuration defines the test. The evidence records what happened. The documentation explains what the evidence supports.

## Related material

Scored evidence:

`../evidence/scored/`

Attacker utilities and key copy:

`../attacker/`

Provider implementations:

`../provider_a/`

`../provider_b/`

Association implementation:

`../association/`

Relay implementation:

`../intermediary/`
