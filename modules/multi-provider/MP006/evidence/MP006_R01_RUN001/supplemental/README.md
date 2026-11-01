# MP006-R01 — Supplemental Evidence

## Purpose

This directory preserves two additional artifacts from the MP006 physical power-loss experiment.

These records support review of the original session but remain separate from the frozen R01 scored evidence.

Neither artifact should replace or modify the original experiment records.

## Directory Contents

| File | Purpose |
|---|---|
| [recovered_validation.json](recovered_validation.json) | Post-recovery validation of Provider A's preserved consumption ledger |
| [association_recorder_final.jsonl](association_recorder_final.jsonl) | Complete association-recorder history, including session termination |

## Recovered State Validation

[recovered_validation.json](recovered_validation.json) preserves the result of the MP006 `validate-recovered` operation.

**Recorded status:** `PASS`

| Property | Recorded value |
|---|---|
| Provider | `PROVIDER_A` |
| Ledger entries | 1 |
| Ledger sequence | 1 |
| Original authorization present | Yes |
| Ledger chain valid | Yes |
| Snapshot matches ledger | Yes |

**Recovered ledger head:**

`7191f3b14e0641d7c197b547b61f41b36c9792593cf6b6b067c3980d2f596dba`

**Recovered ledger SHA-256:**

`a30acbf87e291fbacaac011452732a16d02457d4ff49beb49b5d1147bb0b17f7`

The recorded ledger identity matches the original consumption history and raw recovery capture.

### Validation Procedure

The MP006 implementation performs the following checks before reporting successful recovery validation:

1. Reads the raw consumption ledger captured before provider restart.
2. Reads the recovered spent-state snapshot.
3. Inspects the ledger structure and hash linkage.
4. Checks whether the original authorization remains recorded.
5. Verifies that the snapshot agrees with the ledger.
6. Compares all three recovered persistent files against their pre-interruption counterparts.

If the snapshot disagrees with the ledger or the recovered files differ from the preserved consumed state, validation fails.

The implementation does not repair the recovered state to produce a passing result.

Successful validation is a prerequisite for the recovered-provider launch procedure.

The underlying evidence remains in:

[Recovered raw state](../R01/recovered_before_start/)

## Final Association Recorder

[association_recorder_final.jsonl](association_recorder_final.jsonl) preserves the association recorder after session termination.

The file contains 10 records.

| Sequence | Record type | Provider | Event |
|---|---|---|---|
| 1 | `SESSION_START` | — | Session initialized |
| 2 | `SUBMISSION` | Provider B | `DENY auth_missing` |
| 3 | `SUBMISSION` | Provider A | `START` |
| 4 | `SUBMISSION` | Provider A | `COMPLETE` |
| 5 | `SUBMISSION` | Provider B | `DENY auth_missing` |
| 6 | `SUBMISSION` | Provider A | `DENY auth_spent` |
| 7 | `SUBMISSION` | Provider B | `DENY auth_missing` |
| 8 | `SUBMISSION` | Provider A | `START` |
| 9 | `SUBMISSION` | Provider A | `COMPLETE` |
| 10 | `SESSION_END` | — | Session terminated |

All eight submission records contain `sig_valid: true`.

Provider A supplied the scored execution and replay decisions.

Provider B's `auth_missing` denials are preserved as additional multi-provider observations.

### Session Termination

**Recorded termination timestamp:**

`2026-10-31T17:39:47.780720+00:00`

**Session ID:**

`MP006_R01_RUN001`

**Recorded submission count:** `8`

**Final record hash:**

`b3882880658623bab7f6d2d24b69a4931560756c1fc46b880b8d3924cba39f34`

The final record references the preceding record's hash.

All ten records contain sequential record numbers and consistent previous-record hash references.

These structural observations do not substitute for independent cryptographic verification of the complete recorder history.

## Comparison With Scored Recorder

The original scored recorder is preserved at:

[../R01/association_recorder.jsonl](../R01/association_recorder.jsonl)

It contains nine records.

The supplemental final recorder contains those same nine records, byte-for-byte, followed by the tenth `SESSION_END` record.

The original evidence is not changed.

From this directory, the nine-record prefix can be compared using:

```bash
head -n 9 association_recorder_final.jsonl | cmp - ../R01/association_recorder.jsonl
```

A zero exit status indicates that the compared bytes match.

The final recorder must not replace the original scored recorder because the original inventory and scoring evidence are tied to its preserved contents.

## Integrity and Preservation

This directory does not contain a separate `SHA256SUMS.txt`.

The two supplemental artifacts are not included in the original R01 SHA-256 inventory.

The original scored inventory remains:

[../R01/SHA256SUMS.txt](../R01/SHA256SUMS.txt)

Do not regenerate historical inventories or modify preserved evidence to incorporate these files.

## Evidence Boundary

The supplemental records provide additional support for two observations:

- Provider A's previously consumed authorization remained present in its recovered ledger before restart.
- The association recorder retained its original event history through orderly session termination.

The recovered-validation artifact is a result produced by the MP006 validation implementation.

The final recorder documents session closure but does not introduce another execution or replay test.

The authoritative scored result remains:

[../R01/case_results.json](../R01/case_results.json)

See the [session evidence documentation](../README.md) for the relationship between scored and supplemental evidence.
