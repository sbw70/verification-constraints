# MP006 — Experimental Results

**Project:** Xer0trust / Neutral Unified Verification Layer (NUVL)

**Experiment:** MP006 — Physical Power-Loss Authority Persistence

**Scored session:** `MP006_R01_RUN001`

**Date:** October 31, 2026

**Target:** Provider A — Dell `Xer0trust-3`

**Recorded result:** PASS

**Safety classification:**

`REPLAY_REJECTED_WITHOUT_ADDITIONAL_CONSUMPTION_OR_EXECUTION`

---

## 1. Objective

MP006 evaluates whether provider-controlled, single-use execution authority remains consumed after physical power loss and host recovery.

The experiment extends MP005, which previously established authority persistence across an idle forced provider-process restart.

MP006 introduces a different interruption condition: complete removal of power from the provider host.

The scored requirements are:

1. Consume valid provider-issued authority exactly once.
2. Preserve the resulting persistent consumption and execution records.
3. Document physical power interruption and subsequent recovery.
4. Capture recovered persistent state before restarting the provider application.
5. Verify that consumed authority survived the interruption.
6. Restart the same provider implementation using the same persistent state.
7. Submit the original authorization again.
8. Confirm replay denial without additional consumption or execution.
9. Submit separate fresh authority.
10. Confirm successful fresh execution without altering the original consumption history.

The NUVL intermediary does not enforce provider authorization.

Provider A retains exclusive control over authorization validation, consumption, replay enforcement, and execution.

## 2. Final Scored Result

The official scorer returned:

**Status:** `PASS`

**Safety result:**

`REPLAY_REJECTED_WITHOUT_ADDITIONAL_CONSUMPTION_OR_EXECUTION`

All recorded checks passed across seven verification groups.

| Verification group | Recorded result |
|---|---|
| Initial authorization consumption | PASS |
| Recovery and process identity | PASS |
| Persistent-state continuity | PASS |
| Original authorization replay | PASS |
| Separate fresh authorization | PASS |
| Power-interruption procedure | PASS |
| Preserved request integrity | PASS |

Primary record:

[case_results.json](evidence/MP006_R01_RUN001/R01/case_results.json)

The scorer also records:

`"timestamp_comparisons_scored": false`

Cross-machine timestamp ordering was not used to determine PASS.

## 3. Experimental Sequence

The experiment followed this sequence:

```text
INITIAL PROVIDER
       |
       v
Fresh persistent state
       |
       v
Original authorization accepted
       |
       v
Consumption recorded — ledger sequence 1
       |
       v
Execution recorded once
       |
       v
Initial evidence preserved
       |
       v
Physical power interruption
       |
       v
Host recovery / changed boot ID
       |
       v
Raw persistent state captured before provider restart
       |
       v
Provider restarted using existing state
       |
       v
Original authorization replayed
       |
       v
DENY — auth_spent
       |
       v
No new consumption or execution
       |
       v
Separate fresh authorization submitted
       |
       v
Fresh execution recorded once
       |
       v
Consumption ledger sequence 2
```

The original and recovered provider processes used the same frozen Provider A implementation.

## 4. Initial Authorization Consumption

### Original Authorization

**Authorization ID:**

`0105b3696211a2f1e536e3b9f07d0c8688e6e05640fd50b1462bb864ece97a0c`

**Operation ID:**

`cf008a19995daf5e51de368f2e44a31dd6a3740150aeb884db727bdcd91a0c5b`

Provider A accepted the authorization and recorded one execution.

The association recorder preserved valid provider-signed `START` and `COMPLETE` boundary events.

### Initial State Transition

| Property | Before consumption | After consumption |
|---|---:|---:|
| Ledger entries | 0 | 1 |
| Ledger sequence | 0 | 1 |
| Spent authorizations | 0 | 1 |
| Execution records | 0 | 1 |
| Original authorization consumed | No | Yes |

The consumption ledger advanced to sequence 1.

**Ledger head:**

`7191f3b14e0641d7c197b547b61f41b36c9792593cf6b6b067c3980d2f596dba`

The spent-state snapshot agreed with the ledger.

The provider execution log contained one execution associated with the original authorization.

**Initial consumption result: PASS**

Evidence:

- [Pre-consumption state](evidence/MP006_R01_RUN001/R01/pre_consume/)
- [Consumed state](evidence/MP006_R01_RUN001/R01/consumed/)
- [Original authorization](evidence/MP006_R01_RUN001/R01/original/)
- [Initial submission](evidence/MP006_R01_RUN001/R01/send_consume/)

## 5. Physical Power Interruption

After initial consumption, the experiment entered its physical power-interruption phase.

