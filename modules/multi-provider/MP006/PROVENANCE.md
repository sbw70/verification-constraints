# MP006 — Provenance and Evidence Integrity

**Project:** Xer0trust / Neutral Unified Verification Layer (NUVL)

**Experiment:** MP006 — Physical Power-Loss Authority Persistence

**Scored session:** `MP006_R01_RUN001`

**Experiment date:** October 31, 2026

**Recorded disposition:** PASS

## 1. Purpose

This document establishes the source, configuration, execution, and evidence provenance for MP006.

MP006 evaluates whether provider-controlled, single-use execution authority remains consumed after physical power interruption and host recovery.

The experiment reuses the frozen MP005 Provider A implementation and its durable authorization-consumption mechanism.

The provenance record distinguishes:

- Original implementation and dependency identities.
- MP006-specific orchestration code.
- Reviewed configuration and operator authorization.
- Provider runtime and process identities.
- Persistent state before and after power interruption.
- Signed provider boundary observations.
- Independently collected network reachability observations.
- Original scored evidence and supplemental records.

Provenance establishes the relationship between these artifacts.

It does not independently establish the correctness of the implementation or the outcome of the experiment.

Those questions are addressed by the preserved evidence and scoring results.

## 2. Repository Location

**Repository:** `sbw70/verification-constraints`

**Experiment directory:**

`modules/multi-provider/MP006/`

Primary records:

- [README.md](README.md)
- [OPERATING_PROCEDURE.md](OPERATING_PROCEDURE.md)
- [SOURCE_REVIEW.md](SOURCE_REVIEW.md)
- [LOCAL_VALIDATION.json](LOCAL_VALIDATION.json)
- [Scored evidence](evidence/MP006_R01_RUN001/R01/)
- [Supplemental evidence](evidence/MP006_R01_RUN001/supplemental/)

The original experiment records remain in their session-specific directories.

Historical artifacts are not rewritten to reflect later documentation changes.

## 3. Source Lineage

### Original Multi-Provider Development

MP006 builds on the earlier multi-provider experiments.

The immediate implementation dependency is MP005, which established durable authorization-consumption enforcement across provider-process restart.

The historical MP005 manifests identify an earlier baseline source commit:

`fa541618b1a3bc58700a81b29129b17b35b1e0fc`

This identifies earlier source provenance.

It does not identify the final hardened MP005 implementation.

### Frozen MP005 Reference

MP006 records the following reference commit:

`73713f6e9ed9c95251cc69ec88ef816cab771ac0`

The original MP006 build inventory identifies 48 unchanged files copied from the MP005 reference.

These files include:

- Provider A and Provider B implementations.
- Authorization-issuance utilities.
- Laboratory cryptographic fixtures.
- NUVL intermediary.
- Association recorder.
- Provider trust registry.
- Verification harness.
- Configuration and implementation manifests.
- Historical simulation and review code.

The copied reference is located at:

[reference/MP005/](reference/MP005/)

The MP005 reference is a dependency, not a newly implemented MP006 security mechanism.

## 4. Frozen Implementation Identity

The principal frozen implementation hashes are:

| Component | SHA-256 |
|---|---|
| Provider A | `79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6` |
| Provider B | `618ec76ef5dd3bfa3ba7b1ad3941ed0516a7511b72957d7efb82ec565905b605` |
| NUVL relay | `09d458cc8e3e13706b5463deffea0e14fcd784011a629623a09b9bd5ee04d6f4` |
| Association recorder | `fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc` |

The original source identities are preserved in:

- [MP005 Source Manifest](reference/MP005/configs/MP005_SOURCE_MANIFEST.json)
- [MP005 Implementation Manifest](reference/MP005/configs/MP005_IMPLEMENTATION_MANIFEST.json)
- [Original MP006 Build Inventory](manifests/original/SHA256SUMS.txt)

MP006-R01 scored Provider A.

Provider B remained an independently controlled provider but was not the power-loss test target.

## 5. MP006 Implementation Identity

