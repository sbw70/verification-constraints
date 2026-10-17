# MP003 Provenance

This document records the implementation lineage, test configuration, deployment identity, campaign history, evidence handling, and publication staging for MP003.

MP003 reuses the MP002 multi-provider implementation unchanged and adds attacker-side material that models compromise of Provider A's authorization-issuance private key.

## Test identity

Test:

`MP003`

Scored session:

`MP003_SCORED_20261015_R2`

Primary claim under test:

**Compromise of Provider A's authorization-issuance key can produce valid Provider A authority, but does not confer Provider B execution authority.**

The scored campaign contained:

- `B01_CONTROL`
- `C01_COMPROMISED_A_TO_A`
- `C02_PROVIDER_A_AUTH_TO_B`
- `C03_CLAIM_B_SIGNED_BY_A`
- `B02_POST_ATTACK_B_HEALTH`

## Relationship to MP001 and MP002

The architecture remained:

Requester  
→ NUVL relay  
→ Provider A and Provider B  
→ association recorder

Provider A and Provider B remained separate authority domains, each with its own issuance and boundary keypairs and its own spent state.

The relay remained mechanical transport.

The association remained an evidence-verification and recording component, not an execution authority.

MP003 did not change the authorization format, request binding, boundary-event format, association record format, or provider spent-state mechanism.

## Experimental delta

MP003 changed no implementation file.

Every runtime, mint utility, key, the relay, the association recorder, and the provider registry are byte-identical to the MP002 publication copies. This was checked file by file during publication staging.

The MP003 delta is entirely attacker-side, in `attacker/`:

| File | SHA-256 |
|---|---|
| `compromised_provider_a_issuance_private.pem` | `37f808b6901f5020fb7b68924217d76f7923d898e44913a6338008d85ac15fd8` |
| `provider_a_issuance_public.pem` | `a52276369981962b878311ec4e33186af25ac10cd359fafbc760e118e607ad71` |
| `mint_compromised_a.py` | `41306a6fe2f4751443b531e0938128ec08c771aea62d68e8fc4b952dc2284f10` |
| `mint_forged_b_with_a_key.py` | `7963cf83496aca069e51cd2cc7fcedb4f9720b8b0f2684303bea15d863b3ef1b` |

The attacker's private key is byte-identical to Provider A's real issuance private key.

`mint_compromised_a.py` differs from Provider A's legitimate mint by one line, the private key file name. `mint_forged_b_with_a_key.py` differs from `mint_compromised_a.py` by one line, `PROVIDER_ID = "PROVIDER_B"`.

The Provider B runtime still contains the MP002 policy gate for `CTX_MP002_DIVERGE`. No MP003 case used that context.

## Implementation identities

| Component | SHA-256 |
|---|---|
| Relay | `09d458cc8e3e13706b5463deffea0e14fcd784011a629623a09b9bd5ee04d6f4` |
| Provider A runtime | `c875582b275f270b8e68af69ed4ee84896e83815cdf33b7d7c5ccc813fe2e606` |
| Provider A mint | `1a485e8a5d3de854cb31303b8d3bf1339ef72cb9b42f308490bd02519e76d7ec` |
| Provider B runtime | `5e0ab4b79df4c97bc7bc324d63da85711728d625b82306cdce6c92592e2ee13e` |
| Provider B mint | `1b3ba1314761a5489817c660cdc4d62e65ba77deae2bfce2fdce48c228f98deb` |
| Association recorder | `fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc` |
| Provider registry | `59d739588427d87313e3434982d943a9c82bad26c3fe3deb7d5488efadb6088d` |

These identities are tied to the scored campaign in four independent places:

1. the locked run manifest, which fixes all of them;
2. `operator/MP003_PRE_RUN_BASELINE.txt`, captured before scoring;
3. the association `SESSION_START` record, for the recorder, registry, contract, and manifest;
4. an SSH check of the live provider hosts before C01, which confirmed both provider runtimes and mint utilities matched the manifest.