The operator confirmed that:

- Initial consumption had completed.
- The provider was idle.
- Initial evidence had been preserved.
- Physical power loss was approved.
- The provider's power was disconnected.

An independent network witness monitored the provider host.

### Reachability Observations

The preserved witness log contains 3,297 observations.

| Observation | Count |
|---|---:|
| Successful responses | 3,211 |
| Timeouts | 51 |
| Destination host unreachable | 35 |
| **Total** | **3,297** |

**First observed network failure:**

`2026-10-31T16:34:15.3227076Z`

**First successful response after interruption:**

`2026-10-31T16:37:07.1485269Z`

The witness established the expected sequence:

`REACHABLE → UNREACHABLE → REACHABLE`

The exact physical disconnection and reconnection times were not independently recorded.

Network loss is consistent with the documented power interruption but does not independently prove electrical power removal.

### Operator Attestation

The operator record identifies physical disconnection and power-loss approval as completed.

It also confirms preservation of initial and recovered evidence on the OmniBook.

**Procedure result: PASS**

Evidence:

- [Power procedure](evidence/MP006_R01_RUN001/R01/power_procedure.json)
- [Reachability witness](evidence/MP006_R01_RUN001/R01/reachability.jsonl)
- [Operator checkpoint](evidence/MP006_R01_RUN001/R01/operator_checkpoint.json)

## 6. Recovery and Process Identity

After power restoration, the experiment preserved Provider A's persistent-state files before explicitly restarting the provider application.

The recovered host had a different operating-system boot identifier.

### Process Comparison

| Property | Initial runtime | Recovered runtime |
|---|---|---|
| Hostname | `Xer0trust-3` | `Xer0trust-3` |
| PID | `113976` | `1725` |
| Boot ID | `881b67af-b296-4908-9bc9-cb398860f244` | `aa810aed-0a27-4577-8580-43576daa4fd4` |
| Provider source | Same frozen implementation | Same frozen implementation |
| Persistent-state path | Same | Same |
| Launch command | Same | Same |
| Working directory | `/home/seth` | `/home/seth` |

**Provider A SHA-256:**

`79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6`

The source hash remained unchanged.

The changed boot identifier established a different OS boot.

The process identity records confirmed the same provider implementation and persistent-state location.

### Recovery Capture

The raw recovery capture occurred at:

`2026-10-31T16:38:03.426647+00:00`

The provider-stopped check was recorded at:

`2026-10-31T16:38:03.468948+00:00`

All three expected persistent-state files were present.

The capture preserved their original bytes before application-level validation or provider restart.

**Recovery result: PASS**

Evidence:

- [Recovered raw state](evidence/MP006_R01_RUN001/R01/recovered_before_start/)
- [Recovery capture check](evidence/MP006_R01_RUN001/R01/recovery_capture_check.json)
- [Provider runtime evidence](evidence/MP006_R01_RUN001/R01/runtime/)

## 7. Persistent-State Continuity

The recovered persistent-state files were compared with the corresponding files preserved after initial consumption.

### Byte-Level Comparison

| File | Consumed state vs. recovered state |
|---|---|
| Consumption ledger | Identical |
| Spent-state snapshot | Identical |
| Execution log | Identical |

### Preserved SHA-256 Identities

**Consumption ledger:**

`a30acbf87e291fbacaac011452732a16d02457d4ff49beb49b5d1147bb0b17f7`

**Spent-state snapshot:**

`4e67aff2218d05d88cac141702aabdbb8c460204472df0803ca3321d1c67a47e`

**Execution log:**

`98f5616477144f0c91de7aebfac53dd2f3280a5573553cfbf01bc84be0310e65`

The recovered ledger still contained the original authorization at sequence 1.

The recovered snapshot identified that authorization as spent.

The recovered execution log retained the original execution record.

No additional consumption or execution appeared in the recovered files.

The frozen MP005 ledger-validation functions subsequently confirmed ledger structure and snapshot consistency.

**Continuity result: PASS**

Supporting validation:

[recovered_validation.json](evidence/MP006_R01_RUN001/supplemental/recovered_validation.json)

This validation receipt is supplemental evidence and is not included in the original scored inventory.

## 8. Exact Authorization Replay

Following recovery, Provider A restarted using the preserved persistent state.

Its runtime log recorded:

`Spent entries loaded: 1`

The original authorization was submitted again.

The preserved replay used the original authorization identity, request representation, verification context, and authorization package.

Provider A returned a signed boundary denial:

`DENY auth_spent`

### Replay State Comparison

