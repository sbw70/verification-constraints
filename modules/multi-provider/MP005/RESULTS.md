# MP005 — Experimental Results

**Experiment:** Multi-Provider Durable Authority

**Final scored session:** `MP005_SCORED_20261026_R3`

**Provider A (R01): PASS**

**Provider B (R02): PASS**

## 1. Objective

MP005 evaluates whether provider-controlled, single-use execution authority remains consumed after an idle forced-process restart.

The tested implementation uses a durable, hash-linked consumption ledger maintained locally by each provider.

The experiment evaluates whether:

1. Valid authorization is consumed before execution.
2. Consumption survives termination and restart of the provider process.
3. Exact replay of consumed authorization is denied.
4. Replay produces no additional consumption or execution.
5. A separate fresh authorization remains executable.

Provider A and Provider B independently enforce their respective authorization boundaries.

The NUVL intermediary does not originate or control execution authority. The association recorder provides signed boundary evidence without authorizing execution.

## 2. Final Scored Results

**Session:** `MP005_SCORED_20261026_R3`

| Test | Provider A — R01 | Provider B — R02 |
|---|---|---|
| Valid authorization consumed | PASS | PASS |
| Linked consumption entry verified | PASS | PASS |
| Initial execution recorded once | PASS | PASS |
| Signed START and COMPLETE verified | PASS | PASS |
| New process instance verified | PASS | PASS |
| Same host and boot verified | PASS | PASS |
| Durable state preserved | PASS | PASS |
| Exact replay denied `auth_spent` | PASS | PASS |
| No additional replay consumption | PASS | PASS |
| No additional replay execution | PASS | PASS |
| Fresh authorization consumed | PASS | PASS |
| Fresh execution recorded once | PASS | PASS |
| **Final classification** | **PASS** | **PASS** |

Both scored cases satisfied the recorded requirements.

Primary result files:

- [R01 Provider A results](evidence/scored/MP005_SCORED_20261026_R3/R01/case_results.json)
- [R02 Provider B results](evidence/scored/MP005_SCORED_20261026_R3/R02/case_results.json)

These are software-execution and process-restart observations. No physical actuator behavior was scored.

## 3. Initial Authorization Consumption

Each provider received a valid provider-specific authorization through the NUVL intermediary.

Before admitting execution, the provider verified the authorization and recorded its consumption in a provider-local ledger.

The scored evidence established:

- One new consumption entry.
- Correct authorization and operation identity.
- Sequential ledger advancement.
- Valid previous-entry hash linkage.
- Correct recomputed entry hash.
- Agreement between ledger and spent-state snapshot.
- One recorded execution.
- Signed START and COMPLETE observations associated with the consumed authorization.

The consumption ledger is authoritative for reconstructing spent authority.

The materialized snapshot represents the ledger-derived state.

The intermediary does not maintain either record.

## 4. Forced Process Restart

The experiment used an operator-controlled idle forced-process termination.

The harness required evidence of completed initial consumption and execution before the termination checkpoint.

The recorded restart checks established:

- A different process instance after restart.
- A later process start time.
- The same host.
- The same operating-system boot.
- The same runtime path and verified source hash.
- The same command line and working directory.
- The same persistent state path.
- Preserved consumption and execution history.
- Continued agreement between the spent-state snapshot and consumption ledger.

A new process identifier alone was not sufficient.

The experiment established a process restart, not an operating-system reboot or power-loss recovery.

## 5. Exact Replay

Following restart, the original consumed authorization was submitted again.

Both providers returned the recorded authorization-denial reason:

`auth_spent`

The scored evidence established:

- The original authorization remained marked as consumed.
- No additional execution was recorded.
- No new START or COMPLETE event was associated with the replay.
- The relevant execution records remained unchanged.
- The spent-state snapshot remained unchanged.
- The existing consumption history remained preserved.

The original authorization did not become executable merely because the provider process restarted.

The recorded result supports single-use enforcement across the specific process-restart condition tested.

## 6. Fresh Authorization

After replay denial, each provider received a separate fresh authorization.

The scored evidence established:

- A different authorization identifier.
- Successful authorization consumption.
- Exactly one additional linked consumption entry.
- One additional recorded execution.
- An updated snapshot consistent with the ledger.
- Signed START and COMPLETE boundary observations.

This distinction is important.

MP005 did not merely establish that old authorization could be rejected after restart.

It also established that the restarted provider could continue admitting new, valid authority under the tested conditions.

## 7. Signed Association Evidence

The association recorder captured provider-originated boundary events separately from the providers' local state.