Unlike MP002, MP003 has no separate `deployed_implementation_hashes.txt`.

## Reused startup banners

Because implementations were reused byte-for-byte, their startup banners keep earlier names:

- relay: `MP001_NUVL_MULTI_PROVIDER_RELAY`;
- association recorder: `MP001_ASSOCIATION_RECORDER`;
- Provider B: `MP002_PROVIDER_B`.

These are implementation labels, not session identifiers. No source file was modified to change them.

## Locked contract and manifest

| File | SHA-256 |
|---|---|
| `configs/MP003_CONTRACT.md` | `ac368500126f3314faa7f5193a07bbb78061c10e1931606778b6414702b9579b` |
| `configs/MP003_RUN_MANIFEST.json` | `85ac48ff64f7b94d078ceb0638240980d30013a78cf3d850964abbd895eb7368` |

Both were fixed before the first scored attempt and not edited afterward. Both scored attempts' `SESSION_START` records carry these hashes.

Unlike MP002, copies are not duplicated inside the scored evidence directory.

The manifest specifies which authorization header is absent in C01, C03, and B02, and therefore which provider is expected to return `auth_missing`. Earlier informal descriptions of MP003 omitted those details. Scoring followed the manifest.

## Provider keys

Each provider used separate laboratory Ed25519 keypairs for authorization issuance and for boundary-event signing. All are published intentionally for reproducibility. They are test keys, not production credentials.

Only Provider A's issuance private key was treated as compromised. Publication of the keys after the run does not change which components held or exercised which keys during the scored campaign.

## Deployment

| Role | Host | Address | Working directory |
|---|---|---|---|
| Provider A | `Xer0trust-3` (Dell) | 192.168.1.118 | `/home/seth/MULTI_PROVIDER_003/provider_a` |
| Provider B | `Xer0trust2` (HP) | 192.168.1.106 | `/home/seth/MULTI_PROVIDER_003/provider_b` |
| Relay | `nuvl-relay` (Raspberry Pi 3B+) | 192.168.1.100 | `/home/seth/MULTI_PROVIDER_003/intermediary` |
| Association recorder | `Xer0trust` (OmniBook) | 192.168.1.102 | `MULTI_PROVIDER_003\association` |
| Requester / operator | `Xer0trust` (OmniBook) | 192.168.1.102 | `MULTI_PROVIDER_003` |

Network notes recorded before the run:

- challenge traffic stopped;
- a managed switch was present but deliberately not connected;
- the existing multi-provider topology was otherwise unchanged.

The operator notes' header also lists a Chromebook as requester and as a network change. That is incorrect. The Chromebook was not involved in MP003, and a later notes entry corrects it.

MP003 makes no globally synchronized cross-host timing claim. Host clocks were not synchronized. In C01, Provider A's local execution timestamp is earlier than the operator's send timestamp.

## Campaign history

All times are operator-local (UTC−4) on 2026-10-15 unless noted.

### Pre-run baseline (17:53)

`operator/MP003_PRE_RUN_BASELINE.txt` recorded the contract, manifest, and implementation hashes before scoring.

### Preflight

Each attacker utility was exercised once against preflight requests and contexts. The packages are in `evidence/preflight/`. Both were checked offline as signed by the compromised Provider A key. Neither was presented to a provider.

### First scored attempt — `MP003_SCORED_20261015`

Preserved unchanged in `evidence/retained_partial/`.

- The association recorder was first started in the wrong terminal window and stopped with zero submissions. That log is retained.
- A legitimate B01 then executed at both providers (A `a6fd6f04…`, B `52d0874f…`).
- The resulting provider state was later misclassified as pre-run residue (21:52) and reset (22:00). The first reset command produced malformed JSON because quoting was stripped across PowerShell/SSH; the files were then rewritten correctly via base64 transport.
- The misclassification was corrected at 22:18.
- No compromised-key case ran.
- This session's association log has no `SESSION_END`, because the recorder was not stopped cleanly before the restart.

