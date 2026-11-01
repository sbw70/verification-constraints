# MP006 R01 local implementation

Status: LOCAL BUILD. Not deployed, authorized for a live run, or scored.
Linux hosts have not been contacted. No MP005 files are modified.

Use `OPERATING_PROCEDURE.md` for the detailed command-by-command handoff and both
STOP checkpoints. `SOURCE_REVIEW.md` records code-inspection findings and the
three targeted scorer corrections. The build now has eight offline tests; the
original seven-test result is retained in LOCAL_VALIDATION.json as prior history.
Actual relay/recorder environment paths and effective launch configurations remain
STOP 1 review inputs, not facts established by local source inspection.

## Paths and dependency identity

Build root: this directory, under the current Multi Provider project.
Reviewed installation targets (not created by this build):

- Windows: `C:\Users\holiw\esp32-main\MULTI_PROVIDER_006`
- Dell: `/home/seth/MULTI_PROVIDER_006`
- State: `<root>/state/<session>/provider_a/`
- Evidence: `<root>/evidence/<session>/R01/`
- New operator authorizations: `<root>/authorizations/`
- Raw recovery capture: `<evidence>/recovered_before_start/`

`reference/MP005` contains byte-identical dependency directories from public
commit `73713f6e9ed9c95251cc69ec88ef816cab771ac0`. Historical MP005 evidence and
operator authorizations are not copied. Original config locks are retained only
for source provenance; MP006 never changes or uses them to authorize MP006 runs.
The legacy simulation/test code is retained because `verify_harness` checks it.
Do not execute those simulation scripts in this reference dependency tree.

Provider SHA-256:
`79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6`.
The copied PEM files are existing public laboratory fixtures, not new production keys.

## Reuse

`mp006.py` imports `common` and `ledger_evidence` from the frozen reference.
It uses source/harness verification, durable bootstrap, authority preparation,
exact-byte submission, recorder cursors/correlation, Ed25519 boundary validation,
state capture, raw snapshot/ledger validation, replay and consumption/fresh checks,
process identity and SHA-256 inventories without changing those functions.

Authority preparation deliberately calls `prepare_authority` unchanged. Its
legacy `test: MP005` and `CTX_MP005_` fixture prefixes remain; session and case
labels contain MP006, and authority is freshly minted into MP006 directories.
Labels are opaque signed request/context inputs. The wrapper never rewrites a
minted authorization or its header, relaxes binding, or introduces expiry.

New code handles paths, phase orchestration, detached launch, raw pre-start copy,
changed-boot checks, operator/witness evidence, terminal marker, and result assembly.
No new ledger, authorization, signing, or signature-verification algorithm exists.
No timestamps are compared for execution eligibility or scoring. Probe timeout
and sampling cadence apply only to individual reachability observations.

## Review and non-destructive preflight procedure

This is a procedure for review, not permission to deploy or execute it.
Issue complete commands one at a time and inspect actual output between steps.

1. Review this source, configuration, local test report and inventories.
2. After separate deployment approval, verify all machine addresses and identities.
3. Inspect Dell boot/startup mechanisms: system and user services, cron including
   `@reboot`, desktop autostart, login hooks, and any provider supervisors. Preserve
   relevant configuration and disabled/enabled status. Do not rely on a missing
   listener alone to establish absence of autostart. Review any disable change.
4. Verify no unrelated Dell work remains and preserve important non-test data.
5. Check Python, cryptography and `ss`; hash installed reference dependencies.
6. Review actual relay/recorder launch configuration. Frozen relay defaults contain
   historical addresses; do not launch them directly. Keep existing validated
   relay/recorder processes powered, or review separate configuration-only launches
   using their existing interfaces. Association output must be a continuous locally
   accessible log and use the copied trust keys. Do not reuse MP005 evidence paths.
7. Choose a unique MP006 session. Confirm state/evidence paths are absent. The final
   reviewed config sets readiness flags and `status: REVIEWED_FOR_OPERATOR_RUN`.
8. Create a new explicit operator authorization with `authorized: true`, `session`,
   `config_sha256`, and a reviewed `allowed_actions` list. The live actions are
   `initialize`, `prepare`, `capture`, `send`, `checkpoint`, `launch`, `_serve`.
   `_serve` is the detached child. No current authorization is supplied by this build.
   Use the same absolute authorization path before and after reboot.
9. Review and record all actual launch commands. MP006 creates no autostart service.

