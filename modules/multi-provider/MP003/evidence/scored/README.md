# Scored Evidence

This directory contains the preserved evidence from the MP003 scored campaign.

The scored run tested whether compromise of Provider A's authorization-issuance key confers Provider B execution authority.

The campaign contained a control case, three compromised-key cases, and a post-attack health check.

## Session

Scored session:

`MP003_SCORED_20261015_R2`

This is the second scored attempt for MP003. The first attempt is preserved unchanged under `../retained_partial/`. See that directory and `../../PROVENANCE.md` for why the campaign was restarted.

The contract, run manifest, association recorder, provider registry, provider runtimes, mint utilities, attacker utilities, keys, and relay implementation were fixed for the scored campaign. Their hashes are recorded in `../../configs/MP003_RUN_MANIFEST.json` and were re-verified against the published copies before publication.

The association log's `SESSION_START` record carries the hashes the recorder loaded at startup:

| Item | SHA-256 |
|---|---|
| Contract | `ac368500126f3314faa7f5193a07bbb78061c10e1931606778b6414702b9579b` |
| Run manifest | `85ac48ff64f7b94d078ceb0638240980d30013a78cf3d850964abbd895eb7368` |
| Association recorder | `fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc` |
| Provider registry | `59d739588427d87313e3434982d943a9c82bad26c3fe3deb7d5488efadb6088d` |

Unlike MP002, the contract and manifest are not duplicated inside this directory. The authoritative copies are under `../../configs/`.

## Contents

- `SCORECARD.txt` — scored-result record written after the campaign.
- `association.jsonl` — append-only hash-chained association record of every signed provider boundary submission received during the session.
- `SHA256SUMS.txt` — integrity manifest for this directory tree.
- `B01_CONTROL/` — control case.
- `C01_COMPROMISED_A_TO_A/` — compromised Provider A key used against Provider A.
- `C02_PROVIDER_A_AUTH_TO_B/` — valid Provider A authority presented to Provider B.
- `C03_CLAIM_B_SIGNED_BY_A/` — Provider B identity claimed under Provider A's key.
- `B02_POST_ATTACK_B_HEALTH/` — legitimate Provider B authority after the attack cases.
- `final_provider_a/`, `final_provider_b/` — final durable provider state.
- `operator_transcripts/` — console output from all four processes, saved after the session.

Each case directory has its own README with identifiers, association records, and provider state checks.

## Scored cases

| Case | Provider A header | Provider B header | Provider A result | Provider B result | Result |
|---|---|---|---|---|---|
| B01 | legitimate A auth | legitimate B auth | `START` → `COMPLETE` | `START` → `COMPLETE` | **PASS** |
| C01 | A auth minted with compromised A key | absent | `START` → `COMPLETE` | `DENY auth_missing` | **PASS** |
| C02 | A auth minted with compromised A key | the same A auth | `START` → `COMPLETE` | `DENY auth_provider_mismatch` | **PASS** |
| C03 | absent | auth claiming `PROVIDER_B`, signed with compromised A key | `DENY auth_missing` | `DENY auth_bad_sig` | **PASS** |
| B02 | absent | legitimate B auth | `DENY auth_missing` | `START` → `COMPLETE` | **PASS** |

Expected results are taken from the locked run manifest, which specifies which header is absent in each case. Every observed result matched the manifest.

For C02 and C03, Provider B's non-consumption and non-execution were verified from Provider B's own state files after each case, not inferred from the `DENY`.

## Association record map

| Records | Content |
|---|---|
| 1 | `SESSION_START` |
| 2–3 | B01 harness misfire — both providers `DENY auth_malformed`, retained, not scored |
| 4–7 | B01 |
| 8–10 | C01 |
| 11–13 | C02 |
| 14–15 | C03 |
| 16–18 | B02 |
| 19 | `SESSION_END`, `submission_count` 17 |

All 17 submissions passed signature verification against the registered provider boundary keys, matched the registry, and none was a duplicate.

## Retained harness misfire

Records 2 and 3 come from the first B01 send. The sending harness referenced the wrong authorization filenames, and the forwarded header values were non-empty but undecodable. Both providers emitted signed `DENY auth_malformed`. Nothing was consumed or executed.

This was a harness/precondition misfire. The intended B01 condition was not reached on that attempt. It is not a property failure. The records remain in the hash chain and are not scored. See `B01_CONTROL/README.md`.

## Final provider state

| | Executions | Spent authorizations |
|---|---|---|
| Provider A | 3 (B01, C01, C02) | 3 |
| Provider B | 2 (B01, B02) | 2 |

These counts reconcile with the scored cases:

- Provider A executed B01 and both cases in which it received an authorization minted with its compromised key.
- Provider B executed only the two authorizations minted with its own issuance key.
- Neither the C02 Provider A authorization nor the C03 forgery appears in Provider B's state.

## Integrity

Association log: 19 records, hash chain verified from the genesis value through the final record.

Final association record hash:

`4c3282924708f504323bbd2cb1188bd0f2071e54a66b5bdb928e344abaa0a906`

SHA-256 of `association.jsonl`:

`50af864099a7eb91970866a664005caa24042224d2b69525e0e9610c53eb642a`

SHA-256 of `SCORECARD.txt`:

`b35f1503a3e521c1c13b0f13262637c52743fc12e77f28437eef11d51ea15a7b`

`SHA256SUMS.txt` lists 67 files with paths relative to this directory and LF line endings. It verifies with:

`sha256sum -c SHA256SUMS.txt`

The README files in this tree were added after `SHA256SUMS.txt` was generated and are not listed in it.

`SHA256SUMS.txt` was regenerated once after the session, solely to add `operator_transcripts/`. The superseded version (`7a375202…`) and the current version (`73e31c55…`) are both recorded in the operator notes. No other evidence file changed.

## What MP003 demonstrates

The scored evidence supports the MP003 claim:

**compromise of Provider A's tested authorization-issuance key produced valid Provider A authority, but did not confer Provider B execution authority under this contract.**

- C01 shows the compromised key is real Provider A authority.
- C02 shows that authority is refused at Provider B on scope.
- C03 shows relabeling it as Provider B is refused at Provider B on signature.
- B02 shows Provider B's legitimate authority still works afterward.

The relay transported attacker-supplied authorization to both providers without verifying, minting, or converting it.

The association verified and preserved signed provider evidence without authorizing execution.

## Important limitations

MP003 does not claim that a compromised Provider A remains trustworthy. Provider A executed every authorization minted with its compromised key.

MP003 does not establish:

- compromise of Provider A's boundary-signing key;
- compromise of any Provider B key;
- compromise of a provider host, the relay host, or the association host;
- key revocation, rotation, or recovery;
- detection of the compromise;
- denial-of-service resistance;
- crash-window, concurrent-use, power-loss, or restart behavior;
- cross-provider atomicity;
- globally synchronized chronology across hosts (provider-local timestamps are not comparable across hosts);
- implementation diversity between providers;
- physical actuation or independent hardware-witness evidence.

## Related evidence

First scored attempt, retained:

`../retained_partial/`

Provider state captured before the R2 reset:

`../pre_run_state/`

Preflight artifacts (never scored):

`../preflight/`

Operator notes and pre-run baseline:

`../../operator/`