Provider state copies from this attempt, captured during pre-test setup, are in `evidence/pre_run_state/`.

### Clean restart as R2 (22:27)

Because provider state had been reset mid-session, the first attempt was retained and a clean campaign was started. The operator notes record that before R2:

- Provider A and Provider B spent state was clean;
- both execution logs were absent;
- association, providers, and relay were confirmed down.

R2 `SESSION_START`: 2026-10-16 02:29:03 UTC.

### B01 harness misfire (22:39)

The first R2 B01 send referenced `provider_*_authorization.b64` while the mint utilities had written `provider_*_authorization.json.b64`. The forwarded header values were non-empty and undecodable. Both providers emitted signed `DENY auth_malformed` (association records 2–3). Nothing was consumed. This is retained and not scored.

The original note described the headers as empty. It was corrected later: an empty header produces `auth_missing`, not `auth_malformed`.

### Scored cases (22:41–23:30)

| Case | Sent (local) | Records | Result |
|---|---|---|---|
| B01 | not recorded in a file | 4–7 | PASS |
| C01 | 23:20:22.923 | 8–10 | PASS |
| C02 | 23:23:52.474 | 11–13 | PASS |
| C03 | 23:27:15.330 | 14–15 | PASS |
| B02 | 23:30:10.639 | 16–18 | PASS |

Per-case identifiers and evidence are in each case directory under `evidence/scored/`.

## Request transmission

C01 through B02 were sent from the OmniBook operator host with `curl.exe`.

Before each send, the operator command checked that each authorization header value was non-empty and decoded back to the saved package, to prevent a repeat of the B01 misfire. Each send wrote `relay_send_record.txt` with time, relay URL, context, which file was placed in each header, request hash, and HTTP status.

The scored B01 send predates this procedure. Its requester host and HTTP status were not recorded in a file.

The relay returns `204` before provider delivery completes. Provider outcomes were established from signed association records and provider state, not from relay responses.

## Provider state capture

Before C01, both providers' live state and runtime hashes were read over SSH. Both providers' state was byte-identical to the B01 post-case files.

After each of C01, C02, C03, and B02, both providers' spent-state and execution files were copied byte-for-byte via `scp` into the case directory (`_post_a/`, `_post_b/`), with renamed copies alongside (`*_after_<case>`).

For every Provider B rejection, non-consumption and non-execution were confirmed from Provider B's own files, not inferred from the signed `DENY`.

The B02 post-state was also copied to `evidence/scored/final_provider_a/` and `final_provider_b/`.

## Association provenance

The association recorder was unchanged from MP001 and MP002. It verifies each provider boundary submission against the registered boundary key and appends it to a hash-chained log.

It does not compute quorum, cross-provider success, or overall authorization. Pass/fail scoring was done after the session from the preserved evidence.

Integrity:

- 19 records; hash chain independently re-verified from the genesis value;
- all 17 submissions `sig_valid`, `registry_match`, `verification_code=ok`, no duplicates;
- `SESSION_END` `submission_count` 17;
- final record hash `4c3282924708f504323bbd2cb1188bd0f2071e54a66b5bdb928e344abaa0a906`, matching the value the recorder printed at shutdown;
- `association.jsonl` SHA-256 `50af864099a7eb91970866a664005caa24042224d2b69525e0e9610c53eb642a`.

## Final scored provider state

| | Executions | Spent |
|---|---|---|
| Provider A | 3 (B01, C01, C02) | 3 |
| Provider B | 2 (B01, B02) | 2 |

Provider B's state was byte-identical from after B01 through after C03.

## Shutdown

1. The association recorder was stopped first with Ctrl+C. It wrote `SESSION_END` and printed the final record hash.
2. Provider A, Provider B, and the relay were then stopped with Ctrl+C.

Each provider and the relay printed a `KeyboardInterrupt` traceback from `serve_forever()`. None of these scripts installs a signal handler, so this is the normal stop path.

