# MP005 — Provenance and Evidence Integrity

**Project:** Xer0trust / Neutral Unified Verification Layer (NUVL)

**Experiment:** MP005 — Multi-Provider Durable Authority

**Final scored session:** `MP005_SCORED_20261026_R3`

**Recorded disposition:** R01 PASS / R02 PASS

## 1. Purpose

This document identifies the source, configuration, execution, and evidence records supporting MP005.

Its purpose is to make the published experiment independently inspectable without altering the original observations.

MP005 evaluates whether independently controlled providers preserve consumed, single-use execution authority across an idle forced-process restart.

The experiment includes:

- Provider-specific authorization issuance.
- Independent provider authorization validation.
- Durable, hash-linked consumption ledgers.
- Materialized spent-authority snapshots.
- Provider-local execution records.
- Signed provider boundary observations.
- Independent association recording.
- Process identity and restart evidence.
- Historical configuration and implementation records.

The NUVL intermediary does not originate or control provider execution authority.

The association recorder observes signed events but does not authorize execution.

The test harness collects and verifies evidence without replacing provider enforcement.

Provenance records establish the identity and relationship of the published artifacts. They are not substitutes for the experimental observations themselves.

## 2. Repository Location

Repository:

https://github.com/sbw70/verification-constraints

Experiment directory:

`modules/multi-provider/MP005/`

The reviewed MP005 publication contains 1,404 files.

The publication preserves implementation code, laboratory configuration, historical snapshots, test evidence, and technical reviews.

Primary documentation:

- [README.md](README.md)
- [RESULTS.md](RESULTS.md)
- [Evidence README](evidence/README.md)
- [Configuration README](configs/README.md)

The original records remain in their campaign-specific locations.

Historical results are not overwritten to conform to later outcomes.

## 3. Provenance Records

The [provenance/](provenance/) directory contains four primary records.

| File | Function |
|---|---|
| [CAMPAIGN_CONFIGURATION_MAP.json](provenance/CAMPAIGN_CONFIGURATION_MAP.json) | Maps physical campaigns to their original configurations, authorizations, and recorder evidence |
| [INTEGRITY_CONTEXTS.json](provenance/INTEGRITY_CONTEXTS.json) | Defines how relative paths and historical inventories must be resolved |
| [R3_VALIDATED_CODE_SHA256SUMS.txt](provenance/R3_VALIDATED_CODE_SHA256SUMS.txt) | Preserves SHA-256 identities of the validated R3 implementation and test code |
| [HARDENING_TECHNICAL_RECORD.json](provenance/HARDENING_TECHNICAL_RECORD.json) | Preserves selected historical hardening observations and implementation identities |

These records serve different purposes.

The campaign map establishes which configuration belongs to which experiment.

The integrity-context file establishes where historical file references resolve.

The validated-code inventory identifies the reviewed source bytes.

The hardening technical record preserves earlier implementation observations without presenting them as new experiments.

## 4. Source Lineage

MP005 originated from the earlier multi-provider implementation.

The baseline source commit recorded in the manifests is:

`fa541618b1a3bc58700a81b29129b17b35b1e0fc`

This commit identifies the source baseline used for comparison.

It does not mean that the final MP005 provider implementations are byte-identical to that baseline.

Provider A and Provider B underwent subsequent hardening.

The intermediary, association recorder, and associated components retain their independently recorded source identities.

Primary sources:

- [MP005_SOURCE_MANIFEST.json](configs/MP005_SOURCE_MANIFEST.json)
- [MP005_IMPLEMENTATION_MANIFEST.json](configs/MP005_IMPLEMENTATION_MANIFEST.json)
- [Baseline snapshots](baseline/)

### Provider Implementation History

| Provider | Baseline | R2 Hardened | R3 Candidate |
|---|---|---|---|
| Provider A | `c875582b...` | `a8ab30e1...` | `79e4994c...` |
| Provider B | `5e0ab4b7...` | `c7d3ab6d...` | `618ec76e...` |

The abbreviated hashes above are identifiers for readability.

The full SHA-256 values are preserved in the manifests.

The source manifests distinguish the historical baseline from the validated R3 candidate.

A reviewer must not assume that a successful result from one implementation version establishes the behavior of another version.

## 5. Final R3 Source Identities

The final R3 provider runtime SHA-256 values are:

