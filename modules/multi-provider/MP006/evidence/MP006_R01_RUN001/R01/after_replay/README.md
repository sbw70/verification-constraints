# MP006-R01 — Post-Replay State

## Purpose

This directory preserves Provider A's persistent state after replaying the original authorization following physical power loss and recovery.

The capture is used to determine whether replay caused an additional authorization consumption, changed persistent state, or produced another software execution.

## Directory Contents

| File | Purpose |
|---|---|
| [consume_ledger.jsonl](consume_ledger.jsonl) | Provider-local consumption ledger after replay |
| [spent_state.json](spent_state.json) | Materialized spent-authority snapshot |
| [execution.jsonl](execution.jsonl) | Provider-local execution history |
| [snapshot.json](snapshot.json) | Captured state metadata, hashes, and ledger validation |
| [process.json](process.json) | Recovered provider process and persistent-state identity |
| [SHA256SUMS.txt](SHA256SUMS.txt) | Original five-file integrity inventory |

## Recorded State

**Capture timestamp:**

`2026-10-31T17:02:33.678818+00:00`

| Property | Before replay | After replay |
|---|---:|---:|
| Ledger entries | 1 | 1 |
| Ledger sequence | 1 | 1 |
| Spent authorizations | 1 | 1 |
| Execution records | 1 | 1 |
| Original authorization spent | Yes | Yes |
| Snapshot matches ledger | Yes | Yes |

The consumption ledger, spent-state snapshot, and execution log are byte-identical to their corresponding files in [before_replay/](../before_replay/).

They also match the original persistent files preserved in [consumed/](../consumed/).

No additional consumption or execution record was observed.

## Persistent-State Integrity

The following SHA-256 digests remained unchanged across replay.

| File | SHA-256 |
|---|---|
| Consumption ledger | `a30acbf87e291fbacaac011452732a16d02457d4ff49beb49b5d1147bb0b17f7` |
| Spent-state snapshot | `4e67aff2218d05d88cac141702aabdbb8c460204472df0803ca3321d1c67a47e` |
| Execution log | `98f5616477144f0c91de7aebfac53dd2f3280a5573553cfbf01bc84be0310e65` |

The ledger retains its original head:

`7191f3b14e0641d7c197b547b61f41b36c9792593cf6b6b067c3980d2f596dba`

The original authorization remains recorded as consumed at ledger sequence 1.

The materialized snapshot agrees with the consumption ledger.

## Replay Denial

The associated [boundary evidence](../send_replay/boundary_records.json) contains one Provider A event:

| Field | Recorded value |
|---|---|
| Stage | `DENY` |
| Reason | `auth_spent` |
| Ledger sequence | 1 |
| Recorder sequence | 6 |
| Recorder signature-valid flag | `true` |

The event identifies the original authorization and existing ledger head.

No `START` or `COMPLETE` event was recorded for the replayed authorization.

The frozen MP005 verification code checks the provider signature, authorization identity, nonce, operation binding, and signing-key identity.

The MP006 scorer evaluates the denial alongside the preserved provider-local state.

The recorded replay checks passed.

## Process Continuity

The capture identifies the same recovered provider process used before replay.

| Property | Recorded value |
|---|---|
| Hostname | `Xer0trust-3` |
| PID | `1725` |
| Python version | 3.12.3 |
| Persistent filesystem | ext4 |

**Boot identifier:**

`aa810aed-0a27-4577-8580-43576daa4fd4`

**Provider source SHA-256:**

`79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6`

The process identity fields match those in `before_replay/process.json`.

The evidence therefore associates the before-and-after replay captures with the same recovered provider instance and persistent-state path.

## Integrity Verification

The original [SHA256SUMS.txt](SHA256SUMS.txt) inventories five evidence files.

From this directory:

```bash
sha256sum -c SHA256SUMS.txt
```

The README was added after the scored experiment and is not included in the original inventory.

Do not modify the preserved evidence or regenerate its historical hashes.

## Evidence Boundary

This directory supports the conclusion that replay did not alter the recorded consumption ledger, spent-authority snapshot, or execution history.

The signed `auth_spent` denial provides the corresponding provider-originated authorization decision.

Together, these records support the scored replay-safety result:

`REPLAY_REJECTED_WITHOUT_ADDITIONAL_CONSUMPTION_OR_EXECUTION`

The evidence establishes this result for the recorded replay attempt, not for every possible replay or storage-failure scenario.

The subsequent [fresh-authority test](../before_fresh/) evaluates whether the recovered provider can still execute a separate unused authorization.

See the [R01 evidence documentation](../README.md) for the complete experiment.