Read-only local command (Windows build root):

```powershell
python -B .\mp006.py inspect
```

## Operator sequence after all required approvals

CLI: `python3 -B /home/seth/MULTI_PROVIDER_006/mp006.py ACTION` on Dell;
Windows uses `python -B .\mp006.py ACTION`. Mutable actions require
`--authorization ABSOLUTE_FILE`. Follow the steps one at a time, never as a batch.
Do not use `initialize` after the initial fresh-state setup.

1. `initialize` on Dell; `prepare --kind consume` on controller. Transfer required
   new identity/evidence copies without replacing existing evidence.
2. `launch --tag initial` on Dell. It uses R3-style `nohup`, `-u -B`, closed stdin,
   separate exclusive logs/PID files, a detached session and `/home/seth` cwd.
   Confirm the actual PID, log and listener. A launch acknowledgment is not execution.
3. `capture --label pre_consume --pid PID` on Dell, transfer snapshot to controller.
4. `send --kind consume --log CONTINUOUS_LOG` on controller. Capture `consumed`
   on Dell, transfer back, then `checkpoint --log CONTINUOUS_LOG` on controller.
5. Independently confirm idle; record boot ID; `marker --tag initial` on Dell.
   Start witness on OmniBook with verified target and a new file:

   ```powershell
   .\Watch-MP006Reachability.ps1 -Target 192.168.1.118 -OutputPath .\evidence\MP006_R01_RUN001\R01\reachability.jsonl
   ```

   Confirm initial success, preserve all initial evidence and SHA-256 inventories on
   OmniBook, and STOP for explicit physical-power approval. No command pulls power.
6. Operator disconnects Dell power, documents actual unplug/reconnect observations,
   and reconnects after a documented interval. No duration threshold applies.
7. After boot, leave provider stopped. FIRST run `recover-capture` on Dell. It copies
   raw ledger, snapshot and execution bytes (or records absence), inventories them,
   then checks for provider processes/listener, records boot ID, and verifies source.
   It does not import Provider A or validate/repair the copied state. If any step
   fails, preserve its partial folder and error; do not remove it or retry over it.
8. Copy raw recovery evidence plus its inventory and capture check to OmniBook.
   Compare hashes there before any provider start. If provider auto-started, record
   the breach; a later capture cannot establish a valid pre-start observation.
9. Run `validate-recovered` on the preserved copies. This uses the existing ledger
   verifier and compares all three raw files to the consumed evidence. Preserve missing/invalid state and stop for review;
   never repair it to advance the run. The final score also compares raw recovered
   bytes to the consumed copies, so reconciliation cannot conceal changed history.
10. `launch --tag recovered` against the SAME state. Save startup output, confirm
    actual PID/listener, `marker --tag recovered`, and capture `before_replay`.
11. Transfer snapshots. `send --kind replay --log CONTINUOUS_LOG`, capture
    `after_replay`, and transfer back. Replay reuses original package/header bytes.
12. `prepare --kind fresh`, capture `before_fresh`, transfer, `send --kind fresh`,
    capture `after_fresh`, transfer. Verify signed evidence and exact counts.
13. Stop witness with Ctrl+C after observed successful recovery. Preserve the log.
14. Create `power_procedure.json` in case evidence, with operator's actual values:
    `operator`, `disconnected_utc`, `reconnected_utc`, `physical_disconnect`, `power_loss_approved`,
    `idle_confirmed`, `initial_evidence_preserved_on_omnibook`, and
    `recovered_raw_preserved_on_omnibook`. Boolean attestations must reflect facts.
15. `score --log CONTINUOUS_LOG`. Final correlation rechecks late events. Missing
    artifacts produce INCOMPLETE; invalid artifacts produce HARNESS_ERROR. Preserve
    failures. Results and case inventory are exclusive writes; never overwrite them.

Process boot IDs establish a new OS boot; network observations establish observed
unavailability; operator attestation establishes physical disconnection. Video is
optional. Start ticks and PID ordering are not compared across boots.

If fresh execution cannot complete, preserve replay observations separately; an
incomplete score does not convert fail-closed recovery into overall PASS.
The score cannot establish R02/R03/R04, full-history rollback resistance, concurrent
double-spend resistance, or equivalent behavior elsewhere. On PASS its claim is
limited to the tested Provider A retaining consumed authority across this documented
power-loss/reboot cycle, rejecting replay and accepting separate fresh authority.