### Provider A

File:

`provider_a/provider_a.py`

SHA-256:

`79e4994c955ca842af04a8fd650a33d49de040bab95b821ded9e63e16866f2b6`

### Provider B

File:

`provider_b/provider_b.py`

SHA-256:

`618ec76ef5dd3bfa3ba7b1ad3941ed0516a7511b72957d7efb82ec565905b605`

### NUVL Intermediary

File:

`intermediary/nuvl_multi_relay.py`

SHA-256:

`09d458cc8e3e13706b5463deffea0e14fcd784011a629623a09b9bd5ee04d6f4`

### Association Recorder

File:

`association/association_recorder.py`

SHA-256:

`fad60dfc8df53337d2e41288c2c4973442258cae4240945ebbd0aa8920550bfc`

### Provider Registry

File:

`association/provider_registry.json`

SHA-256:

`59d739588427d87313e3434982d943a9c82bad26c3fe3deb7d5488efadb6088d`

Additional source, signing-key, trust-key, and harness identities are preserved in:

[R3_VALIDATED_CODE_SHA256SUMS.txt](provenance/R3_VALIDATED_CODE_SHA256SUMS.txt)

That inventory contains 30 file identities.

Paths in this inventory resolve relative to the MP005 root.

## 6. Implementation Changes

The R2 hardened implementation introduced durable provider-local consumption history.

The R3 revision refined snapshot reconciliation against the validated ledger.

The R3 review supplement identifies the following provider changes:

- Modified `load_spent_state`.
- Added `classify_snapshot`.
- Added `preserve_malformed_snapshot`.
- Added `reject_json_constant`.

The changes are documented separately for Provider A and Provider B.

Exact implementation comparisons:

- [Provider A R2-to-R3 patch](notes/provider_a_R3_REVIEW_FROM_R2.patch)
- [Provider B R2-to-R3 patch](notes/provider_b_R3_REVIEW_FROM_R2.patch)
- [R3 review supplement](notes/MP005_R3_REVIEW_SUPPLEMENT.json)
- [R3 reconciliation analysis](evidence/reviews/MP005_R3_RECONCILIATION.md)

The provider-specific authorization, consumption, signing, and execution boundaries remain part of the frozen tested implementations.

The review supplement describes the source changes and their tested scope.

It does not establish additional physical experiments.

## 7. Configuration Integrity

The final R3 configuration is preserved in [configs/](configs/).

The canonical configuration inventory is:

[MP005_LOCK_SHA256SUMS.txt](configs/MP005_LOCK_SHA256SUMS.txt)

It covers five files:

1. `configs/MP005_CONTRACT.md`
2. `configs/MP005_SOURCE_MANIFEST.json`
3. `configs/MP005_HARNESS_MANIFEST.json`
4. `configs/MP005_IMPLEMENTATION_MANIFEST.json`
5. `configs/MP005_RUN_MANIFEST.json`

Paths in this inventory resolve relative to the MP005 root.

### Final R3 Configuration Identities

Contract SHA-256:

`9e68503d4788287a34cc7e8ef3f1313f0b49eaaa7c10098dda9407761c9a3324`

Run manifest SHA-256:

`25a0334640651210eb2d22d3df0cb695e0499508d784d7c1463332b7267e8b93`

Canonical lock SHA-256 recorded in the R3 operator authorization:

`beb89d3c68e5d83ada267df95b686ecb7cf49e4dd51dfddd18039a00d223804d`

The canonical lock identity and the individual configuration-file hashes serve different purposes.

The lock identifies the authorized configuration collection.

The individual hashes identify the exact files within that collection.

These values must not be interchanged.

## 8. Historical Configuration Preservation

MP005 retains earlier configuration revisions rather than replacing them with the final R3 files.

Historical configurations are stored under:

[configs/history/](configs/history/)

The campaign mapping identifies three physical campaigns.

| Campaign | Configuration Directory | Lock SHA-256 Prefix |
|---|---|---|
| Rehearsal R1 | `configs/history/MP005_REHEARSAL_LOCK_20261025` | `08039d75...` |
| Scored R2 | `configs/history/MP005_SCORED_20261025_R2` | `1f309e8a...` |
| Scored R3 | `configs` | `beb89d3c...` |

Full identities and associated source paths are preserved in:

