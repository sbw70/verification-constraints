# MP006-R01 — Pre-Consumption State

## Purpose

This directory preserves Provider A's initial persistent state before the original authorization was consumed.

The capture establishes the starting condition against which the first authorized execution is evaluated.

## Directory Contents

| File | Purpose |
|---|---|
| [consume_ledger.jsonl](consume_ledger.jsonl) | Initial provider-local consumption ledger |
| [spent_state.json](spent_state.json) | Initial spent-authority snapshot |
| [execution.jsonl](execution.jsonl) | Preserved execution-log bytes |
| [snapshot.json](snapshot.json) | State metadata, ledger validation, hashes, and execution counts |
| [process.json](process.json) | Provider process, boot, source, and filesystem identity |
| [SHA256SUMS.txt](SHA256SUMS.txt) | Original integrity inventory |

## Initial Persistent State

The recorded state is:

| Property | Value |
|---|---|
| Ledger entries | 0 |
| Ledger sequence | 0 |
| Ledger head | `null` |
| Spent authorizations | 0 |
| Execution records | 0 |
| Original authorization consumed | No |
| Ledger validation | Valid |
| Snapshot matches ledger | Yes |

The consumption ledger is an empty, zero-byte file.

The spent-state snapshot contains:

```json
{
  "ledger_head": null,
  "ledger_seq": 0,
  "spent": {},
  "version": 1
}
```

This is the initial state produced by the frozen MP005 ledger initialization procedure.

The original authorization is identified in the capture metadata but is not present in the consumption ledger or spent-state snapshot.

## Execution Log

The preserved `execution.jsonl` file contains zero bytes.

The capture metadata records:

`"execution_log_exists": false`

This distinction matters.

The original provider execution log did not exist at the source path when the snapshot was taken.

The MP005 evidence harness preserved an empty file representing that absence.

The empty evidence file must not be interpreted as proof that the original execution-log file existed on the provider.

No execution records were present.

## Provider Process Identity

The capture identifies the original running Provider A instance.

| Property | Recorded value |
|---|---|
| Hostname | `Xer0trust-3` |
| Operating system | Linux |
| Provider PID | `113976` |
| Python version | 3.12.3 |
| Persistent filesystem | ext4 |
| Captured UTC | `2026-10-31T15:58:41.441263+00:00` |

**Boot identifier:**

`881b67af-b296-4908-9bc9-cb398860f244`

**Provider source SHA-256:**

`79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6`

The process record identifies the frozen MP005 Provider A implementation running under the MP006 adapter.

The persistent state directory was:

`/home/seth/MULTI_PROVIDER_006/state/MP006_R01_RUN001/provider_a/`

These identities are subsequently compared with the recovered provider process.

## Capture and Validation

The MP006 adapter obtains the provider process identity and invokes the frozen MP005 state-snapshot functions.

The snapshot implementation:

1. Reads the spent-state snapshot.
2. Preserves the execution-log contents or records its absence.
3. Reads and validates the consumption ledger.
4. Records file hashes, state paths, and authorization status.
5. Preserves the resulting metadata and process identity.

The independent ledger validator checks entry structure, sequence, hash linkage, and agreement with the materialized spent-state snapshot.

For this initial capture, the empty ledger and empty spent-authority map are consistent.

The original scorer evaluates this condition through its `fresh_genesis` and initial-consumption checks.

## Integrity

The original [SHA256SUMS.txt](SHA256SUMS.txt) contains five file entries.

Both empty evidence files have the SHA-256 digest:

`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`

To verify the original inventory, run from this directory:

```bash
sha256sum -c SHA256SUMS.txt
```

The README is additional documentation and is not part of the original evidence inventory.

Do not modify the original files or regenerate their historical hashes.

## Evidence Boundary

This directory establishes the recorded state before consumption.

It does not independently establish that an authorization was subsequently accepted, executed, or persisted.

Those observations are preserved in:

- [Initial request and boundary evidence](../send_consume/)
- [Post-consumption state](../consumed/)

See the [R01 evidence documentation](../README.md) for the complete experimental sequence.
