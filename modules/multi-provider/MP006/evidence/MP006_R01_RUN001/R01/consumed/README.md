# MP006-R01 — Consumed Authorization State

## Purpose

This directory preserves Provider A's persistent state after the original authorization was consumed and executed, but before the physical power interruption.

It establishes the durable consumption history that must survive power loss and remain enforceable after recovery.

## Directory Contents

| File | Purpose |
|---|---|
| [consume_ledger.jsonl](consume_ledger.jsonl) | Provider-local hash-linked consumption ledger |
| [spent_state.json](spent_state.json) | Materialized spent-authority snapshot |
| [execution.jsonl](execution.jsonl) | Provider-local software execution record |
| [snapshot.json](snapshot.json) | Captured state metadata, hashes, and ledger validation |
| [process.json](process.json) | Original provider process, boot, source, and filesystem identity |
| [SHA256SUMS.txt](SHA256SUMS.txt) | Original five-file integrity inventory |

## Recorded State

The capture was completed on October 31, 2026.

**Capture timestamp:**

`2026-10-31T16:15:03.161642+00:00`

| Property | Recorded value |
|---|---|
| Provider | `PROVIDER_A` |
| Ledger entries | 1 |
| Ledger sequence | 1 |
| Spent authorizations | 1 |
| Execution records | 1 |
| Original authorization present | Yes |
| Ledger chain valid | Yes |
| Snapshot matches ledger | Yes |
| Matching execution count | 1 |

The initial state contained no consumed authorizations or execution records.

This capture records the first successful authorization consumption and corresponding software execution.

## Consumption Ledger

The ledger contains one entry for the original authorization.

**Authorization ID:**

`0105b3696211a2f1e536e3b9f07d0c8688e6e05640fd50b1462bb864ece97a0c`

**Ledger head:**

`7191f3b14e0641d7c197b547b61f41b36c9792593cf6b6b067c3980d2f596dba`

The entry has:

- Ledger sequence `1`.
- A null previous-entry hash, identifying the first entry.
- The original authorization identifier and nonce.
- The associated operation identifier.
- A SHA-256 entry hash calculated over the canonical entry representation.

The frozen MP005 provider implementation appends the consumption record and calls `fsync` before proceeding to execution.

The consumption ledger is authoritative for reconstruction of spent-authority state.

## Spent-State Snapshot

The materialized snapshot records the original authorization as consumed.

Its ledger sequence and head match the consumption ledger.

The snapshot contains one spent authorization, bound to the original authorization nonce.

The independent ledger validator reported agreement between the ledger and snapshot.

## Execution Evidence

[execution.jsonl](execution.jsonl) contains one software execution record.

The record identifies:

- Provider `PROVIDER_A`.
- The original authorization.
- The corresponding operation identifier.
- Local execution sequence `1`.
- Result `executed`.

The preserved execution record was written at:

`2026-10-31T16:13:48.525160+00:00`

The associated [signed boundary records](../send_consume/boundary_records.json) contain:

- `START`, recorder sequence `3`.
- `COMPLETE`, recorder sequence `4`.

Both events identify ledger sequence `1` and the same ledger head.

These observations support the recorded software execution. They are not independent hardware-execution attestation.

## Provider Process Identity

The capture identifies the original provider process.

| Property | Recorded value |
|---|---|
| Hostname | `Xer0trust-3` |
| PID | `113976` |
| Python version | 3.12.3 |
| Persistent filesystem | ext4 |
| Provider source | Frozen MP005 Provider A |

**Boot identifier:**

`881b67af-b296-4908-9bc9-cb398860f244`

**Provider source SHA-256:**

`79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6`

The process identity matches the original [pre-consumption capture](../pre_consume/).

The recorded state directory was:

`/home/seth/MULTI_PROVIDER_006/state/MP006_R01_RUN001/provider_a/`

## Pre-Interruption Checkpoint

After consumption was established, MP006 recorded an operator checkpoint.

The separate [operator_checkpoint.json](../operator_checkpoint.json) contains:

`AWAITING_EXPLICIT_POWER_APPROVAL`

The checkpoint was recorded at:

`2026-10-31T16:20:23.500002+00:00`

It references the same original boot identifier.

The checkpoint documents readiness for operator review. It is not, by itself, evidence that physical power was removed.

## Recovery Comparison

The three persistent files in this directory provide the reference state for the subsequent recovery comparison.

The corresponding files in [recovered_before_start/](../recovered_before_start/) match their recorded SHA-256 digests.

| Persistent file | SHA-256 |
|---|---|
| Consumption ledger | `a30acbf87e291fbacaac011452732a16d02457d4ff49beb49b5d1147bb0b17f7` |
| Spent-state snapshot | `4e67aff2218d05d88cac141702aabdbb8c460204472df0803ca3321d1c67a47e` |
| Execution log | `98f5616477144f0c91de7aebfac53dd2f3280a5573553cfbf01bc84be0310e65` |

The recovered files preserve the original consumption and execution history.

## Integrity

The original [SHA256SUMS.txt](SHA256SUMS.txt) inventories five files.

From this directory, verify the inventory using:

```bash
sha256sum -c SHA256SUMS.txt
```

This README was added after evidence collection and is not included in the historical inventory.

Do not modify the original evidence or regenerate its SHA-256 inventory.

## Evidence Boundary

This directory establishes the recorded consumed state before power interruption.

It does not independently prove that the state survived power loss or that replay was subsequently denied.

Those properties are evaluated using the recovered persistent files, replay evidence, and final scorer.

See the [R01 evidence documentation](../README.md) for the complete experimental record.