[CAMPAIGN_CONFIGURATION_MAP.json](provenance/CAMPAIGN_CONFIGURATION_MAP.json)

The final R3 configuration must not be substituted when evaluating the rehearsal or R2 scored campaign.

Doing so would create an incorrect correspondence between the evidence and the configuration used when it was captured.

## 9. Operator Authorization Records

Historical operator authorization records remain in the MP005 root.

These include:

- [Preflight authorization](MP005_PREFLIGHT_20261022_R1.rehearsal.json)
- [Rehearsal authorization](MP005_REHEARSAL_20261024_R1.rehearsal.json)
- [Earlier scored R1 authorization](MP005_SCORED_20261025_R1.scored.json)
- [Scored R2 authorization](MP005_SCORED_20261025_R2.scored.json)
- [Scored R3 authorization](MP005_SCORED_20261026_R3.scored.json)

These files preserve historical operator approval and configuration-lock references.

They are distinct from provider-issued authorization artifacts.

The operator records do not independently grant authority for Provider A or Provider B to execute a request.

Provider-specific authorization remains subject to the provider's own signature validation, policy, and consumption constraints.

The earlier scored R1 authorization was superseded.

The R2 and R3 scored campaigns used separate authorizations and configuration locks.

The authorization records also contain original operator-workspace references. Those references document the historical environment; they are not portable repository paths.

## 10. Configuration-to-Recorder Correlation

The association recorder writes a SESSION_START record identifying the configuration used during the session.

The record includes:

- Session identifier.
- Recorder source SHA-256.
- Provider registry SHA-256.
- Run manifest SHA-256.
- Contract SHA-256.
- Registered provider identities.

For the final R3 campaign, the original recorder log is:

[evidence/scored/MP005_SCORED_20261026_R3/association/recorder.jsonl](evidence/scored/MP005_SCORED_20261026_R3/association/recorder.jsonl)

The SESSION_START record contains the final R3 contract and run-manifest identities listed above.

This allows a reviewer to associate the captured signed boundary observations with the relevant frozen configuration.

The recorder log uses a hash-linked JSON Lines structure.

Each record contains a sequence number, previous-record hash, and current-record hash.

The log preserves the submitted bytes, observation metadata, and signature-verification results.

A hash-linked evidence log supports detection of inconsistent modification when an independent trusted reference is retained.

It does not, by itself, prevent complete replacement of the history by an actor controlling all copies.

## 11. Evidence Inventory Contexts

The correct interpretation of a SHA-256 inventory depends on its original directory and campaign.

The authoritative resolution rules are preserved in:

[INTEGRITY_CONTEXTS.json](provenance/INTEGRITY_CONTEXTS.json)

### Scored and Rehearsal Evidence

`SHA256SUMS.txt` paths resolve relative to the directory containing the inventory.

For example, entries in:

`evidence/scored/MP005_SCORED_20261026_R3/R01/SHA256SUMS.txt`

resolve against:

`evidence/scored/MP005_SCORED_20261026_R3/R01/`

They do not resolve against the MP005 root.

### Current Configuration Lock

Entries in:

`configs/MP005_LOCK_SHA256SUMS.txt`

resolve relative to the MP005 root.

### Historical Configuration Locks

Historical configuration inventories resolve within their retained configuration overlays.

Where a historical lock references a `configs/` file, the corresponding file in the historical configuration directory is used when present.

Other dependencies resolve according to the preserved integrity-context rules.

### Baseline Source Records

Baseline source references resolve against their original baseline snapshot.

The final R3 implementation must not be used as a substitute for the MP003 baseline when checking historical identities.

### Simulation Evidence

The retained simulation contexts are:

| Campaign | Source Context |
|---|---|
| R1 | `baseline/pre_hardening` |
| R2 | `baseline/pre_R3` |
| R3 | MP005 root |

These contexts matter when interpreting the different hardened implementations.

## 12. Simulation Preservation

MP005 preserves three simulation generations.

### R1 — Baseline

Evidence:

[evidence/simulated_smoke/MP005_SIMULATED_SMOKE_R1/](evidence/simulated_smoke/MP005_SIMULATED_SMOKE_R1/)

The R1 baseline demonstrated a rollback weakness in the earlier implementation.

In the recorded S03 cases, rollback of the materialized spent state re-enabled previously consumed authority.

