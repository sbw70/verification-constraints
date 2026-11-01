# MP006 — Evidence

This directory contains the recorded evidence for MP006-R01, a physical power-loss and authority-persistence experiment using Provider A.

The test examined whether an authorization consumed before complete power loss remained spent after the provider recovered, and whether a separate fresh authorization remained executable.

## Evidence Structure

### [MP006_R01_RUN001/R01/](MP006_R01_RUN001/R01/)

The scored experiment record.

| Directory or file | Contents |
|---|---|
| `original/` | Original authorization, request, identity, and issuance records. |
| `fresh/` | Separate fresh authorization and associated issuance records. |
| `pre_consume/` | Provider state before initial consumption. |
| `consumed/` | Provider state after initial authorized execution. |
| `recovered_before_start/` | Raw persistent state recovered after power restoration, before restarting Provider A. |
| `before_replay/` and `after_replay/` | State captures surrounding replay of the original authorization. |
| `before_fresh/` and `after_fresh/` | State captures surrounding execution of the fresh authorization. |
| `send_consume/` | Preserved initial request, relay response, and signed boundary records. |
| `send_replay/` | Preserved replay request, relay response, and signed denial. |
| `send_fresh/` | Preserved fresh request, relay response, and signed boundary records. |
| `runtime/` | Initial and recovered provider runtime logs and process records. |
| `reachability.jsonl` | Independent network reachability observations during the experiment. |
| `association_preserved.jsonl` | Preserved association recorder evidence used for scoring. |
| `power_procedure.json` | Operator confirmations and recorded power-interruption observations. |
| `recovery_capture_check.json` | Confirmation that recovered state was captured before provider restart. |
| `case_results.json` | Official scorer output and individual verification checks. |
| `SHA256SUMS.txt` | SHA-256 inventory for the preserved scored evidence. |

### [MP006_R01_RUN001/supplemental/](MP006_R01_RUN001/supplemental/)

Contains two separately preserved artifacts:

- `association_recorder_final.jsonl` — Final recorder log, including the orderly session-ending record appended after preservation of the scored evidence.
- `recovered_validation.json` — Original post-recovery ledger-validation receipt from the Dell provider.

These supplemental files are distinct from the original scored evidence inventory.

## Recorded Outcome

The official scorer returned:

**Status:** `PASS`

**Safety result:** `REPLAY_REJECTED_WITHOUT_ADDITIONAL_CONSUMPTION_OR_EXECUTION`

The recorded evidence establishes that:

- The original authorization executed once before power loss.
- The recovered persistent ledger retained the consumed authorization.
- Replaying that authorization produced a signed `auth_spent` denial.
- Replay caused no additional consumption or execution.
- A separate fresh authorization executed once after recovery.

The detailed machine-readable checks are preserved in [case_results.json](MP006_R01_RUN001/R01/case_results.json).

## Evidence Integrity

The scored evidence contains a SHA-256 inventory.

From `evidence/`, verify it with:

    cd MP006_R01_RUN001/R01
    sha256sum -c SHA256SUMS.txt

The original scored archive was independently verified with **79/79 inventoried files matching**.

The supplemental recorder and validation artifacts were collected separately and verified against their original sources.

Do not modify recorded artifacts or historical hash inventories.

## Evidence Limitations

The independent reachability witness recorded network disconnection and recovery. The exact physical unplugging and reconnection timestamps were not recorded.

The scorer explicitly reports:

`"timestamp_comparisons_scored": false`

The evidence documents one completed physical power-loss experiment. It does not establish behavior under every possible interruption, storage failure, or adversarial rollback condition.

## Related Implementation

- [MP006 implementation](../mp006.py)
- [Operating procedure](../OPERATING_PROCEDURE.md)
- [MP006 configuration](../configs/MP006_R01.json)