The MP006-specific orchestration implementation is:

[mp006.py](mp006.py)

**Original recorded SHA-256:**

`c11c0af05f30f5d02ef2f96d05d263f712c18659003cfaf0ca821f7398ea4ad6`

The adapter provides experiment-specific functions for:

- Configuration and operator-authorization checks.
- Controlled provider launch.
- Provider process identity.
- Persistent-state evidence capture.
- Raw recovery preservation.
- Boot identity comparison.
- Replay and fresh-authorization verification.
- Evidence classification and scoring.

The adapter imports frozen MP005 functions from:

`reference/MP005/harness/common.py`

`reference/MP005/harness/ledger_evidence.py`

It also loads the frozen Provider A runtime.

The source review records that MP006 does not replace the underlying provider authorization, signature, consumption-ledger, or execution algorithms.

### Offline Validation

[LOCAL_VALIDATION.json](LOCAL_VALIDATION.json) records eight successful offline tests.

The original validation record predates the live experiment.

Its `NOT_RUN` and `NOT_DEPLOYED` fields represent historical build status, not the final scored outcome.

The original source review is preserved at:

[SOURCE_REVIEW.md](SOURCE_REVIEW.md)

The source-review findings must be distinguished from subsequent live observations.

## 6. Configuration Identity

The reviewed configuration is:

[configs/MP006_R01.json](configs/MP006_R01.json)

**Configuration SHA-256:**

`d7b4be8a0b42fed64f7ca2a17fc412280a84d7ea20d2421c0c786873756a63ea`

It identifies:

| Field | Recorded value |
|---|---|
| Session | `MP006_R01_RUN001` |
| Baseline | `MP005_SCORED_20261026_R3` |
| Provider | Provider A |
| Provider host | `192.168.1.118` |
| Provider port | `9090` |
| Relay | `192.168.1.100:8080` |
| Association recorder | `192.168.1.102:9191` |
| Status | `REVIEWED_FOR_OPERATOR_RUN` |

These addresses identify the recorded laboratory configuration.

They are not permanent deployment defaults.

### Operator Authorization

The session-specific operator authorization is:

[authorizations/MP006_R01_RUN001.json](authorizations/MP006_R01_RUN001.json)

It records:

- `authorized: true`
- Session `MP006_R01_RUN001`
- The reviewed configuration SHA-256.
- Seven explicitly permitted orchestration actions.

The recorded authorization configuration hash matches the reviewed configuration.

This file authorizes the local experimental procedure.

It is not a provider-issued execution authorization.

The authorization file itself is not cryptographically signed.

Control of the local authorization and configuration files remains a trust assumption of the test.

## 7. Physical Laboratory Environment

The scored experiment used the following recorded roles.

| Component | Role |
|---|---|
| Dell `Xer0trust-3` | Provider A and persistent-state test target |
| Raspberry Pi `nuvl-relay` | NUVL intermediary |
| HP OmniBook | Controller, association recorder, and independent reachability witness |
| Provider B | Independent provider receiving forwarded requests; not scored for power loss |

### Provider A Runtime

**Operating system:**

`Linux-6.14.0-37-generic-x86_64-with-glibc2.39`

**Python:**

`3.12.3`

**Provider implementation:**

`/home/seth/MULTI_PROVIDER_006/reference/MP005/provider_a/provider_a.py`

**Persistent state:**

`/home/seth/MULTI_PROVIDER_006/state/MP006_R01_RUN001/provider_a/`

The recorded filesystem mount identifies an ext4 filesystem on `/dev/sda2`.

The experiment did not independently characterize the storage device's physical write guarantees.

## 8. Provider Process Provenance

Two different operating-system boot identities were recorded.

### Initial Runtime

**Hostname:** `Xer0trust-3`

**PID:** `113976`

**Boot ID:**

`881b67af-b296-4908-9bc9-cb398860f244`

### Recovered Runtime

**Hostname:** `Xer0trust-3`

**PID:** `1725`

**Boot ID:**

`aa810aed-0a27-4577-8580-43576daa4fd4`