The final R3 recorder log is:

[evidence/scored/MP005_SCORED_20261026_R3/association/recorder.jsonl](evidence/scored/MP005_SCORED_20261026_R3/association/recorder.jsonl)

The published log contains 17 records:

- One SESSION_START record.
- Sixteen boundary submissions.

The submissions include signed START, COMPLETE, and DENY observations for the two provider domains.

The SESSION_START record identifies the recorder, provider registry, contract, and run-manifest hashes.

These records support correlation of the observed provider events with the recorded configuration.

A signed boundary observation is not independent hardware execution attestation.

HTTP `204 No Content` is not accepted as proof that execution completed.

## 8. R3 Scored Evidence Inventories

Each final scored case preserves its original SHA-256 inventory.

| Case | Inventory Entries | Result |
|---|---:|---|
| R01 — Provider A | 67 | PASS |
| R02 — Provider B | 67 | PASS |
| **Total** | **134** | **Both PASS** |

Inventories:

- [R01 SHA256SUMS.txt](evidence/scored/MP005_SCORED_20261026_R3/R01/SHA256SUMS.txt)
- [R02 SHA256SUMS.txt](evidence/scored/MP005_SCORED_20261026_R3/R02/SHA256SUMS.txt)

Each inventory covers the corresponding preserved case files.

The publication audit verified the retained evidence against these inventories.

Publication verification did not rerun the underlying physical experiment.

## 9. Earlier Physical Rehearsal

**Session:** `MP005_REHEARSAL_20261024_R1`

| Case | Result |
|---|---|
| R01 — Provider A | PASS |
| R02 — Provider B | PASS |

The physical rehearsal exercised the restart, replay, and fresh-authorization procedure before scored execution.

Both cases recorded PASS.

The operator subsequently accepted the rehearsal as a prerequisite for a separately authorized scored campaign.

Acceptance was not itself scored authorization.

Evidence:

- [Rehearsal R01 results](evidence/preflight/MP005_REHEARSAL_20261024_R1/R01/case_results.json)
- [Rehearsal R02 results](evidence/preflight/MP005_REHEARSAL_20261024_R1/R02/case_results.json)
- [Rehearsal review](evidence/reviews/MP005_REHEARSAL_20261024_R1.review.json)
- [Operator acceptance](evidence/reviews/MP005_REHEARSAL_20261024_R1.acceptance.json)

The acceptance record identifies an outstanding external Ed25519 audit at the time of acceptance. That record is preserved without retroactive modification.

## 10. Earlier Scored R2 — NON-PASS

**Session:** `MP005_SCORED_20261025_R2`

| Case | Classification |
|---|---|
| R01 — Provider A | NON-PASS |
| R02 — Provider B | NOT_RUN |

Provider A successfully demonstrated initial consumption, process-restart durability, and exact-replay denial.

However, the fresh-authorization requirement was not satisfied.

The observed sequence was:

1. Fresh authorization was issued and submitted.
2. The authorization was durably consumed.
3. The consumption ledger advanced from one to two entries.
4. A signed START observation was recorded.
5. No corresponding fresh execution was recorded.
6. No signed COMPLETE observation was recorded.

The execution count remained unchanged at one.

A disconnected SSH output pipe and a possible logging-related exception were identified as a suspected contributing condition.

The exact causal exception was not captured.

**The root cause was not confirmed.**

The consumed authorization was not retried.

R01 remained NON-PASS, and R02 was not performed.

The later R3 campaign used separate state and a detached provider-launch procedure. It did not overwrite or reclassify the earlier failure.

Evidence:

[R2 fresh-execution incident](evidence/scored/MP005_SCORED_20261025_R2/R01/R01_FRESH_EXECUTION_INCIDENT.json)

[Complete R2 scored evidence](evidence/scored/MP005_SCORED_20261025_R2/)

## 11. Simulation Results

Simulation evidence is preserved separately from the physical scored campaigns.

### R1 — Baseline Characterization

The baseline simulation identified a rollback weakness.

For both providers, S03 demonstrated that rolling back the earlier implementation's materialized spent state could make previously consumed authority executable again.

The S03 PASS classification means the characterization was completed successfully.

It does not mean rollback protection passed.

Evidence:

- [R1 results](evidence/simulated_smoke/MP005_SIMULATED_SMOKE_R1/case_results.json)
- [R1 review summary](evidence/reviews/simulation/R1_SUMMARY.json)

### R2 — Hardened Simulation

The R2 simulation evaluated provider-local hash-linked consumption history.

All eight recorded cases passed their tested conditions.

