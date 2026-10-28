# R02 — Provider B restart durability — BLOCKED TEMPLATE

Target: Provider B, separate HP/Mint. Pavilion is never the target. Use only window labels confirmed by the final machine map. Follow LIVE_COMMAND_TEMPLATES.md to bind the session-specific variables and argument arrays. No commands below are permitted while R2/lock/readiness/authorization gates are unresolved.

## Preconditions

R2 reviewed successfully; final claim/manifests and canonical lock verified; current physical role/hostname/IP map and all paths match; explicit phase/session authorization; distinct clean state/evidence destinations; valid ledger and matching snapshot; no duplicate provider; registry/trust hashes match; relay and association running once and not restarted during case; controller continuously reads the association log. `$Case` and MP_CASE MUST equal R02; MP_PROVIDER MUST equal provider_b. Controller and provider roots may differ.

Provider and controller working directories and variables must be printed/confirmed before running case commands. The assistant gives ONE command per step and waits; copy operations below are separate steps, never stacked. Failure/collision = stop; do not silently retry.

## Consume and prove completion

1. OmniBook — MAIN PowerShell: `python "$MpRoot\harness\live_case.py" prepare @LiveArgs`. Expected: NEW case directory, preserved request/context/authorization/header and identity.json. No request sent. Verify output bytes and absence of reused case destination.
2. Copy the newly prepared case to the target's NEW case directory using the single initial SCP template. Do not mint a second target-side authority. Verify original identity/request/package/header hashes on both machines. Providers need these preserved identities for capture.
3. Provider B — SSH (inspection): `python3 "$MP_ROOT/harness/live_case.py" capture-state "${MP_ARGS[@]}" --pid "$MP_PID" --label pre_consume`. Expected: raw snapshot, consume_ledger.jsonl, execution.jsonl, snapshot.json and process.json in pre_consume. Copy that NEW directory to controller with CaptureLabel=pre_consume as a separate command; verify its hashes/path/authority.
4. OmniBook — MAIN PowerShell: `python "$MpRoot\harness\live_case.py" consume @LiveArgs --association-log $AssociationLog`. Expected: correlated provider-signed START and COMPLETE captured under consume/boundary_records.json. A relay 204 is never completion. Missing/ambiguous evidence = STOP, no kill.
5. Provider B — SSH (inspection): `python3 "$MP_ROOT/harness/live_case.py" capture-state "${MP_ARGS[@]}" --pid "$MP_PID" --label consumed`. Copy consumed to controller once; validate all raw hashes, exactly one valid new ledger entry, matching snapshot/head, exactly one execution and signed matching head. Do not force-stop unless this is proven.
6. Provider B — SSH (inspection): `python3 "$MP_ROOT/harness/live_case.py" capture "${MP_ARGS[@]}" --pid "$MP_PID" --label pre_restart`. Copy pre_restart_process.json and pre_restart_state separately to controller. Verify runtime/ledger/state/cwd/command and actual process identity.
7. OmniBook — MAIN PowerShell: `python "$MpRoot\harness\live_case.py" checkpoint @LiveArgs`. Expected: OPERATOR_CHECKPOINT, automatic_kill_executed=false, exact PID kill instruction. The helper now independently validates captured raw ledger/state and signed consume/head before permitting checkpoint. **STOP POINT:** human confirms prior COMPLETE, no in-flight requests, correct numeric PID and IDLE. Never kill merely because a process is reachable.

## Manual restart and exact replay

8. Provider B — SSH (inspection): human executes the single numeric `kill -KILL <confirmed PID>` supplied by the checkpoint, after IDLE confirmation. This is a template token, not a pasteable literal. Assistant must substitute only the objectively confirmed PID and await output. No scripted termination/restart.
9. Provider B — SSH (runtime): human repeats EXACT prior launch command, same runtime/hash/cwd/state/ledger. Never bootstrap/reset/restore state here. Relay, association, non-target remain running. Health is a preliminary check only. Obtain the actual new PID separately; do not reuse old MP_PID.
10. Provider B — SSH (inspection): `python3 "$MP_ROOT/harness/live_case.py" capture "${MP_ARGS[@]}" --pid "$MP_PID" --label post_restart`. Copy post_restart_process.json and post_restart_state separately. **STOP POINT:** prove same host/boot/runtime/hash/path/cwd/argv/state, new (PID,start_ticks), later ticks. Process-local EXECUTION_SEQ continuity is irrelevant.
11. Provider B — SSH (inspection): `python3 "$MP_ROOT/harness/live_case.py" capture-state "${MP_ARGS[@]}" --pid "$MP_PID" --label before_replay`. Copy once to controller. Require ledger/snapshot/execution equality with consumed and authority still spent. Revalidate preserved exact request/context/package/header hashes.
12. OmniBook — MAIN PowerShell: `python "$MpRoot\harness\live_case.py" replay @LiveArgs --association-log $AssociationLog`. Expected one correlated signed DENY auth_spent, no START/COMPLETE. New process proof is checked before send.
13. Provider B — SSH (inspection): `python3 "$MP_ROOT/harness/live_case.py" capture-state "${MP_ARGS[@]}" --pid "$MP_PID" --label after_replay`. Copy once. **STOP POINT:** raw ledger hash/bytes/lines/entries/seq/head, snapshot and execution must be unchanged; original remains spent; signed DENY head equals current head. Any real additional consume/execution = FAIL, preserve and stop.

## Fresh authority and final evidence

14. OmniBook — MAIN PowerShell: `python "$MpRoot\harness\live_case.py" prepare-fresh @LiveArgs`. Expected a different authorization, only after replay invariants pass. Copy the NEW fresh directory to the target once, preserving all bytes.
15. Provider B — SSH (inspection): `python3 "$MP_ROOT/harness/live_case.py" capture-state "${MP_ARGS[@]}" --pid "$MP_PID" --label before_fresh`. Copy once to controller.
16. OmniBook — MAIN PowerShell: `python "$MpRoot\harness\live_case.py" fresh @LiveArgs --association-log $AssociationLog`. Expected signed START/COMPLETE for the fresh identity; no silent repeat/retry.
17. Provider B — SSH (inspection): `python3 "$MP_ROOT/harness/live_case.py" capture-state "${MP_ARGS[@]}" --pid "$MP_PID" --label after_fresh`. Copy once. Require exactly one added entry, seq+1, prior head link, independently recomputed new head, one fresh execution and matching signed head. Compare the gap from after_replay to before_fresh to ensure no unexplained ledger/state/execution change; recheck original execution count across all final raw evidence.
18. OmniBook — MAIN PowerShell: `python "$MpRoot\harness\live_case.py" score @LiveArgs --association-log $AssociationLog`. Expected case_results.json and SHA256SUMS.txt. The helper revalidates raw material/signatures and rechecks the continuous association log for late original events. Inspect result rather than treating exit code alone as proof. Preserve final provider ledger/state/execution, continuous association log, process evidence and console outputs before ending the session. See POST_RUN_AUDIT.md.

## Outcomes

PASS: every locked consume/restart/replay/fresh assertion, signed correlation and preservation check satisfied. Real property violation after proven prerequisites: FAIL. Missing/wrong host/path/identity/state, unproven consume/restart or unavailable endpoint: PRECONDITION_NOT_MET. Inconsistent/corrupt copies, parser/tooling/correlation ambiguity: HARNESS_ERROR. NOT_RUN if the case never began. Stop on any non-PASS and preserve all attempts/misfires; do not clean up or retry in the same scored campaign. Rehearsal evidence is never scored evidence.
