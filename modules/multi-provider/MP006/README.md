# MP006 — Physical Power-Loss Authority Persistence

## Purpose

MP006 evaluates whether provider-controlled, single-use execution authority remains consumed after complete physical power loss and host recovery.

The experiment extends MP005's process-restart durability testing to a different failure condition.

**Primary question:**

Can a provider lose power, restart using its existing persistent state, and continue rejecting previously consumed authority without preventing separately authorized fresh execution?

The experiment tests that property without transferring authorization or execution authority to the NUVL intermediary.

## Recorded Result

**Session:** `MP006_R01_RUN001`

**Date:** October 31, 2026

**Target:** Provider A — Dell Linux Mint

**Status:** `PASS`

**Safety result:**

`REPLAY_REJECTED_WITHOUT_ADDITIONAL_CONSUMPTION_OR_EXECUTION`

### Observed Behavior

| Phase | Recorded result |
|---|---|
| Initial state | No consumed authorizations |
| Original authorization | Accepted and executed once |
| Initial consumption ledger | Advanced to sequence 1 |
| Physical power interruption | Operator-attested; network loss independently observed |
| Host recovery | Different boot ID; original persistent history recovered |
| Original authorization replay | Denied — `auth_spent` |
| Replay execution | No additional execution |
| Replay consumption ledger | Unchanged at sequence 1 |
| Separate fresh authorization | Accepted and executed once |
| Final consumption ledger | Advanced to sequence 2 |

The scorer reported PASS across all seven verification groups:

- Initial consumption.
- Recovery.
- State continuity.
- Replay rejection.
- Fresh execution.
- Physical-interruption procedure.
- Preserved request integrity.

[View scored results](evidence/MP006_R01_RUN001/R01/case_results.json)

## Experimental Method

The experiment followed a controlled sequence.

### 1. Establish Fresh State

Provider A started with a new, isolated consumption ledger and spent-authority snapshot.

A provider-issued authorization was prepared for one operation.

### 2. Consume Authority

The original authorization was submitted through the NUVL relay.

Provider A validated the authorization, recorded its consumption, executed once, and emitted signed boundary events.

The consumption ledger advanced to sequence 1.

### 3. Interrupt Power

The provider was confirmed idle.

Initial state and execution evidence were independently preserved.

The operator physically disconnected the Dell's power.

An independent reachability witness recorded the transition from reachable to unreachable.

### 4. Restore and Capture

After power restoration, the persistent state was copied before Provider A restarted.

The raw capture preserved:

- Consumption-ledger bytes.
- Spent-state snapshot bytes.
- Execution-log bytes.
- SHA-256 identities.
- Recovery boot identity.

The preserved files were checked against the pre-interruption evidence.

The capture process did not repair the persistent state.

### 5. Replay Original Authority

Provider A restarted using the existing persistent state.

The original authorization was submitted again using its preserved bytes.

Provider A emitted a signed denial identifying the authorization as already spent.

The ledger, spent-state snapshot, and execution log remained unchanged.

### 6. Execute Fresh Authority

A separate authorization was issued for a new operation.

Provider A accepted and executed it once.

The consumption ledger advanced to sequence 2 while preserving the original consumption history.

## Directory Structure

| Path | Contents |
|---|---|
| [mp006.py](mp006.py) | MP006 orchestration, recovery capture, verification, and scoring |
| [test_local.py](test_local.py) | Offline implementation tests |
| [Watch-MP006Reachability.ps1](Watch-MP006Reachability.ps1) | Independent network reachability witness |
| [OPERATING_PROCEDURE.md](OPERATING_PROCEDURE.md) | Original operator procedure and approval checkpoints |
| [SOURCE_REVIEW.md](SOURCE_REVIEW.md) | Pre-deployment source inspection and limitations |
| [LOCAL_VALIDATION.json](LOCAL_VALIDATION.json) | Historical offline validation record |
| [configs/](configs/) | Reviewed MP006 configuration |
| [authorizations/](authorizations/) | Explicit operator authorization |
| [reference/](reference/) | Frozen MP005 implementation dependencies |
| [manifests/](manifests/) | Historical build and deployment inventories |
| [evidence/](evidence/) | Completed experiment evidence |

Each directory contains more detailed documentation.

## Implementation

MP006 uses a narrow Python adapter around the frozen MP005 implementation.

The adapter adds:

- Experiment-specific paths and configuration.
- Operator authorization checks.
- Controlled provider launch and identity capture.
- Pre-start raw recovery preservation.
- Changed-boot verification.
- Physical-interruption evidence checks.
- Replay and fresh-execution scoring.
- Evidence inventories and result classification.

The underlying provider authorization and persistence functions remain unchanged.

### Frozen Provider Identity

**MP005 reference commit:**

`73713f6e9ed9c95251cc69ec88ef816cab771ac0`

**Provider A SHA-256:**

`79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6`

The adapter verifies the frozen source and harness identities.

It does not replace Provider A's authorization, signature-verification, durable-consumption, or execution methods.

See [Frozen MP005 reference](reference/MP005/).

## Authority Separation

The experiment preserves four distinct responsibilities.

**Provider A**

Controls authorization validation, consumption, replay enforcement, and execution.

**NUVL intermediary**

