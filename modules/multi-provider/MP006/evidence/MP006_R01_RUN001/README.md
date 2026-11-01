# MP006_R01_RUN001 — Session Evidence

## Purpose

This directory preserves the evidence from MP006's first physical power-loss authority-persistence experiment, conducted on October 31, 2026.

The session tested Provider A's ability to retain consumed authorization state after complete power loss and recovery.

The directory separates the original scored evidence from supplemental artifacts preserved independently.

## Directory Structure

| Directory | Contents |
|---|---|
| [R01/](R01/) | Original scored experiment, including state captures, authorization artifacts, execution records, signed boundary observations, process identities, and scoring results. |
| [supplemental/](supplemental/) | Additional preserved records supporting review of the original experiment. |

## Original Scored Evidence

The [R01 directory](R01/) contains the evidence evaluated by the MP006 scorer.

Its principal records include:

- [case_results.json](R01/case_results.json) — Official scoring result and individual verification checks.
- [SHA256SUMS.txt](R01/SHA256SUMS.txt) — SHA-256 inventory covering 79 scored evidence files.
- [recovered_before_start/](R01/recovered_before_start/) — Raw persistent state captured after power restoration and before provider restart.
- [association_recorder.jsonl](R01/association_recorder.jsonl) — Preserved signed boundary-event observations.
- [power_procedure.json](R01/power_procedure.json) — Operator-confirmed physical interruption and recovery information.
- [reachability.jsonl](R01/reachability.jsonl) — Independent network reachability observations.

The scorer returned:

**Status:** `PASS`

**Safety result:** `REPLAY_REJECTED_WITHOUT_ADDITIONAL_CONSUMPTION_OR_EXECUTION`

The recorded ledger progressed from zero entries to one after initial authorization consumption.

After recovery and replay, the ledger and execution records remained unchanged.

Execution of a separate fresh authorization advanced the ledger to sequence 2.

The association recorder also contains Provider B `auth_missing` denials associated with forwarded requests. Provider B was not the scored execution target.

## Supplemental Evidence

The [supplemental directory](supplemental/) contains two additional artifacts.

### recovered_validation.json

[View file](supplemental/recovered_validation.json)

Preserves the original post-recovery ledger-validation result from the Dell provider.

It records:

- `status: PASS`
- One recovered ledger entry.
- A valid ledger chain.
- The original authorization present in the ledger.
- Agreement between the recovered spent-state snapshot and consumption ledger.

### association_recorder_final.jsonl

[View file](supplemental/association_recorder_final.jsonl)

Preserves the association recorder's final log after orderly session shutdown.

The original scored recorder evidence contains nine records:

- One `SESSION_START`.
- Eight signed boundary submissions.

The final recorder log contains those same records followed by a tenth record, `SESSION_END`.

The supplemental final log must not replace the original recorder evidence in the scored inventory.

## Evidence Integrity

The original R01 inventory contains 79 SHA-256 entries.

From the `R01/` directory, verify the inventoried files using:

```bash
sha256sum -c SHA256SUMS.txt
```

The supplemental files are not included in that inventory.

They were preserved and verified separately against their source records.

Do not alter the original evidence, historical inventories, or recorded scoring output.

## Interpretation

The recorded evidence supports the conclusion that Provider A retained the original authorization's consumed status across the observed physical power interruption.

The replay was denied without another consumption or execution.

The independent reachability witness recorded loss and restoration of network connectivity. The exact physical disconnection and reconnection times were not recorded.

The scorer did not evaluate timestamp ordering:

`"timestamp_comparisons_scored": false`

The experiment establishes the observed result for this specific session, implementation, and environment.

It does not establish resistance to arbitrary replacement of persistent history or every possible power-interruption failure mode.

See the [parent evidence documentation](../README.md) for navigation across the published MP006 evidence.