However, independent review identified a snapshot-reconciliation semantics blocker.

The R2 implementation was not accepted as the final hardened candidate.

Evidence:

- [R2 results](evidence/simulated_smoke/MP005_SIMULATED_SMOKE_R2/case_results.json)
- [R2 review summary](evidence/reviews/simulation/R2_SUMMARY.json)
- [R2 independent review](notes/MP005_R2_INDEPENDENT_REVIEW.json)

### R3 — Revised Hardened Simulation

The R3 simulation evaluated six cases for each provider.

| Case | Tested Behavior |
|---|---|
| S00 | Restart durability and consumed-authority replay |
| S01–S02 | Ledger-related startup failure conditions |
| S03 | Valid earlier-prefix snapshot reconciliation |
| S04 | Snapshot-ahead rejection |
| S05 | Equal-sequence ledger-head and spent-state divergence rejection |

| Provider | Cases Passed |
|---|---:|
| Provider A | 6/6 |
| Provider B | 6/6 |
| **Total** | **12/12** |

The R3 independent review recomputed captured evidence without running new provider or server tests.

Its conclusion was:

`PASS_FOR_TESTED_R3_RECONCILIATION_SCOPE`

Evidence:

- [R3 results](evidence/simulated_smoke/MP005_SIMULATED_SMOKE_R3/case_results.json)
- [R3 review summary](evidence/reviews/simulation/R3_SUMMARY.json)
- [R3 independent review](notes/MP005_R3_INDEPENDENT_REVIEW.json)
- [R3 reconciliation analysis](evidence/reviews/MP005_R3_RECONCILIATION.md)

The simulation results support specific reconciliation and startup behaviors. They do not extend the scored physical test to every simulated condition.

## 12. Configuration and Evidence Interpretation

The recorded campaigns used different configurations and state histories.

Their corresponding configuration identities are preserved in:

[CAMPAIGN_CONFIGURATION_MAP.json](provenance/CAMPAIGN_CONFIGURATION_MAP.json)

The original run manifest retains some planning-time `NOT_RUN` fields.

These values are historical configuration records, not the final outcome of the later executed campaigns.

Final experiment dispositions must be determined from the corresponding case results and campaign evidence.

Historical configurations must be used when verifying historical sessions.

A later successful result does not retroactively change an earlier failed or unexecuted case.

## 13. Established Results

Within the recorded experimental conditions, MP005 establishes:

1. Provider A durably consumed authorization before recorded execution.
2. Provider B independently did the same.
3. Both providers preserved consumed-authority status across idle forced-process restarts.
4. Both denied exact replay without additional execution.
5. Both admitted and executed separate fresh authorization.
6. Signed boundary observations and provider-local state supported the scored results.
7. The intermediary did not need to hold or originate provider authority.
8. The association recorder did not need to control provider execution.

These are observations about the tested implementation and environment.

They are not claims of universal correctness under all possible failure conditions.

## 14. Limitations and Unestablished Properties

MP005 does not establish:

- Resistance to rollback of the entire consumption ledger and snapshot to an older mutually consistent history.
- Automatic enforcement of external ledger-head freshness.
- Durability across physical power loss.
- Durability across operating-system reboot.
- Crash-window correctness during an interrupted consumption operation.
- Concurrent double-spend resistance.
- Independent operating-system execution attestation.
- Physical actuator behavior.
- Guaranteed boundary-event delivery.
- Generalized security against complete host compromise.

A valid signed boundary event demonstrates verification against the registered provider key. It does not independently attest physical execution.

The provider-local execution log records the software execution consequence used by the experiment.

The test did not score continuity of process-local execution sequence counters.

These exclusions remain applicable despite the final R3 PASS results.

## 15. Conclusion

**MP005 R3 completed successfully for both independent provider domains.**

Under the tested idle forced-process restart conditions, previously consumed authorization remained spent.

Exact replay did not produce additional execution.

Separate fresh authorization remained usable.

The observed enforcement was maintained within provider-controlled boundaries, using durable provider-local consumption history.

The intermediary forwarded requests without becoming an authorization authority.

The association recorder preserved signed observations without becoming an execution authority.

**Final scored disposition: R01 PASS / R02 PASS.**

---

## Related Documentation

- [MP005 overview](README.md)
- [Evidence guide](evidence/README.md)
- [Provenance](PROVENANCE.md)
- [Test contract](configs/MP005_CONTRACT.md)
- [Harness](harness/README.md)
- [Provider A](provider_a/README.md)
- [Provider B](provider_b/README.md)