Forwards provider-specific requests without independently authorizing execution.

**Association recorder**

Receives and verifies signed provider boundary events.

**MP006 harness**

Controls the experimental procedure and evaluates recorded evidence.

The operator authorization permits specified test operations.

It does not replace provider-issued execution authorization.

Neither the relay nor the recorder acquires authority to create, enlarge, or reuse provider authorization.

### Provider B

The relay continued forwarding to both configured providers.

Provider B produced `auth_missing` denials because the R01 requests did not include authorization for Provider B.

Provider B was not the scored execution target.

Its observations do not establish power-loss durability for Provider B.

## Evidence

The original scored evidence is preserved at:

[evidence/MP006_R01_RUN001/R01/](evidence/MP006_R01_RUN001/R01/)

### Primary Records

| Evidence | Purpose |
|---|---|
| [case_results.json](evidence/MP006_R01_RUN001/R01/case_results.json) | Official scoring result |
| [SHA256SUMS.txt](evidence/MP006_R01_RUN001/R01/SHA256SUMS.txt) | Original 79-file scored inventory |
| [recovered_before_start/](evidence/MP006_R01_RUN001/R01/recovered_before_start/) | Raw persistent state preserved before provider restart |
| [association_recorder.jsonl](evidence/MP006_R01_RUN001/R01/association_recorder.jsonl) | Signed provider boundary observations |
| [reachability.jsonl](evidence/MP006_R01_RUN001/R01/reachability.jsonl) | Independent network reachability witness |
| [power_procedure.json](evidence/MP006_R01_RUN001/R01/power_procedure.json) | Operator physical-interruption record |

Additional evidence is preserved separately:

[evidence/MP006_R01_RUN001/supplemental/](evidence/MP006_R01_RUN001/supplemental/)

Supplemental records do not replace files in the original scored inventory.

### Evidence Integrity

The original R01 SHA-256 inventory contains 79 scored files.

From the R01 evidence directory:

```bash
sha256sum -c SHA256SUMS.txt
```

Historical evidence and checksum manifests must remain unchanged.

New documentation is not retroactively included in original scored inventories.

## Distinguishing MP005 From MP006

| Property | MP005 R3 | MP006 R01 |
|---|---|---|
| Provider-process termination | Tested | Occurs as part of host power interruption |
| Same persistent state after restart | Tested | Tested |
| Physical power disconnection | Not tested | Operator-attested |
| Changed host boot ID | Not required | Verified |
| Independent network reachability witness | Not required | Recorded |
| Original authority replay rejection | Tested | Tested |
| Separate fresh authority execution | Tested | Tested |
| Scored providers | A and B | A only |

MP005 established process-restart behavior.

MP006 adds evidence for persistence across the documented physical power-loss and reboot cycle.

The experiments support different claims and retain separate evidence.

## Historical Development Records

[LOCAL_VALIDATION.json](LOCAL_VALIDATION.json) records eight successful offline tests.

Its `NOT_RUN` and `NOT_DEPLOYED` fields reflect the earlier local-build validation stage.

Similarly, [SOURCE_REVIEW.md](SOURCE_REVIEW.md) documents pre-deployment source inspection, not the subsequent live experiment.

These records remain unchanged.

The final R01 disposition is established by the scored evidence rather than retroactive changes to earlier documentation.

## Limitations

The recorded PASS supports the tested Provider A behavior during this specific experiment.

It does not establish:

- Physical power loss measured by an independent electrical instrument.
- Resistance to replacement of the complete persistent history.
- Correctness across every crash or interrupted-write window.
- Concurrent double-spend resistance.
- Equivalent behavior on Provider B.
- Independent hardware actuation.
- Security against an attacker controlling every evidence source.
- Protection against arbitrary modification of local authorization or configuration files.

The network witness independently observed connectivity loss and restoration.

The physical disconnection itself was documented by the operator.

The experiment also recorded different operating-system boot identifiers.

These observations are complementary, not interchangeable.

The scorer explicitly records:

`"timestamp_comparisons_scored": false`

Cross-machine timestamp ordering was not used to determine PASS.

Signed provider events and persistent software records provide execution evidence, not independent hardware execution attestation.

## Reproduction and Preservation

The published files preserve the completed experiment.

They do not constitute standing permission to repeat it.

A separate experiment requires:

- Explicit operator approval.
- Verified implementation and configuration identities.
- New session-specific authorization.
- Fresh, isolated persistent state.
- Separate evidence paths.
- Reviewed network and process configuration.
- Preservation of previous results.

Do not reset historical consumption ledgers or overwrite evidence to manufacture a fresh test condition.

Do not alter frozen MP005 dependencies to make a new test pass.

The original operator procedure is preserved for review:

[OPERATING_PROCEDURE.md](OPERATING_PROCEDURE.md)

Its historical instructions must not be interpreted as authorization for another live run.

## Conclusion

MP006-R01 recorded successful retention of provider-controlled, consumed authority across the documented physical power-loss and reboot cycle.

The original authorization remained spent.

Exact replay produced a signed denial without additional consumption or execution.

Separate fresh authority remained executable.

The result supports the tested persistence and replay-enforcement property without requiring the intermediary to acquire provider execution authority.

**Recorded classification: PASS — within the tested scope.**