This was a successful characterization of a weakness, not a successful rollback-defense result.

Preservation references:

- [R1 preservation record](notes/R1_PRESERVATION.json)
- [R1-to-R3 preservation record](notes/MP005_R1_R3_PRESERVATION.json)
- [R1 review summary](evidence/reviews/simulation/R1_SUMMARY.json)

### R2 — Hardened Candidate

Evidence:

[evidence/simulated_smoke/MP005_SIMULATED_SMOKE_R2/](evidence/simulated_smoke/MP005_SIMULATED_SMOKE_R2/)

The R2 simulation used the hardened provider-local consumption-ledger implementation.

Its tested cases passed, but independent review identified a snapshot-reconciliation semantics blocker.

The earlier R2 implementation was not accepted as the final R3 candidate.

Preservation references:

- [R2-to-R3 preservation record](notes/MP005_R2_R3_PRESERVATION.json)
- [R2 independent review](notes/MP005_R2_INDEPENDENT_REVIEW.json)
- [R2 review summary](evidence/reviews/simulation/R2_SUMMARY.json)

### R3 — Revised Candidate

Evidence:

[evidence/simulated_smoke/MP005_SIMULATED_SMOKE_R3/](evidence/simulated_smoke/MP005_SIMULATED_SMOKE_R3/)

The R3 simulation recorded 12 PASS results:

- Provider A: S00–S05 PASS.
- Provider B: S00–S05 PASS.

The independent review recomputed captured evidence and reported:

`PASS_FOR_TESTED_R3_RECONCILIATION_SCOPE`

The review did not execute new provider or server experiments.

References:

- [R3 independent review](notes/MP005_R3_INDEPENDENT_REVIEW.json)
- [R3 review summary](evidence/reviews/simulation/R3_SUMMARY.json)
- [R3 SHA-256 inventory](evidence/simulated_smoke/MP005_SIMULATED_SMOKE_R3/SHA256SUMS.txt)

The R3 simulation and its review remain distinct from the later physical scored experiment.

## 13. Physical Test Provenance

### Preflight

Session:

`MP005_PREFLIGHT_20261022_R1`

Evidence:

[evidence/preflight/MP005_PREFLIGHT_20261022_R1/](evidence/preflight/MP005_PREFLIGHT_20261022_R1/)

This stage preserved host-local configuration and readiness observations.

It was not the final scored experiment.

### Rehearsal

Session:

`MP005_REHEARSAL_20261024_R1`

Recorded results:

- R01 Provider A: PASS.
- R02 Provider B: PASS.

The operator accepted the rehearsal as a prerequisite for a separately authorized scored campaign.

Evidence:

- [Rehearsal results and records](evidence/preflight/MP005_REHEARSAL_20261024_R1/)
- [Rehearsal review](evidence/reviews/MP005_REHEARSAL_20261024_R1.review.json)
- [Operator acceptance](evidence/reviews/MP005_REHEARSAL_20261024_R1.acceptance.json)

### Scored R2

Session:

`MP005_SCORED_20261025_R2`

Recorded disposition:

- R01 Provider A: NON-PASS.
- R02 Provider B: NOT_RUN.

The original authorization was preserved as consumed, and exact replay was denied.

However, a separate fresh authorization was consumed without the required execution record and signed completion.

The cause was not conclusively established.

The consumed authorization was not retried.

Evidence:

[R2 scored records](evidence/scored/MP005_SCORED_20261025_R2/)

[R2 execution incident](evidence/scored/MP005_SCORED_20261025_R2/R01/R01_FRESH_EXECUTION_INCIDENT.json)

### Scored R3

Session:

`MP005_SCORED_20261026_R3`

Recorded disposition:

- R01 Provider A: PASS.
- R02 Provider B: PASS.

Both providers preserved consumed authority across the tested idle forced-process restarts.

Exact replay was denied without additional execution.

Distinct fresh authorization was subsequently consumed and executed once.

Evidence:

- [R01 results](evidence/scored/MP005_SCORED_20261026_R3/R01/case_results.json)
- [R02 results](evidence/scored/MP005_SCORED_20261026_R3/R02/case_results.json)
- [R3 scored evidence](evidence/scored/MP005_SCORED_20261026_R3/)

