# Evidence

This directory contains the retained evidence for MP003.

MP003 tests whether compromise of Provider A's authorization-issuance key confers Provider B execution authority.

Evidence is separated so setup activity, a retained first attempt, and the scored campaign cannot be confused with one another.

## Contents

- `scored/` — the scored MP003 campaign (`MP003_SCORED_20261015_R2`). **This is the MP003 result.**
- `retained_partial/` — the first scored attempt (`MP003_SCORED_20261015`), preserved unchanged. One legitimate B01 ran; no compromised-key case ran.
- `pre_run_state/` — provider state captured during pre-test setup from the first attempt.
- `preflight/` — dry-run mints from the attacker utilities, generated before scoring and never sent.

## Scored evidence

`scored/` contains the five scored cases:

| Case | What it tests | Result |
|---|---|---|
| B01 | Both providers execute their own legitimate authorization | **PASS** |
| C01 | The compromised Provider A key produces authority Provider A accepts | **PASS** |
| C02 | Valid Provider A authority presented to Provider B is refused (`auth_provider_mismatch`) | **PASS** |
| C03 | An authorization claiming `PROVIDER_B` but signed with Provider A's key is refused (`auth_bad_sig`) | **PASS** |
| B02 | Provider B's legitimate authority still works after the attack cases | **PASS** |

`scored/` also retains one harness misfire before the scored B01: association records 2–3, both providers `DENY auth_malformed`. It is not scored and is not a property failure.

See `scored/README.md` for the full campaign, association record map, final state, and integrity values.

## Non-scored evidence

### retained_partial/

The first attempt executed one valid B01. Provider state from that B01 was then misclassified as pre-run residue and reset, so the campaign was restarted cleanly as R2. The attempt is preserved as found:

- its association log has no `SESSION_END`, because the recorder was not stopped cleanly before the restart;
- a separate short log records the recorder being started in the wrong terminal window;
- its empty C01–C03, B02, and final-state folders are not present in the repository, because Git does not track empty directories.

### pre_run_state/

Four provider state files from the first attempt, captured during pre-test setup. Their JSON content matches the first attempt's B01 post-state. They differ by trailing line-ending bytes added during capture through a Windows shell.

### preflight/

One dry-run mint from each attacker utility, against preflight requests and contexts. Both were verified offline as signed by the compromised Provider A issuance key. Neither was presented to a provider.

## Evidence layers in the scored campaign

**Request and authorization artifacts.** Each case directory preserves the exact request bytes and the authorization package or packages sent.

**Relay send records.** C01 through B02 each include `relay_send_record.txt`: send time, context, which file was placed in each header, request hash, and HTTP status.

**Provider-local state.** Each case directory preserves both providers' state after the case, with raw `scp` drops in `_post_a/` and `_post_b/`. `final_provider_a/` and `final_provider_b/` hold the end-of-campaign state.

**Signed association record.** `scored/association.jsonl` is the hash-chained record of every signed boundary event both providers emitted during the session.

**Operator transcripts.** `scored/operator_transcripts/` holds console output from all four processes, saved after the session. It corroborates the signed record; it does not replace it.

These layers were cross-checked against one another. For every rejection at Provider B, non-consumption and non-execution were confirmed from Provider B's own state files, not inferred from the signed `DENY`.

## Integrity

`scored/SHA256SUMS.txt` covers the scored evidence tree, 67 files. README files are not included in it.

The non-scored directories have no checksum file of their own. Their READMEs list the SHA-256 of each file.

## Related

Operator notes and pre-run baseline:

`../operator/`

Locked contract and run manifest:

`../configs/`

Attacker utilities and key copy:

`../attacker/`