| Property | Before replay | After replay |
|---|---:|---:|
| Ledger entries | 1 | 1 |
| Ledger sequence | 1 | 1 |
| Spent authorizations | 1 | 1 |
| Execution records | 1 | 1 |
| Original authorization spent | Yes | Yes |
| Additional execution | — | 0 |

The consumption ledger, spent-state snapshot, and execution log retained their existing SHA-256 identities.

The association recorder preserved one valid Provider A `DENY auth_spent` event.

No additional Provider A `START` or `COMPLETE` event was associated with the replay.

The replay did not create another consumption entry.

The replay did not produce another recorded execution.

**Replay result: PASS**

Evidence:

- [Replay submission](evidence/MP006_R01_RUN001/R01/send_replay/)
- [Before replay](evidence/MP006_R01_RUN001/R01/before_replay/)
- [After replay](evidence/MP006_R01_RUN001/R01/after_replay/)
- [Signed boundary observations](evidence/MP006_R01_RUN001/R01/association_recorder.jsonl)

### Security Significance

Provider A did not treat successful recovery or process restart as permission to reuse consumed authority.

The prior consumption remained enforceable.

The result establishes replay rejection for the tested authorization, persistent history, and recovery condition.

It does not establish protection against arbitrary replacement of the complete persistent history.

## 9. Fresh Authorization Execution

After the original authorization was denied, a separate fresh authorization was prepared.

### Fresh Authorization

**Authorization ID:**

`821ca36878ef72241d6bb02815ad5de8ce2e867f49d1807f6bf0cdd99ff24695`

**Operation ID:**

`980a0f7e80d9d918347d65757666ab7b918306c3e4f4f9ab4a8deeda2db6535f`

The fresh authorization was distinct from the original.

Before submission, its authorization ID was absent from the consumption ledger and spent-state snapshot.

### Fresh Execution Result

Provider A accepted the fresh authorization.

The provider recorded:

- One new consumption entry.
- One additional software execution.
- Signed `START` and `COMPLETE` boundary observations.
- A new ledger head linked to the original consumption entry.

### State Advancement

| Property | Before fresh execution | After fresh execution |
|---|---:|---:|
| Ledger entries | 1 | 2 |
| Ledger sequence | 1 | 2 |
| Spent authorizations | 1 | 2 |
| Execution records | 1 | 2 |
| Original consumption preserved | Yes | Yes |

**Final ledger head:**

`b744c9c7182d82769e11a4e29394f463a2a0f93e3d80f5f5a2d4d5873a074a6d`

The second ledger entry identifies the original ledger head as its previous-entry hash.

The ledger remains valid and the spent-state snapshot agrees with the final history.

**Fresh execution result: PASS**

Evidence:

- [Fresh authorization](evidence/MP006_R01_RUN001/R01/fresh/)
- [Fresh submission](evidence/MP006_R01_RUN001/R01/send_fresh/)
- [Before fresh execution](evidence/MP006_R01_RUN001/R01/before_fresh/)
- [After fresh execution](evidence/MP006_R01_RUN001/R01/after_fresh/)

### Execution Sequence Interpretation

The provider runtime logs record process-local execution sequence `1` for both the initial and recovered processes.

This is not a duplicate persistent consumption.

The process-local execution counter restarts with the provider process.

The durable consumption ledger does not restart.

Its sequence advances from 1 to 2.

Process-local counter continuity across operating-system boots was not a scored requirement.

## 10. Signed Boundary Evidence

The original scored association recorder contains nine records:

- One `SESSION_START`.
- Eight signed provider submissions.

All eight submissions have recorded valid signatures.

### Recorded Boundary Sequence

| Recorder sequence | Provider | Boundary | Result |
|---|---|---|---|
| 1 | Recorder | SESSION_START | Session initialized |
| 2 | Provider B | DENY | `auth_missing` |
| 3 | Provider A | START | Original authorization |
| 4 | Provider A | COMPLETE | Original authorization |
| 5 | Provider B | DENY | `auth_missing` |
| 6 | Provider A | DENY | `auth_spent` |
| 7 | Provider B | DENY | `auth_missing` |
| 8 | Provider A | START | Fresh authorization |
| 9 | Provider A | COMPLETE | Fresh authorization |

Provider A's signed boundary events were correlated with the preserved authorization identities and provider-local state.

Provider B received forwarded requests without a corresponding Provider B authorization.

Its `auth_missing` denials were expected observations.

Provider B was not the scored power-loss execution target.

### Final Recorder Record

A supplemental final recorder log contains a tenth record:

`SESSION_END`

The original nine scored records remain an identical prefix.

The supplemental final log does not replace the original recorder evidence.

Evidence:

