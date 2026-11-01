# MP006-R01 — Before Replay

## Purpose

This directory preserves Provider A's persistent state and process identity after power restoration and provider restart, immediately before replaying the original authorization.

The capture establishes whether the recovered provider recognizes the previously consumed authorization before receiving the replay request.

## Directory Contents

| File | Purpose |
|---|---|
| [consume_ledger.jsonl](consume_ledger.jsonl) | Recovered provider-local consumption ledger |
| [spent_state.json](spent_state.json) | Recovered spent-authority snapshot |
| [execution.jsonl](execution.jsonl) | Preserved execution history |
| [snapshot.json](snapshot.json) | Ledger validation, state hashes, authorization status, and execution counts |
| [process.json](process.json) | Recovered provider process, boot, source, and filesystem identity |
| [SHA256SUMS.txt](SHA256SUMS.txt) | Original five-file integrity inventory |

## Recorded State

**Capture timestamp:**

`2026-10-31T16:58:07.848338+00:00`

| Property | Value |
|---|---|
| Provider | `PROVIDER_A` |
| Ledger entries | 1 |
| Ledger sequence | 1 |
| Spent authorizations | 1 |
| Execution records | 1 |
| Original authorization present | Yes |
| Ledger chain valid | Yes |
| Snapshot matches ledger | Yes |

The original authorization remains recorded as consumed.

**Ledger head:**

`7191f3b14e0641d7c197b547b61f41b36c9792593cf6b6b067c3980d2f596dba`

The consumption ledger, spent-state snapshot, and execution log match the corresponding files preserved in [consumed/](../consumed/).

No additional consumption or execution occurred between the original state capture and this recovered-state capture.

## Recovered Process Identity

The capture identifies the running Provider A instance after reboot.

| Property | Recorded value |
|---|---|
| Hostname | `Xer0trust-3` |
| PID | `1725` |
| Python version | 3.12.3 |
| Persistent filesystem | ext4 |
| Provider source | Frozen MP005 Provider A |

**Recovered boot identifier:**

`aa810aed-0a27-4577-8580-43576daa4fd4`

**Provider source SHA-256:**

`79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6`

The original provider process used PID `113976` under a different boot identifier.

The recovered process retained the same hostname, provider source hash, launch command, working directory, and persistent-state path.

The MP006 scorer evaluates these identities through its recovery checks.

## Persistent-State Continuity

The three persistent files retain their original SHA-256 values.

| File | SHA-256 |
|---|---|
| Consumption ledger | `a30acbf87e291fbacaac011452732a16d02457d4ff49beb49b5d1147bb0b17f7` |
| Spent-state snapshot | `4e67aff2218d05d88cac141702aabdbb8c460204472df0803ca3321d1c67a47e` |
| Execution log | `98f5616477144f0c91de7aebfac53dd2f3280a5573553cfbf01bc84be0310e65` |

The recovered ledger contains the original authorization at sequence 1.

The snapshot agrees with the ledger, and the execution log retains the original software execution record.

The same persistent history was previously preserved in [recovered_before_start/](../recovered_before_start/), before provider startup.

## Integrity

The original [SHA256SUMS.txt](SHA256SUMS.txt) inventories five evidence files.

From this directory:

```bash
sha256sum -c SHA256SUMS.txt
```

This README is additional documentation and is not included in the historical inventory.

Do not modify the preserved evidence or regenerate its hashes.

## Evidence Boundary

This capture establishes the provider's recorded state before replay.

It does not independently establish whether the subsequent replay was accepted or rejected.

That determination requires the signed denial and unchanged persistent-state evidence preserved in:

- [Replay request and boundary records](../send_replay/)
- [Post-replay state](../after_replay/)

See the [R01 evidence documentation](../README.md) for the complete experiment.
