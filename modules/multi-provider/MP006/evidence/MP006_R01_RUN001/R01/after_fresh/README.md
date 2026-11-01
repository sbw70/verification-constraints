# MP006-R01 — After Fresh Execution

## Purpose

This directory preserves Provider A's persistent state after executing a separate, previously unused authorization following physical power loss, recovery, and successful replay denial.

The capture establishes whether the recovered provider remains capable of accepting new authority without losing its previous consumption history.

## Directory Contents

| File | Purpose |
|---|---|
| [consume_ledger.jsonl](consume_ledger.jsonl) | Final hash-linked authorization consumption ledger |
| [spent_state.json](spent_state.json) | Final materialized spent-authority snapshot |
| [execution.jsonl](execution.jsonl) | Provider-local software execution history |
| [snapshot.json](snapshot.json) | State metadata, hashes, and ledger validation |
| [process.json](process.json) | Recovered provider process and filesystem identity |
| [SHA256SUMS.txt](SHA256SUMS.txt) | Original five-file integrity inventory |

## Recorded State

**Capture timestamp:**

`2026-10-31T17:22:21.189468+00:00`

| Property | Before fresh execution | After fresh execution |
|---|---:|---:|
| Ledger entries | 1 | 2 |
| Ledger sequence | 1 | 2 |
| Spent authorizations | 1 | 2 |
| Execution records | 1 | 2 |
| Fresh authorization spent | No | Yes |
| Fresh authorization executions | 0 | 1 |

The original authorization remains consumed.

The fresh authorization is added to the existing ledger and spent-state snapshot.

The recorded ledger chain remains valid, and the materialized snapshot agrees with the ledger.

## Ledger Continuity

**Fresh authorization ID:**

`821ca36878ef72241d6bb02815ad5de8ce2e867f49d1807f6bf0cdd99ff24695`

**Final ledger head:**

`b744c9c7182d82769e11a4e29394f463a2a0f93e3d80f5f5a2d4d5873a074a6d`

The second ledger entry:

- Identifies the fresh authorization and corresponding operation.
- Uses ledger sequence `2`.
- References the first entry's hash.
- Preserves the original entry unchanged.
- Produces a new ledger head consistent with the recorded snapshot.

The original authorization remains present in the spent-state map.

No previously consumed authority was restored or discarded.

## Execution Evidence

[execution.jsonl](execution.jsonl) contains two software execution records.

The first belongs to the original authorization, executed before power loss.

The second belongs to the fresh authorization.

**Fresh execution timestamp:**

`2026-10-31T17:20:43.482145+00:00`

The corresponding [signed boundary records](../send_fresh/boundary_records.json) contain:

| Recorder sequence | Stage | Ledger sequence |
|---|---|---:|
| 8 | `START` | 2 |
| 9 | `COMPLETE` | 2 |

Both records identify the fresh authorization and final ledger head.

The recorder marks both signatures as valid.

The MP006 scorer independently checks authorization identity, ledger advancement, hash linkage, and execution count.

All twelve fresh-execution checks returned `true`.

### Execution Sequence Interpretation

Both execution records contain:

`"local_execution_seq": 1`

This is expected because the counter is process-local and restarted when Provider A restarted after power loss.

The persistent consumption ledger maintains continuity independently of that counter.

Process-local execution sequence continuity across reboot is not a scored property.

## Provider Identity

The final capture identifies the same recovered provider process used during replay.

| Property | Recorded value |
|---|---|
| Hostname | `Xer0trust-3` |
| PID | `1725` |
| Boot identifier | `aa810aed-0a27-4577-8580-43576daa4fd4` |
| Python version | 3.12.3 |
| Persistent filesystem | ext4 |

**Provider source SHA-256:**

`79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6`

The process identity, source hash, launch command, and persistent-state path match the preceding [before_fresh/](../before_fresh/) capture.

## Final Persistent-State Hashes

| File | SHA-256 |
|---|---|
| Consumption ledger | `4ecbacd1fd75ab974e055cdb1c2213c8e4fbfd0b4a2cc6bcadba5e1f5fca628f` |
| Spent-state snapshot | `7c741dc13f7d2582330adc45d8a0abc141152f2f6d64dc90b07c9683c4a234c3` |
| Execution log | `c807868d280ccb16aee01550d2b0b642602951c0228be651771447f716c78047` |

The hashes differ from the pre-execution state because the provider recorded one additional authorization consumption and execution.

## Integrity Verification

The original [SHA256SUMS.txt](SHA256SUMS.txt) inventories five evidence files.

From this directory:

```bash
sha256sum -c SHA256SUMS.txt
```

This README is additional documentation and is not included in the historical evidence inventory.

Do not modify the original files or regenerate their hashes.

## Evidence Boundary

This directory supports the observed successful execution of one fresh authorization after provider recovery.

Together with the unchanged replay records, it demonstrates that the recovered provider:

- Continued rejecting previously consumed authority.
- Preserved its original consumption history.
- Accepted and consumed separate fresh authority.
- Recorded one additional software execution.

The evidence does not establish hardware-level execution or behavior under every possible storage failure.

The official result is preserved in [case_results.json](../case_results.json).

See the [R01 evidence documentation](../README.md) for the complete experiment.
