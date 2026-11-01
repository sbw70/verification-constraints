# MP006-R01 — Before Fresh Execution

## Purpose

This directory preserves Provider A's persistent state immediately before submitting a separate fresh authorization after power-loss recovery and successful replay denial.

The capture establishes two conditions:

1. The original authorization remains consumed.
2. The fresh authorization has not previously been consumed or executed.

## Directory Contents

| File | Purpose |
|---|---|
| [consume_ledger.jsonl](consume_ledger.jsonl) | Existing provider-local consumption history |
| [spent_state.json](spent_state.json) | Materialized spent-authority snapshot |
| [execution.jsonl](execution.jsonl) | Existing software execution history |
| [snapshot.json](snapshot.json) | State metadata, hashes, and fresh-authorization status |
| [process.json](process.json) | Recovered provider process and filesystem identity |
| [SHA256SUMS.txt](SHA256SUMS.txt) | Original five-file integrity inventory |

## Recorded State

**Capture timestamp:**

`2026-10-31T17:15:06.724982+00:00`

| Property | Recorded value |
|---|---|
| Provider | `PROVIDER_A` |
| Ledger entries | 1 |
| Ledger sequence | 1 |
| Spent authorizations | 1 |
| Total execution records | 1 |
| Original authorization spent | Yes |
| Fresh authorization spent | No |
| Fresh authorization execution count | 0 |
| Ledger chain valid | Yes |
| Snapshot matches ledger | Yes |

The existing ledger contains only the original authorization consumed before the physical power interruption.

The fresh authorization is absent from both the consumption ledger and the spent-state snapshot.

Although the execution log contains one record, that record belongs to the original authorization.

The fresh authorization has no matching execution record.

## Fresh Authorization Identity

The capture references the authorization preserved in [fresh/](../fresh/).

**Fresh authorization ID:**

`821ca36878ef72241d6bb02815ad5de8ce2e867f49d1807f6bf0cdd99ff24695`

**Original authorization ID:**

`0105b3696211a2f1e536e3b9f07d0c8688e6e05640fd50b1462bb864ece97a0c`

The identifiers are different.

The fresh authorization also has its own nonce, request representation, verification context, and operation binding.

The MP006 scorer checks that the fresh authorization is distinct and previously unspent before evaluating its subsequent execution.

## Continuity After Replay

The consumption ledger, spent-state snapshot, and execution log are byte-identical to their corresponding files in [after_replay/](../after_replay/).

Their SHA-256 digests remain:

| File | SHA-256 |
|---|---|
| Consumption ledger | `a30acbf87e291fbacaac011452732a16d02457d4ff49beb49b5d1147bb0b17f7` |
| Spent-state snapshot | `4e67aff2218d05d88cac141702aabdbb8c460204472df0803ca3321d1c67a47e` |
| Execution log | `98f5616477144f0c91de7aebfac53dd2f3280a5573553cfbf01bc84be0310e65` |

**Existing ledger head:**

`7191f3b14e0641d7c197b547b61f41b36c9792593cf6b6b067c3980d2f596dba`

The original consumption history remains intact.

No state advancement occurred between the replay-denial capture and this fresh-authorization baseline.

## Provider Process Identity

The capture identifies the same recovered provider instance used during replay.

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

The recorded hostname, boot identifier, PID, process start ticks, source identity, launch command, and state path match the recovered provider's preceding and subsequent captures.

## Integrity Verification

The original [SHA256SUMS.txt](SHA256SUMS.txt) inventories five evidence files.

From this directory:

```bash
sha256sum -c SHA256SUMS.txt
```

This README is additional documentation and is not included in the historical inventory.

Do not modify the original evidence or regenerate its hashes.

## Evidence Boundary

This directory establishes the fresh authorization's unspent status before submission.

It does not independently establish that the fresh authorization subsequently executed.

That determination requires:

- [Fresh request and signed boundary records](../send_fresh/)
- [Post-execution state](../after_fresh/)

See the [R01 evidence documentation](../README.md) for the complete experiment.