The captured process identities establish:

- Same hostname.
- Different operating-system boot identifiers.
- Different provider process instances.
- Same provider implementation path.
- Same verified provider source hash.
- Same persistent-state path.
- Same provider launch command.
- Same working directory.

The original and recovered process identities are preserved in:

- [Initial Process](evidence/MP006_R01_RUN001/R01/pre_consume/process.json)
- [Consumed-State Process](evidence/MP006_R01_RUN001/R01/consumed/process.json)
- [Recovered Process](evidence/MP006_R01_RUN001/R01/before_replay/process.json)
- [Final Process](evidence/MP006_R01_RUN001/R01/after_fresh/process.json)

The matching runtime hash establishes implementation continuity between the recorded processes.

The changed boot identifier establishes that the host was running under a different OS boot.

Neither observation independently measures removal of electrical power.

## 9. Physical-Interruption Evidence

Three evidence sources document the interruption and recovery.

### Operator Record

[power_procedure.json](evidence/MP006_R01_RUN001/R01/power_procedure.json)

Records affirmative operator attestations for:

- Physical disconnection.
- Power-loss approval.
- Provider idle confirmation.
- Preservation of initial evidence on the OmniBook.
- Preservation of recovered raw evidence on the OmniBook.

Exact physical disconnection and reconnection times were not recorded.

The file instead references the first observed network timeout and subsequent recovery.

### Independent Reachability Witness

[reachability.jsonl](evidence/MP006_R01_RUN001/R01/reachability.jsonl)

The witness recorded 3,297 observations.

The preserved log includes:

- 3,211 successful responses.
- 51 timeout observations.
- 35 destination-host-unreachable observations.

**First recorded failure:**

`2026-10-31T16:34:15.3227076Z`

**First successful response after the interruption:**

`2026-10-31T16:37:07.1485269Z`

These timestamps identify network observations.

They are not independently measured physical power-disconnection or reconnection times.

### Recovery Capture Check

[recovery_capture_check.json](evidence/MP006_R01_RUN001/R01/recovery_capture_check.json)

Records:

**Timestamp:**

`2026-10-31T16:38:03.468948+00:00`

**Recovered boot ID:**

`aa810aed-0a27-4577-8580-43576daa4fd4`

**Provider stopped:**

`true`

The process check was performed after raw persistent-state capture.

It establishes the observed stopped condition at inspection, not continuous absence of all earlier provider activity.

## 10. Pre-Restart Persistent-State Preservation

The principal recovery evidence is located at:

[recovered_before_start/](evidence/MP006_R01_RUN001/R01/recovered_before_start/)

The raw capture occurred at:

`2026-10-31T16:38:03.426647+00:00`

The capture preserved the original bytes of three persistent files before the recovered provider was explicitly started.

### Recovered File Identities

| File | Bytes | SHA-256 |
|---|---:|---|
| Consumption ledger | 388 | `a30acbf87e291fbacaac011452732a16d02457d4ff49beb49b5d1147bb0b17f7` |
| Spent-state snapshot | 231 | `4e67aff2218d05d88cac141702aabdbb8c460204472df0803ca3321d1c67a47e` |
| Execution log | 338 | `98f5616477144f0c91de7aebfac53dd2f3280a5573553cfbf01bc84be0310e65` |

All three files were present.

The recovered bytes matched the corresponding files preserved immediately after the original authorization consumption.

The capture procedure did not reconstruct, initialize, or repair provider state.

It preserved the observed files before application-level state validation.

The resulting copies were subsequently checked against the preserved pre-interruption evidence.

### Recovered Ledger Identity

The recovered ledger contained one consumption entry.

**Ledger sequence:** `1`

**Ledger head:**

`7191f3b14e0641d7c197b547b61f41b36c9792593cf6b6b067c3980d2f596dba`

The recovered snapshot identified the original authorization as spent.

Its sequence and head matched the consumption ledger.

## 11. Authorization Artifact Provenance

The experiment preserved separate original and fresh provider-issued authorization artifacts.

