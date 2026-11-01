# MP006-R01 — Scored Evidence

## Purpose

This directory contains the original scored evidence for the MP006 physical power-loss experiment conducted October 31, 2026.

The experiment evaluated whether Provider A retained previously consumed authorization state after power removal, reboot, and recovery.

The evidence records the original execution, persistent-state recovery, exact authorization replay, and subsequent fresh-authority execution.

## Evidence Sequence

| Stage | Directory | Evidence |
|---|---|---|
| 1 | [original/](original/) | Original provider-signed authorization, request, identity, and issuance records |
| 2 | [pre_consume/](pre_consume/) | Initial empty consumption ledger, spent-state snapshot, execution log, and process identity |
| 3 | [send_consume/](send_consume/) | Preserved original request, relay response, recorder cursor, and signed boundary records |
| 4 | [consumed/](consumed/) | Persistent state after the first authorized execution |
| 5 | [recovered_before_start/](recovered_before_start/) | Raw persistent files recovered after power restoration, before provider startup |
| 6 | [before_replay/](before_replay/) | Recovered provider state immediately before replay |
| 7 | [send_replay/](send_replay/) | Preserved replay request and signed `auth_spent` denial |
| 8 | [after_replay/](after_replay/) | Persistent state following the rejected replay |
| 9 | [fresh/](fresh/) | Separate newly issued authorization and request |
| 10 | [before_fresh/](before_fresh/) | Recovered provider state before fresh authorization execution |
| 11 | [send_fresh/](send_fresh/) | Preserved fresh request and signed execution boundary records |
| 12 | [after_fresh/](after_fresh/) | Final persistent state after successful fresh execution |

The provider's initial and recovered runtime records are preserved separately in [runtime/](runtime/).

## Persistent-State Records

The state-capture directories contain five principal files:

| File | Function |
|---|---|
| `consume_ledger.jsonl` | Provider-local hash-linked authorization consumption history |
| `spent_state.json` | Materialized spent-authority snapshot |
| `execution.jsonl` | Provider-local software execution records |
| `snapshot.json` | Captured state metadata, hashes, ledger validation, and execution counts |
| `process.json` | Provider process, boot, source, and persistent-state identity |

Each state capture also contains its own `SHA256SUMS.txt`.

### Recorded State Transitions

| Capture | Ledger entries | Spent authorizations | Execution records |
|---|---:|---:|---:|
| `pre_consume` | 0 | 0 | 0 |
| `consumed` | 1 | 1 | 1 |
| `before_replay` | 1 | 1 | 1 |
| `after_replay` | 1 | 1 | 1 |
| `before_fresh` | 1 | 1 | 1 |
| `after_fresh` | 2 | 2 | 2 |

The captured ledger and execution SHA-256 values remain unchanged between `consumed` and `after_replay`.

After fresh execution, the ledger contains two hash-linked entries, and the spent-state snapshot contains both authorization identifiers.

The provider's process-local execution sequence restarts after reboot. Process-local sequence continuity across boots is not a scored property.

## Recovery Evidence

### Power-Interruption Records

[operator_checkpoint.json](operator_checkpoint.json) records the original provider boot identifier and the checkpoint awaiting explicit physical power approval.

[power_procedure.json](power_procedure.json) records operator confirmation of physical disconnection, idle conditions, authorization, and evidence preservation.

[reachability.jsonl](reachability.jsonl) contains 3,297 network observations from the independent reachability witness.

The first recorded network timeout occurred at:

`2026-10-31T16:34:15Z`

The first recorded successful response after the interruption occurred at:

`2026-10-31T16:37:07Z`

These are network observations, not exact physical power-disconnection or reconnection timestamps.

### Raw Recovery Capture

[recovered_before_start/](recovered_before_start/) contains:

- `provider_a_consume_ledger.jsonl`
- `provider_a_spent_state.json`
- `provider_a_execution.jsonl`
- `raw_capture.json`
- `SHA256SUMS.txt`

The MP006 adapter captures the original persistent bytes before importing or starting the provider.

The recovered consumption ledger contains one valid entry for the previously consumed authorization.

The three recovered persistent files match the corresponding files preserved in `consumed/`.

[recovery_capture_check.json](recovery_capture_check.json) records that Provider A was stopped when the recovery capture check completed.

The recovered boot identifier differs from the original boot identifier.

These observations support recovery continuity. The process check does not prove that no provider process could have started and exited before inspection.

## Signed Boundary Evidence

The request evidence is preserved in three directories.

### Initial Consumption

[send_consume/](send_consume/) contains verified Provider A boundary records:

- `START`
- `COMPLETE`

Both identify ledger sequence 1.

### Original Authorization Replay

[send_replay/](send_replay/) contains one verified Provider A boundary record:

- `DENY`
- Reason: `auth_spent`
- Ledger sequence: 1

No additional `START` or `COMPLETE` event was recorded for the replayed authorization.

The before-and-after replay snapshots preserve identical ledger, spent-state, and execution hashes.

### Fresh Authorization

[send_fresh/](send_fresh/) contains verified Provider A boundary records:

- `START`
- `COMPLETE`

Both identify ledger sequence 2.

The fresh authorization has a different authorization identifier and advances the existing consumption ledger by one entry.

### Association Recorder

[association_recorder.jsonl](association_recorder.jsonl) preserves the scored recorder history.

[association_preserved.jsonl](association_preserved.jsonl) contains the same preserved records.

The scored recorder history contains:

- One `SESSION_START`.
- Five Provider A boundary submissions.
- Three Provider B `auth_missing` denials.

All eight submissions are marked as signature-valid by the recorder.

Provider B's denials are separate observations. Provider B was not the scored execution target.

The original scored recorder log does not contain the subsequently recorded `SESSION_END`. That additional record is preserved outside this directory.

## Runtime Evidence

[runtime/](runtime/) contains:

- `initial.log`
- `initial.pid.json`
- `recovered.log`
- `recovered.pid.json`
- `SHA256SUMS.txt`

The original provider process used PID `113976`.

The recovered provider process used PID `1725`.

The recorded boot identifiers differ, while the provider source SHA-256 remains unchanged:

`79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6`

The recovered provider log records one `auth_spent` denial followed by successful execution of the separate fresh authorization.

## Scoring

The official machine-readable result is:

[case_results.json](case_results.json)

**Status:** `PASS`

**Safety result:**

`REPLAY_REJECTED_WITHOUT_ADDITIONAL_CONSUMPTION_OR_EXECUTION`

The scorer evaluates initial consumption, recovery identity, persistent-state continuity, replay denial, fresh execution, operator procedure evidence, and preserved request integrity.

The result is specific to this recorded run.

The scorer does not evaluate timestamp ordering:

`"timestamp_comparisons_scored": false`

HTTP `204` responses are not treated as proof of execution. Execution assertions require corresponding signed provider boundary records and provider-local persistent evidence.

## Integrity

[SHA256SUMS.txt](SHA256SUMS.txt) is the original scored evidence inventory.

It contains 79 file entries.

To verify the inventoried files, run from this directory:

```bash
sha256sum -c SHA256SUMS.txt
```

The inventory preserves the original recorded evidence identities.

Any README added after scoring is documentation, not part of the original 79-file scored inventory.

Do not regenerate the historical inventory or modify the original evidence to accommodate documentation.

## Scope and Limitations

The evidence supports persistence of consumed authority across the observed physical power interruption and subsequent provider recovery.

It does not establish protection against arbitrary rollback of the complete consumption history, every possible storage failure, or independent hardware attestation of execution.

See the [session documentation](../README.md) for the distinction between scored evidence and supplemental records.