- [Original scored association log](evidence/MP006_R01_RUN001/R01/association_recorder.jsonl)
- [Supplemental final association log](evidence/MP006_R01_RUN001/supplemental/association_recorder_final.jsonl)

## 11. Request and Transport Integrity

The scorer verified that the original, replay, and fresh submissions matched their preserved request and authorization artifacts.

| Submission | Preserved-byte verification |
|---|---|
| Original consumption | PASS |
| Original replay | PASS |
| Fresh authorization | PASS |

All three relay submissions returned HTTP:

`204 No Content`

This response establishes transport-level acknowledgment by the relay.

It does not establish provider authorization, execution, or completion.

Those outcomes were evaluated using signed provider boundary events and persistent-state evidence.

## 12. Relationship to MP005

MP005 and MP006 share the same hardened Provider A authorization and persistence implementation.

They test different interruption conditions.

| Property | MP005 R3 | MP006 R01 |
|---|---|---|
| Idle forced process termination | Tested | Not the primary interruption |
| Same persistent state after process restart | Tested | Tested |
| Physical power interruption | Not tested | Operator-attested |
| Changed OS boot identifier | Not required | Verified |
| Raw state captured before application restart | Not the same recovery procedure | Tested |
| Original authority remains spent | PASS | PASS |
| Exact replay denied | PASS | PASS |
| Fresh authorization executes | PASS | PASS |
| Provider A | PASS | PASS |
| Provider B | PASS | Not scored |

MP005 established the tested process-restart property for both providers.

MP006 extends the evidence to Provider A recovery following the documented physical power interruption.

Neither experiment establishes every possible persistence or rollback condition.

## 13. Evidence Integrity

The original scored experiment is preserved at:

[evidence/MP006_R01_RUN001/R01/](evidence/MP006_R01_RUN001/R01/)

Its SHA-256 inventory covers 79 original scored files.

[SHA256SUMS.txt](evidence/MP006_R01_RUN001/R01/SHA256SUMS.txt)

The inventory includes:

- Provider authorization artifacts.
- Request and submission records.
- Consumption ledgers.
- Spent-state snapshots.
- Execution logs.
- Process identities.
- Signed boundary evidence.
- Raw recovered files.
- Operator and reachability records.
- Scoring results.

From the original R01 evidence directory:

```bash
sha256sum -c SHA256SUMS.txt
```

The supplemental evidence files are not included in that original inventory.

README documentation added after evidence collection must not cause historical manifests to be regenerated.

See [PROVENANCE.md](PROVENANCE.md) for source identity, configuration binding, and evidence preservation details.

## 14. Limitations

The recorded PASS establishes the observed properties of this experiment.

It does not establish:

### Independent Electrical Measurement

The physical power disconnection was documented by the operator.

The independent witness observed network loss and restoration.

A changed boot identifier established an OS reboot.

No independent electrical instrument directly measured removal of power.

### Complete-History Rollback Resistance

The experiment preserved and reused the existing consumption ledger.

It did not test replacement of both the ledger and spent-state snapshot with an older mutually consistent history.

An intact hash chain does not independently establish history freshness.

### Every Crash Window

The experiment did not systematically interrupt execution at every possible persistence or filesystem write boundary.

It does not establish correctness for all interrupted-write conditions.

### Concurrent Double Spending

The experiment tested sequential replay after recovery.

It did not test concurrent presentation of the same authority during the MP006 session.

### Provider B Power-Loss Recovery

Provider B remained outside the scored physical-interruption target.

Its signed `auth_missing` denials do not establish Provider B recovery behavior.

### Physical Execution Attestation

Execution was established through provider software records, persistent state, and signed boundary observations.

No independent physical actuator or hardware execution witness was scored.

### Fully Independent Evidence Custody

The experiment used off-machine preservation, SHA-256 inventories, signed observations, and operator records.

These provide complementary verification.

They do not protect against arbitrary coordinated replacement of every evidence source.

## 15. Supported Conclusion

The MP006-R01 scored evidence supports the following conclusion:

**In the tested Provider A implementation, previously consumed single-use authority remained consumed across the documented physical power-loss and host-recovery cycle.**

The recovered provider:

1. Loaded the original consumed authorization from persistent state.
2. Denied exact replay with `auth_spent`.
3. Produced no additional consumption or execution from that replay.
4. Accepted and executed separate fresh authority.
5. Preserved the original consumption history while advancing the ledger.

These observations were recorded using the same frozen Provider A implementation before and after the interruption.

The intermediary did not acquire or exercise provider authorization authority.

The result demonstrates the tested persistence and replay-enforcement property without extending the claim beyond the observed conditions.

**Final classification: PASS — within the tested scope.**