### Original Authorization

[Original Authorization Evidence](evidence/MP006_R01_RUN001/R01/original/)

**Authorization ID:**

`0105b3696211a2f1e536e3b9f07d0c8688e6e05640fd50b1462bb864ece97a0c`

**Operation ID:**

`cf008a19995daf5e51de368f2e44a31dd6a3740150aeb884db727bdcd91a0c5b`

**Authorization package SHA-256:**

`f459a15ae2d8e0940cc664d6d9d247400abf5de9d57af778d2c0e7f2408ac09a`

The original authorization was used for initial consumption and subsequent replay.

The preserved replay submission maintained the same authorization identity, request representation, verification context, and package identity.

### Fresh Authorization

[Fresh Authorization Evidence](evidence/MP006_R01_RUN001/R01/fresh/)

**Authorization ID:**

`821ca36878ef72241d6bb02815ad5de8ce2e867f49d1807f6bf0cdd99ff24695`

**Operation ID:**

`980a0f7e80d9d918347d65757666ab7b918306c3e4f4f9ab4a8deeda2db6535f`

**Authorization package SHA-256:**

`bfd6350e5663b3eec39a4c2ae6a01b28a381b75c1084b7b20cacd9f44d94bb3f`

The fresh authorization is distinct from the original.

The scorer verifies that it was previously unspent and that its execution advanced the existing consumption history.

## 12. Boundary Evidence Provenance

Provider boundary observations were collected through the association recorder.

The original scored recorder log is:

[association_recorder.jsonl](evidence/MP006_R01_RUN001/R01/association_recorder.jsonl)

It contains nine records:

- One `SESSION_START`.
- Eight signed provider boundary submissions.

The records include:

- Original Provider A `START`.
- Original Provider A `COMPLETE`.
- Provider A replay `DENY auth_spent`.
- Fresh Provider A `START`.
- Fresh Provider A `COMPLETE`.
- Provider B `DENY auth_missing` observations.

Provider B's denials are recorded but do not establish Provider B power-loss durability.

The recorder validates provider signatures using the registered Ed25519 public keys.

Signed boundary events are correlated with authorization identities and provider-local state.

A relay HTTP response is not accepted as evidence of execution.

### Supplemental Final Recorder Log

The final recorder log is preserved at:

[association_recorder_final.jsonl](evidence/MP006_R01_RUN001/supplemental/association_recorder_final.jsonl)

It contains ten records.

The original nine scored records are retained as an identical prefix.

The tenth record is `SESSION_END`.

The supplemental log does not replace the original scored recorder file.

## 13. Original Scored Evidence Inventory

The original scored evidence is located at:

[evidence/MP006_R01_RUN001/R01/](evidence/MP006_R01_RUN001/R01/)

Its root SHA-256 inventory contains 79 entries.

[Original SHA256SUMS.txt](evidence/MP006_R01_RUN001/R01/SHA256SUMS.txt)

The inventory covers:

- Original and fresh authorization artifacts.
- Preserved requests and submission records.
- Provider process identities.
- Persistent-state snapshots.
- Consumption ledgers.
- Execution records.
- Signed boundary observations.
- Raw recovery evidence.
- Runtime logs.
- Physical-interruption procedure.
- Network reachability witness.
- Scored case results.

Subdirectory-local manifests provide additional file-level integrity records.

### Verification

From the original R01 evidence directory:

```bash
sha256sum -c SHA256SUMS.txt
```

Verification establishes agreement with the stored inventory.

It does not independently establish that the inventory itself is immutable or externally trusted.

No original scored artifact should be modified to accommodate subsequent documentation.

## 14. Supplemental Evidence

The supplemental directory contains:

[recovered_validation.json](evidence/MP006_R01_RUN001/supplemental/recovered_validation.json)

[association_recorder_final.jsonl](evidence/MP006_R01_RUN001/supplemental/association_recorder_final.jsonl)

The recovered-validation record reports:

`PASS`