The R3 campaign used separate state directories and an independently detached provider-launch procedure.

Earlier state histories and evidence were retained.

## 14. Scored Evidence Integrity

Each final R3 scored case preserves a SHA-256 inventory.

| Case | Inventory Entries | Scored Outcome |
|---|---:|---|
| R01 Provider A | 67 | PASS |
| R02 Provider B | 67 | PASS |
| Total | 134 | Both PASS |

Inventories:

- [R01 SHA-256 inventory](evidence/scored/MP005_SCORED_20261026_R3/R01/SHA256SUMS.txt)
- [R02 SHA-256 inventory](evidence/scored/MP005_SCORED_20261026_R3/R02/SHA256SUMS.txt)

The inventories identify the original captured files and their hashes.

The preserved case directories contain authorization artifacts, process identities, state snapshots, consumption ledgers, execution records, and correlated boundary evidence.

The publication audit reported successful integrity verification of these inventories.

An inventory match supports byte-level evidence preservation.

It does not independently establish that every recorded assertion is technically correct.

Independent review of the test result requires examining both the evidence and the scoring method.

## 15. Recorded Physical Runtime Identities

The final R3 case identity records bind the evidence to the tested provider source files.

Provider A:

[evidence/scored/MP005_SCORED_20261026_R3/R01/case_identity.json](evidence/scored/MP005_SCORED_20261026_R3/R01/case_identity.json)

Provider B:

[evidence/scored/MP005_SCORED_20261026_R3/R02/case_identity.json](evidence/scored/MP005_SCORED_20261026_R3/R02/case_identity.json)

These records contain:

- Case identifier.
- Session identifier.
- Provider identity.
- Runtime source path.
- Runtime SHA-256.
- State path.
- Execution-log path.

The restart evidence additionally compares process identity, start time, host, boot identifier, runtime, command line, working directory, and state paths.

The recorded R3 process transitions occurred on the same host and operating-system boot.

No host reboot or physical power-loss claim is made.

## 16. Historical Review Status

Some published technical reviews predate the physical rehearsal and scored campaigns.

For example:

[MP005_R3_REVIEW_SUPPLEMENT.json](notes/MP005_R3_REVIEW_SUPPLEMENT.json)

contains:

`"scored_evidence_found_under_MP005": false`

That statement describes the review's historical scope when it was created.

It is not a claim that the later R3 scored evidence is absent from the published repository.

Likewise, frozen run-manifest fields may retain `NOT_RUN` values from planning or configuration-lock stages.

Historical reviews and manifests are preserved with their original content.

Later experimental outcomes are established by their separately recorded evidence.

This separation prevents retroactive alteration of the audit trail.

## 17. Historical Technical-Record Limitation

[HARDENING_TECHNICAL_RECORD.json](provenance/HARDENING_TECHNICAL_RECORD.json) contains technical observations extracted from an earlier hardening handoff.

The record identifies the earlier source as:

`notes/MP005_HARDENING_HANDOFF.json`

It also preserves the source SHA-256.

That original handoff file is not included at the referenced path in the published MP005 tree.

The retained technical record is therefore useful as a documented historical extraction, but a reviewer cannot independently compare it against the omitted original using the published tree alone.

The verified runtime sources, implementation manifests, simulation evidence, and scored evidence provide separate inspection paths.

No claim is made that the omitted handoff itself was independently revalidated from the published repository.

## 18. Publication Preservation Rules

The MP005 publication distinguishes historical experimental material from current explanatory documentation.

The original historical records should remain unchanged.

This includes:

- Frozen provider and intermediary implementations.
- Historical configuration locks.
- Campaign authorizations.
- Simulation evidence.
- Physical preflight and rehearsal records.
- Unsuccessful scored evidence.
- Successful scored evidence.
- Provider-local state histories.
- Signed association records.
- Original SHA-256 inventories.
- Technical reviews and preservation records.

Explanatory README, RESULTS, and PROVENANCE documents may be maintained without changing the original experiment.

Changes to documentation do not retroactively alter the frozen implementation or scored results.

Historical scripts and authorization records may contain references to original local workspace paths.

Those paths are preserved as historical context and should not be silently rewritten to suggest a different original environment.

Where obsolete administrative material was excluded from publication, the retained provenance records must not be interpreted as proof that every earlier workspace file is present.

