# MP006-R01 — Recovered Persistent State

## Purpose

This directory preserves Provider A's persistent state after the physical power interruption and before the provider application was restarted.

The objective was to determine whether previously consumed authorization remained recorded on persistent storage after power restoration.

The capture preserves the original recovered bytes without reconstructing, repairing, or initializing provider state.

## Directory Contents

| File | Purpose |
|---|---|
| [provider_a_consume_ledger.jsonl](provider_a_consume_ledger.jsonl) | Original hash-linked authorization consumption ledger recovered from disk |
| [provider_a_spent_state.json](provider_a_spent_state.json) | Recovered materialized spent-authority snapshot |
| [provider_a_execution.jsonl](provider_a_execution.jsonl) | Recovered provider-local execution history |
| [raw_capture.json](raw_capture.json) | Original source paths, capture timestamp, file lengths, and SHA-256 digests |
| [SHA256SUMS.txt](SHA256SUMS.txt) | Integrity inventory for the four captured evidence files |

## Capture Procedure

The recovery capture was performed using the `recover-capture` action implemented in [mp006.py](../../../../mp006.py).

The implementation:

1. Reads the three persistent files directly from the provider's state directory.
2. Preserves their original bytes in a newly created evidence directory.
3. Records each file's source path, byte count, and SHA-256 digest.
4. Generates the local SHA-256 inventory.
5. Checks for an existing provider process or listener.
6. Records the recovered boot identifier and process-check result separately.

Raw preservation occurs before provider source verification, state parsing, or provider startup.

The capture uses exclusive file creation to avoid overwriting existing evidence.

Missing persistent files are recorded as absent rather than silently reconstructed.

The original persistent files are not modified by the capture routine.

## Recorded Recovery

**Capture timestamp:**

`2026-10-31T16:38:03.426647+00:00`

**Original state directory:**

`/home/seth/MULTI_PROVIDER_006/state/MP006_R01_RUN001/provider_a/`

All three expected persistent files were present.

| Persistent file | Bytes | Recorded SHA-256 |
|---|---:|---|
| Consumption ledger | 388 | `a30acbf87e291fbacaac011452732a16d02457d4ff49beb49b5d1147bb0b17f7` |
| Spent-state snapshot | 231 | `4e67aff2218d05d88cac141702aabdbb8c460204472df0803ca3321d1c67a47e` |
| Execution log | 338 | `98f5616477144f0c91de7aebfac53dd2f3280a5573553cfbf01bc84be0310e65` |

## Recovered Ledger

The recovered consumption ledger contains one entry.

Its recorded properties are:

- Provider: `PROVIDER_A`
- Ledger sequence: `1`
- Ledger entries: `1`
- Previously consumed authorization: present
- Ledger chain: valid

**Ledger head:**

`7191f3b14e0641d7c197b547b61f41b36c9792593cf6b6b067c3980d2f596dba`

The recovered spent-state snapshot identifies the same authorization as consumed.

Its ledger sequence and head agree with the recovered consumption ledger.

The recovered execution log contains the corresponding original software execution record.

## Comparison With Pre-Interruption Evidence

The recovered persistent files were compared with the corresponding files preserved in [consumed/](../consumed/).

| File | Comparison |
|---|---|
| Consumption ledger | Identical |
| Spent-state snapshot | Identical |
| Execution log | Identical |

The recovered ledger retains its original entry and head.

No additional consumption or execution record appears in the recovered state.

The original authorization's consumed status was therefore preserved across the observed interruption.

The separate [recovery_capture_check.json](../recovery_capture_check.json) records:

- Recovered boot ID: `aa810aed-0a27-4577-8580-43576daa4fd4`
- Provider stopped: `true`
- Check timestamp: `2026-10-31T16:38:03.468948+00:00`

The recovered boot identifier differs from the original provider boot identifier.

## Independent State Validation

The recovered state was subsequently evaluated using the frozen MP005 ledger-validation implementation.

The validation checks:

- Ledger entry structure and sequence.
- Previous-entry hash linkage.
- Entry hash correctness.
- Duplicate authorization identifiers.
- Spent-state agreement with the consumption ledger.
- Preservation of the original consumed authorization.

The recorded validation returned `PASS`.

The original validation receipt is preserved separately at:

[recovered_validation.json](../../supplemental/recovered_validation.json)

This receipt is supplemental evidence and is not part of this directory's original capture inventory.

## Integrity Verification

The original inventory is preserved in [SHA256SUMS.txt](SHA256SUMS.txt).

From this directory, run:

```bash
sha256sum -c SHA256SUMS.txt
```

The inventory covers the three persistent files and `raw_capture.json`.

The README was added after evidence collection and is not included in the original inventory.

Do not regenerate the inventory or alter the captured files to accommodate documentation.

## Limitations

This capture establishes the bytes observed on persistent storage at the time of collection.

It is not a forensic disk image or an independent hardware attestation.

The process inspection occurred after the raw files were captured. It does not establish that no provider process could have started and exited before inspection.

The capture does not independently prove the physical power-removal event. That procedure is documented separately in the experiment's operator and reachability records.

Preserving an intact consumption ledger does not establish resistance to an attacker replacing the entire persistent history.

The subsequent replay experiment tests whether the recovered provider continues enforcing the consumed authorization.

See the [R01 evidence documentation](../README.md) for the recorded replay and fresh-authority results.