It confirms the recorded ledger structure, original authorization presence, and agreement between the recovered consumption ledger and spent-state snapshot.

The final recorder log adds an orderly session termination record.

These files were preserved separately.

They are not included in the original 79-file scored inventory.

Supplemental evidence must not be silently substituted for original scored inputs.

## 15. Build Inventory Preservation

Historical build inventories are located at:

[manifests/original/](manifests/original/)

The initial source inventory contains 56 entries.

The subsequent deployment inventory contains 57 entries.

The later inventory reflects:

- A revised reviewed configuration.
- Inclusion of the original root-level inventory file.
- Retention of the other recorded common file identities.

These are historical build records.

They are not equivalent to the 79-file scored evidence inventory.

Because the original build manifests were archived under a different directory and documentation was subsequently added, their relative paths must be interpreted against the historical build layout.

Do not rewrite the original inventories to match the current documentation tree.

## 16. Scored Result Identity

The official result is:

[case_results.json](evidence/MP006_R01_RUN001/R01/case_results.json)

It records:

**Status:**

`PASS`

**Safety result:**

`REPLAY_REJECTED_WITHOUT_ADDITIONAL_CONSUMPTION_OR_EXECUTION`

The scorer evaluated seven groups:

| Group | Result |
|---|---|
| Initial consumption | PASS |
| Recovery | PASS |
| State continuity | PASS |
| Replay | PASS |
| Fresh execution | PASS |
| Procedure | PASS |
| Preserved sends | PASS |

The scored result also records:

`"timestamp_comparisons_scored": false`

Cross-machine timestamp comparisons were not used as scoring conditions.

The final scored result belongs to the preserved R01 evidence.

Historical development records retaining `NOT_RUN` status are not rewritten.

## 17. Evidence Custody and Limitations

The experiment used distinct evidence sources:

**Provider-local evidence**

Consumption ledger, spent-state snapshot, execution log, runtime output, and process identity.

**Association evidence**

Signed provider boundary records received by the independently running association recorder.

**Network witness**

Reachability observations collected from the OmniBook.

**Operator evidence**

Physical-interruption approval, disconnection attestation, idle confirmation, and off-machine preservation attestations.

These sources provide complementary observations.

They do not constitute a fully independent forensic chain of custody.

In particular:

- Physical power loss was operator-attested.
- No independent electrical sensor measured power removal.
- The raw capture was not a forensic disk image.
- Process inspection cannot exclude every possible earlier transient process.
- Local SHA-256 inventories are not externally immutable anchors.
- Signed software events do not independently attest physical execution.
- The experiment does not establish resistance to replacement of the complete persistent history.
- The experiment does not cover all possible crash and interrupted-write windows.

The recorded evidence supports the defined experimental result under its stated assumptions.

## 18. Preservation Requirements

The following restrictions apply to the published experiment:

1. Preserve original scored evidence bytes.
2. Preserve historical SHA-256 inventories.
3. Keep supplemental evidence separate from scored evidence.
4. Do not rewrite historical configuration or validation status fields.
5. Do not modify frozen MP005 dependencies.
6. Do not replace failed verification with reconstructed evidence.
7. Do not reuse original provider authorization as fresh authority.
8. Do not reset historical consumption state to create another test.
9. Do not present operator attestation as independent electrical measurement.
10. Do not extend the observed PASS beyond the tested implementation and conditions.

Any new experiment requires its own reviewed configuration, authorization, isolated state, evidence, and scoring record.

## 19. Conclusion

The preserved MP006-R01 records identify the implementation, configuration, authorization artifacts, provider processes, persistent state, and evidence used during the experiment.

The recorded source and process identities establish continuity of the frozen Provider A implementation across two operating-system boot instances.

The recovered persistent-state files match the preserved pre-interruption state.

The scored evidence records denial of the original consumed authorization without additional consumption or execution, followed by successful execution under separate fresh authority.

These observations support the recorded PASS classification within the defined experimental scope.

They do not establish broader physical, cryptographic, or adversarial guarantees beyond the tested conditions.