## 19. Independent Verification Procedure

An independent reviewer can examine MP005 using the following sequence.

### Step 1 — Identify the Campaign

Select the exact session being evaluated.

Do not combine records from different campaigns.

### Step 2 — Resolve Its Configuration

Use:

[CAMPAIGN_CONFIGURATION_MAP.json](provenance/CAMPAIGN_CONFIGURATION_MAP.json)

Identify the original configuration directory, authorization reference, and canonical lock.

### Step 3 — Verify Configuration Bytes

Recompute SHA-256 for the files identified by the applicable configuration lock.

Use the historical path-resolution rules when necessary.

### Step 4 — Verify Implementation Bytes

Compare the implementation and harness source files against their preserved SHA-256 identities.

Distinguish historical baseline implementations from hardened R2 and R3 candidates.

### Step 5 — Verify Evidence Inventories

Recompute the hashes for the original case evidence.

Resolve inventory paths relative to their documented directory.

Do not replace missing historical evidence with files from a different campaign.

### Step 6 — Inspect Consumption History

Independently inspect the recorded ledger.

Verify:

- Provider identity.
- Entry sequence.
- Authorization identity.
- Previous-entry hash linkage.
- Recomputed entry hashes.
- Absence of duplicate consumed authorization identifiers.
- Agreement with the materialized snapshot.

### Step 7 — Inspect Process Restart

Compare the recorded pre-restart and post-restart identities.

Verify that the required runtime and persistent-state continuity assertions are supported.

### Step 8 — Inspect Replay

Confirm that the exact original authorization was reused.

Verify `auth_spent` denial and absence of additional consumption or execution.

Examine the signed boundary evidence and provider-local records.

### Step 9 — Inspect Fresh Authorization

Confirm that a distinct authorization was issued.

Verify one new linked ledger entry, one recorded execution, and the required signed observations.

### Step 10 — Compare the Classification

Compare the independently derived observations with the preserved case result.

Retain NON-PASS and NOT_RUN classifications where applicable.

Do not treat a favorable summary as a substitute for the original evidence.

## 20. Limits of Provenance Verification

SHA-256 verification establishes byte identity relative to a trusted reference.

It does not independently establish:

- The correctness of all implementation logic.
- The honesty of an originating host.
- The accuracy of every recorded timestamp.
- The absence of a compromise before evidence capture.
- The completeness of omitted historical source files.
- A trusted external timestamp or immutable ledger anchor.
- Physical execution of a software-recorded event.

The provider consumption ledger is internally hash-linked.

An attacker capable of replacing both the consumption ledger and materialized snapshot with an older mutually consistent history remains outside the established MP005 protection.

The association recorder can preserve signed observations of previously recorded ledger heads, but MP005 does not use those observations as an automatic remote freshness authority controlling execution.

The scored experiment does not establish power-loss, reboot, crash-window, concurrency, or hardware-actuation guarantees.

Those properties require separate evidence.

## 21. Conclusion

MP005 preserves a traceable relationship among:

- Historical implementation baselines.
- Hardened provider versions.
- Frozen R3 source identities.
- Configuration locks.
- Operator campaign authorizations.
- Simulation evidence.
- Physical rehearsal evidence.
- Unsuccessful scored observations.
- Successful scored observations.
- Provider-local consumption history.
- Signed independent boundary records.
- SHA-256 inventories.

The final scored R3 campaign records PASS results for Provider A and Provider B within the specified idle forced-process restart conditions.

Both providers preserved previously consumed authority as spent, rejected exact replay without additional execution, and successfully processed separate fresh authorization.

The results remain subject to the stated technical limitations.

**The provenance record preserves what was tested, which implementation was used, which configuration applied, and where the supporting evidence is retained.**

It does not enlarge the observed experimental claims.

---

## Related Documents

- [MP005 README](README.md)
- [RESULTS.md](RESULTS.md)
- [Evidence README](evidence/README.md)
- [Configuration README](configs/README.md)
- [Test contract](configs/MP005_CONTRACT.md)
- [Source manifest](configs/MP005_SOURCE_MANIFEST.json)
- [Implementation manifest](configs/MP005_IMPLEMENTATION_MANIFEST.json)
- [Validated code inventory](provenance/R3_VALIDATED_CODE_SHA256SUMS.txt)
