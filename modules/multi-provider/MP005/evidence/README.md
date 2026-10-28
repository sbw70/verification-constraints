```markdown
# MP005 — Experimental Evidence

## Purpose

This directory preserves the experimental evidence generated during MP005 multi-provider authority-consumption and restart-durability testing.

MP005 examines whether authorization consumed by an independently controlled provider remains spent after an idle forced-process restart.

The experiment also evaluates whether:

- Exact replay of consumed authority is denied.
- Replay produces no additional execution.
- Provider-local consumption history remains intact.
- Fresh, independently authorized requests remain executable.
- Signed boundary observations can be correlated with provider-local records.

Provider A and Provider B retain exclusive control over their respective authorization and execution boundaries.

The intermediary forwards requests without acquiring provider execution authority.

The association recorder independently observes signed boundary events but does not authorize execution.

## Evidence Organization

| Directory | Contents |
|---|---|
| [preflight/](preflight/) | Host-local preflight records and physical rehearsal evidence |
| [scored/](scored/) | Preserved scored campaigns, including unsuccessful and successful results |
| [simulated_smoke/](simulated_smoke/) | Linux simulation campaigns R1, R2, and R3 |
| [reviews/](reviews/) | Technical inspections, validation records, independent reviews, and experimental reconciliation |

The original evidence is retained under its recorded session identifiers.

Historical campaign records are not renamed, overwritten, or retrospectively reclassified.

## Experimental Progression

MP005 developed through separate simulation, preflight, rehearsal, and scored campaigns.

| Campaign | Classification | Outcome |
|---|---|---|
| Simulated R1 | Baseline characterization | Completed; rollback weakness observed |
| Simulated R2 | Hardened implementation characterization | Tested cases passed; reconciliation semantics blocker identified |
| Simulated R3 | Revised hardened implementation | 12/12 cases passed within tested scope |
| Physical preflight | Host and environment verification | Recorded |
| Physical rehearsal | R01 and R02 | Both passed; operator acceptance recorded |
| Scored R2 | First preserved scored attempt | R01 NON-PASS; R02 NOT_RUN |
| Scored R3 | Replacement scored campaign | R01 PASS; R02 PASS |

These classifications describe different experimental stages.

A PASS in one stage must not be interpreted as proof of every property evaluated by subsequent stages.

## 1. Simulation Evidence

Directory:

[simulated_smoke/](simulated_smoke/)

Simulation campaigns were executed separately from the final physical-host scored tests.

They provide supporting evidence about provider behavior, state reconciliation, and rejection conditions.

Simulation results are not interchangeable with scored live results.

### R1 — Baseline Characterization

Session:

`MP005_SIMULATED_SMOKE_R1`

Evidence:

[MP005_SIMULATED_SMOKE_R1/](simulated_smoke/MP005_SIMULATED_SMOKE_R1/)

The baseline simulation examined restart behavior and state manipulation before the subsequent hardening changes.

The S03 cases demonstrated that rollback of the earlier implementation's materialized spent state could restore previously consumed authority.

**Rollback re-enabled authority in the observed R1 S03 cases.**

The recorded S03 status of PASS means that the characterization completed successfully.

It does not mean that rollback resistance passed.

This distinction is essential to interpreting the baseline.

Supporting records:

- [R1 case results](simulated_smoke/MP005_SIMULATED_SMOKE_R1/case_results.json)
- [R1 SHA-256 inventory](simulated_smoke/MP005_SIMULATED_SMOKE_R1/SHA256SUMS.txt)
- [R1 review summary](reviews/simulation/R1_SUMMARY.json)

### R2 — Hardened Implementation

Session:

`MP005_SIMULATED_SMOKE_R2`

Evidence:

[MP005_SIMULATED_SMOKE_R2/](simulated_smoke/MP005_SIMULATED_SMOKE_R2/)

R2 introduced provider-local durable consumption history using a hash-linked ledger.

The observed cases demonstrated that consumption history could preserve spent-authority status independently of the materialized snapshot.

The recorded R2 simulation cases passed their tested conditions.

However, independent review identified a reconciliation semantics blocker.

The R2 implementation was therefore not accepted as the final hardened implementation.

The original R2 observations and review findings remain preserved.

Supporting records:

- [R2 case results](simulated_smoke/MP005_SIMULATED_SMOKE_R2/case_results.json)
- [R2 SHA-256 inventory](simulated_smoke/MP005_SIMULATED_SMOKE_R2/SHA256SUMS.txt)
- [R2 review summary](reviews/simulation/R2_SUMMARY.json)

### R3 — Revised Hardened Implementation

Session:

`MP005_SIMULATED_SMOKE_R3`

Evidence:

[MP005_SIMULATED_SMOKE_R3/](simulated_smoke/MP005_SIMULATED_SMOKE_R3/)

R3 refined startup snapshot reconciliation while retaining the provider-local consumption-ledger architecture.

The simulation evaluated six cases for each provider.

| Case | Scope |
|---|---|
| S00 | Restart durability and single-use behavior |
| S01–S02 | Invalid or unavailable ledger startup conditions |
| S03 | Recovery from a provably valid earlier ledger prefix |
| S04 | Rejection of a snapshot ahead of the ledger |
| S05 | Rejection of equal-sequence ledger-head or spent-state divergence |

Recorded results:

| Provider | Cases | Result |
|---|---|---|
| Provider A | S00–S05 | 6 PASS |
| Provider B | S00–S05 | 6 PASS |
| Total | 12 | 12 PASS |

The independent R3 review was based on recomputation of captured evidence rather than acceptance of existing PASS labels alone.

The reviewer did not execute new provider or server tests as part of that review.

Supporting records:

- [R3 case results](simulated_smoke/MP005_SIMULATED_SMOKE_R3/case_results.json)
- [R3 SHA-256 inventory](simulated_smoke/MP005_SIMULATED_SMOKE_R3/SHA256SUMS.txt)
- [R3 review summary](reviews/simulation/R3_SUMMARY.json)
- [R3 reconciliation analysis](reviews/MP005_R3_RECONCILIATION.md)
- [R3 independent review](../notes/MP005_R3_INDEPENDENT_REVIEW.json)

The R3 simulation does not establish protection against rollback of the entire consumption ledger and snapshot to an older mutually consistent history.

## 2. Physical Preflight

Session:

`MP005_PREFLIGHT_20261022_R1`

Evidence:

[MP005_PREFLIGHT_20261022_R1/](preflight/MP005_PREFLIGHT_20261022_R1/)

This stage preserved host-local readiness and configuration observations for the physical test environment.

The evidence includes records for:

- Provider A.
- Provider B.
- NUVL intermediary.
- Association recorder.

The preflight inventory identifies the examined roles and their recorded results.

Reference:

[PREFLIGHT_EVIDENCE_INVENTORY.json](preflight/MP005_PREFLIGHT_20261022_R1/PREFLIGHT_EVIDENCE_INVENTORY.json)

This preflight session did not itself authorize execution of the later scored campaign.

## 3. Physical Rehearsal

Session:

`MP005_REHEARSAL_20261024_R1`

Evidence:

[MP005_REHEARSAL_20261024_R1/](preflight/MP005_REHEARSAL_20261024_R1/)

The physical rehearsal exercised the restart-durability procedure before scored execution.

Both provider cases produced recorded PASS results.

| Case | Provider | Rehearsal Result |
|---|---|---|
| R01 | Provider A | PASS |
| R02 | Provider B | PASS |

Evidence includes:

- Prepared authorization artifacts.
- Initial provider state.
- Consumption records.
- Signed boundary observations.
- Pre-restart process identity.
- Operator checkpoint.
- Post-restart process identity.
- Exact replay observations.
- Fresh-authorization observations.
- Final case results.
- SHA-256 inventories.

The rehearsal was subsequently accepted as satisfying the prerequisite for a separate scored campaign.

Acceptance did not itself constitute scored authorization.

Supporting records:

- [Rehearsal R01 results](preflight/MP005_REHEARSAL_20261024_R1/R01/case_results.json)
- [Rehearsal R02 results](preflight/MP005_REHEARSAL_20261024_R1/R02/case_results.json)
- [Rehearsal review](reviews/MP005_REHEARSAL_20261024_R1.review.json)
- [Operator acceptance](reviews/MP005_REHEARSAL_20261024_R1.acceptance.json)

## 4. Scored R2 — Preserved Unsuccessful Campaign

Session:

`MP005_SCORED_20261025_R2`

Evidence:

[MP005_SCORED_20261025_R2/](scored/MP005_SCORED_20261025_R2/)

This campaign remains preserved as an unsuccessful scored attempt.

### Provider A — R01

The original authorization was consumed and the corresponding execution was recorded.

After process restart, exact replay was denied.

However, the fresh-authorization portion did not satisfy the required completion criteria.

The fresh authorization was durably consumed, but the expected execution record and signed COMPLETE boundary event were absent.

The recorded evidence identifies:

- Valid consumption-ledger history.
- Successful restart-durability observations.
- Successful exact-replay denial.
- Fresh authorization consumption.
- No corresponding fresh execution record.
- No signed fresh COMPLETE observation.

**Final R01 classification: NON-PASS.**

The incident record identifies disconnected SSH output pipes as a suspected contributing condition.

The exact causal exception was not captured, so that explanation remains a hypothesis rather than a confirmed root cause.

The consumed authorization was not retried.

### Provider B — R02

**Final R02 classification: NOT_RUN.**

No Provider B scored outcome is inferred from an unexecuted case.

### Preserved Failure Evidence

[R01_FRESH_EXECUTION_INCIDENT.json](scored/MP005_SCORED_20261025_R2/R01/R01_FRESH_EXECUTION_INCIDENT.json)

The unsuccessful campaign remains available for independent examination.

It must not be silently replaced by the later R3 result.

## 5. Scored R3 — Successful Campaign

Session:

`MP005_SCORED_20261026_R3`

Evidence:

[MP005_SCORED_20261026_R3/](scored/MP005_SCORED_20261026_R3/)

The replacement campaign used separately isolated provider state and a detached provider-launch procedure.

The previously recorded R2 state and evidence were preserved.

The same principal restart-durability requirements remained applicable.

### Final Results

| Case | Provider | Result |
|---|---|---|
| R01 | Provider A | PASS |
| R02 | Provider B | PASS |

Both cases satisfied the recorded scored requirements.

### Initial Authorization

Each provider accepted its own valid authorization.

The evidence records:

- One new consumption-ledger entry.
- One execution.
- Valid ledger hash linkage.
- Consistent spent-state snapshot.
- Signed START and COMPLETE boundary observations.

### Process Restart

Each provider underwent an operator-controlled idle forced-process termination.

The subsequent restart evidence established:

- A different process instance.
- The same physical host.
- The same operating-system boot.
- The same provider runtime identity.
- The same persistent state paths.
- Preserved consumption history.
- Preserved execution history.

The experiment did not involve a host reboot.

### Exact Replay

The original consumed authorization was submitted again.

For both providers, the recorded result was:

`DENY — auth_spent`

The evidence established:

- No additional consumption-ledger entry.
- No additional execution.
- No additional START event.
- No additional COMPLETE event.
- Unchanged relevant provider-local state.
- Continued recognition of the original authorization as spent.

### Fresh Authorization

Each provider subsequently received a different valid authorization.

The evidence established:

- A new authorization identity.
- One additional linked consumption entry.
- One additional execution.
- Updated spent-state consistency.
- Signed START and COMPLETE boundary observations.

The fresh-authorization requirement passed for both providers.

### Primary Scored Evidence

Provider A:

- [R01 evidence directory](scored/MP005_SCORED_20261026_R3/R01/)
- [R01 case results](scored/MP005_SCORED_20261026_R3/R01/case_results.json)
- [R01 SHA-256 inventory](scored/MP005_SCORED_20261026_R3/R01/SHA256SUMS.txt)

Provider B:

- [R02 evidence directory](scored/MP005_SCORED_20261026_R3/R02/)
- [R02 case results](scored/MP005_SCORED_20261026_R3/R02/case_results.json)
- [R02 SHA-256 inventory](scored/MP005_SCORED_20261026_R3/R02/SHA256SUMS.txt)

Additional R3 evidence:

- [Association observations](scored/MP005_SCORED_20261026_R3/association/)
- [Runtime logs](scored/MP005_SCORED_20261026_R3/runtime/)

Each R3 scored case includes a 67-entry SHA-256 evidence inventory.

## 6. Understanding Case Evidence

The R01 and R02 case directories contain evidence from multiple stages of the same experiment.

### Authorization Identity

`original/` preserves the original request and authorization material.

`fresh/` preserves the separately generated fresh authorization.

The associated identity records allow comparison of request, authorization, binding, nonce, and operation identifiers.

### Consumption Evidence

`pre_consume/` records the relevant state before initial consumption.

`consumed/` records the corresponding state after consumption.

The captured consumption-ledger entries are independently checked for sequence, identity, and hash linkage.

### Restart Evidence

`pre_restart_process.json` records the original process identity.

`post_restart_process.json` records the restarted process identity.

`operator_checkpoint.json` records the evidence checkpoint preceding operator-controlled termination.

The additional restart-state captures preserve the relevant provider-local history.

### Replay Evidence

`before_replay/` and `after_replay/` preserve state around exact replay.

`replay/` contains the corresponding request and boundary observations.

The scorer checks that previously consumed authority remains spent without additional execution.

### Fresh Execution Evidence

`before_fresh/` and `after_fresh/` preserve state surrounding the fresh request.

`fresh_send/` contains the corresponding send and boundary observations.

The scorer verifies that fresh authority extends the consumption history and produces the required execution evidence.

### Final Results

`case_results.json` records the scored assertions and final case classification.

`SHA256SUMS.txt` preserves the corresponding case-file integrity inventory.

The PASS classification is supported by the underlying observations; it is not a substitute for reviewing those observations.

## 7. Association Evidence

The association recorder independently captures provider-originated boundary submissions.

The recorded events include:

- START.
- COMPLETE.
- DENY.

Records contain the submitted event, signature-verification information, receipt metadata, and original submitted bytes.

The recorder maintains a hash-linked JSON Lines evidence history.

The signed events are correlated using provider identity, authorization identity, operation identity, nonce, and request binding.

The recorder's SESSION_START record also preserves configuration and source identities associated with the session.

Association records support independent verification of provider-originated statements.

They are not independent proof of physical execution.

HTTP 204 responses are not treated as evidence that execution occurred.

See [association/README.md](../association/README.md).

## 8. Evidence Integrity and Provenance

MP005 uses SHA-256 inventories to preserve and validate captured evidence.

Individual case inventories are relative to their containing case directories.

Simulation inventories are relative to their corresponding simulation session directories.

Historical configuration locks use their own preserved configuration contexts.

The final R3 configuration must not be substituted when verifying earlier campaigns.

Relevant provenance references:

- [Campaign configuration map](../provenance/CAMPAIGN_CONFIGURATION_MAP.json)
- [Integrity context definitions](../provenance/INTEGRITY_CONTEXTS.json)
- [Validated code inventory](../provenance/R3_VALIDATED_CODE_SHA256SUMS.txt)
- [Source manifest](../configs/MP005_SOURCE_MANIFEST.json)
- [Implementation manifest](../configs/MP005_IMPLEMENTATION_MANIFEST.json)

The publication audit verified retained evidence inventories and their referenced files.

That audit did not rerun the underlying physical experiments.

### Preservation Rules

Historical evidence must remain byte-for-byte unchanged.

A reviewer should:

1. Identify the exact campaign and case.
2. Locate the corresponding original evidence.
3. Resolve the applicable historical configuration.
4. Verify the relevant SHA-256 inventory.
5. Examine the original state and boundary records.
6. Independently evaluate the required assertions.
7. Preserve the original experimental classification.

A later successful campaign does not retroactively convert an earlier unsuccessful result into PASS.

## 9. Technical Reviews

Directory:

[reviews/](reviews/)

This directory contains design inspections, reconciliation analyses, build checks, and validation records.

Notable records include:

- [Hardening design](reviews/MP005_HARDENING_DESIGN.md)
- [Implementation inspection](reviews/MP005_IMPLEMENTATION_INSPECTION.md)
- [R3 reconciliation analysis](reviews/MP005_R3_RECONCILIATION.md)
- [Rehearsal acceptance](reviews/MP005_REHEARSAL_20261024_R1.acceptance.json)
- [R3 validation review](reviews/VALIDATION_R3_REVIEW.json)

Some historical review documents were created before the physical scored campaigns occurred.

Their original NOT_RUN, pending, or readiness classifications reflect the state of the project when those reviews were recorded.

They must not be mistaken for current results or silently rewritten to match later outcomes.

The completed scored results are established by the subsequent physical-campaign evidence.

## 10. Scope and Limitations

The final scored evidence supports preservation of provider-consumed authority across the specific idle forced-process restarts performed in MP005.

It does not establish:

- Resistance to rollback of the entire consumption ledger and materialized snapshot to an older mutually consistent history.
- Enforcement of externally preserved ledger-head freshness.
- Physical power-loss durability.
- Host reboot durability.
- Crash-window correctness.
- Concurrent double-spend resistance.
- Independent operating-system execution attestation.
- Physical actuator behavior.
- Guaranteed delivery of boundary observations.

The experiment uses provider-local execution records as the observed software execution consequence.

It does not prove physical actuation or externally attest every execution event.

The hash-linked ledger provides an internally verifiable consumption history, but an attacker able to replace the entire history with an older mutually consistent version remains outside the established protection.

These limitations remain applicable despite the successful final scored campaign.

## Conclusion

MP005 preserves the progression from an observed baseline rollback weakness through hardened provider-local consumption enforcement and the final successful scored campaign.

The evidence establishes that, under the tested idle forced-process restart conditions:

- Provider A retained previously consumed authority as spent.
- Provider B retained previously consumed authority as spent.
- Exact replay was denied without additional execution.
- Fresh authorization remained executable.
- Consumption and execution observations were supported by provider-local records and signed boundary evidence.

The intermediary did not become an execution authority.

The association recorder did not become an authorization authority.

The final result is limited to the tested conditions and the preserved implementation.

## Related Documentation

- [MP005 root](../)
- [Results](../RESULTS.md)
- [Provenance](../PROVENANCE.md)
- [Provider A](../provider_a/)
- [Provider B](../provider_b/)
- [Test harness](../harness/)
- [Configuration](../configs/)
- [Association recorder](../association/)
- [NUVL intermediary](../intermediary/)
```