Unlike MP002, no separate post-shutdown process or port check was run. Shutdown is evidenced by the console transcripts and the association `SESSION_END`.

## Operator transcripts

Console output from all four processes was copied from the terminals after shutdown and saved verbatim in `evidence/scored/operator_transcripts/`. None of the processes writes its console to disk, so these are operator transcripts, not process-written logs.

They were added to the scored evidence after the session. `SHA256SUMS.txt` was regenerated once to include them:

- superseded: `7a375202e564d7f13c9e71d6fbd454cac559d3f7e11a0955170940b55cafd3af`
- current: `73e31c55530fc63297070d041afdc00acd9f49f279ed5ec9467897af70b6a1dc`

No other evidence file changed.

## Corrections on record

The operator notes are append-only. Three earlier statements are wrong and are corrected by later entries, with the originals retained:

1. pre-run residual state was actually the first attempt's B01;
2. the B01 R2 misfire headers were non-empty and undecodable, not empty;
3. the Chromebook was not involved in MP003.

Notes entries from 23:17 onward were drafted with an AI assistant during the session and appended at the operator's direction.

## Scored evidence integrity

During publication staging:

- all 67 entries in `evidence/scored/SHA256SUMS.txt` verified against the staged copy;
- the staged scored, retained-partial, pre-run-state, and preflight trees matched their sources byte-for-byte;
- the scored tree contained no files missing from `SHA256SUMS.txt`, apart from README files added afterward;
- all 16 file hashes fixed by the run manifest matched the staged files.

## Publication staging

The publication tree was built by copying.

Nothing in the working MP003 tree was moved, renamed, or rewritten to construct it. The working tree did receive the post-session additions described above: append-only notes entries, `SCORECARD.txt`, `SHA256SUMS.txt` (generated once, then regenerated once to add the transcripts), and `operator_transcripts/`.

Staging location:

`MULTI_PROVIDER_003/github/modules/multi-provider/MP003/`

It contained 114 files before documentation was added. Original filenames were preserved.

Excluded from staging:

- `__pycache__/` and compiled Python files;
- live provider runtime state in the working provider directories, where authoritative scored copies exist under `evidence/scored/`.

Before publication, every staged file, including decoded base64 authorization headers and association submission bodies, was scanned for Wi-Fi credentials, passwords, tokens, and SSH keys. None were found. The only private keys present are the five intended laboratory Ed25519 keys. The transcripts contain the lab username, host names, and private LAN addresses, which were left as recorded.

Ten empty case and state folders in the retained first attempt are not present in the repository, because Git does not track empty directories. They are listed in `evidence/retained_partial/README.md`.

## Claim boundaries

MP003 supports a narrow result:

**With Provider A's real authorization-issuance private key in attacker hands, the attacker produced authority Provider A accepted and executed. The same compromise did not produce Provider B execution authority: valid Provider A authority presented to Provider B was refused on scope, an authorization relabeled as Provider B but signed with Provider A's key was refused on signature, and Provider B's legitimate authority continued to work afterward.**

MP003 does not establish:

- that a compromised Provider A remains trustworthy;
- compromise of Provider A's boundary-signing key;
- compromise of any Provider B key;
- compromise of any provider host, the relay host, or the association host;
- detection, revocation, rotation, or recovery of a compromised key;
- denial-of-service resistance;
- crash-window, concurrent-use, power-loss, or restart behavior;
- cross-provider atomicity;
- globally synchronized chronology;
- implementation diversity;
- physical actuation or independent hardware-witness evidence;
- independent association re-verification as part of the scored run.

## Publication principle

The intended evidentiary chain is:

locked test definition  
→ identifiable implementation and attacker material  
→ preserved request and authorization artifacts  
→ provider-local durable state  
→ signed association evidence  
→ integrity manifests  
→ scoped interpretation

The documentation describes what that evidence supports and where the test stops. It does not replace the evidence.
