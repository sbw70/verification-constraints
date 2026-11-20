# MP005 — Provider-Controlled Authority Persistence Across Process Restart

**Project:** Xer0trust / Neutral Unified Verification Layer (NUVL)

**Experiment:** MP005 — Multi-Provider Durable Authority

**Final scored campaign:** `MP005_SCORED_20261026_R3`

**Recorded results: Provider A PASS | Provider B PASS**

## Overview

MP005 evaluates whether independently controlled providers can preserve single-use execution authority across process termination and restart without transferring that authority to an intermediary.

The experiment uses two separate provider domains, a stateless NUVL forwarding intermediary, and an independent association recorder.

Each provider validates its own authorization, records consumption in a durable local ledger, and independently determines whether execution is permitted.

The intermediary forwards requests but does not originate, validate, or enlarge provider authority.

The association recorder observes signed provider boundary events but does not authorize execution.

**The central question is whether an interrupted provider process can restart without making previously consumed authority executable again.**

## Architecture

The tested request path is:

    Requester
        |
        v
    NUVL Intermediary
        |
        +--------------------+
        |                    |
        v                    v
    Provider A           Provider B
        |                    |
        |                    |
        +---------+----------+
                  |
                  v
         Association Recorder
         (Boundary Evidence)

Provider A and Provider B independently evaluate forwarded requests.

Neither provider must approve the other's execution.

Neither provider receives authority to execute on behalf of the other.

The intermediary does not possess provider authorization-signing keys.

The association recorder does not become a shared authorization engine.

The providers remain responsible for determining whether an operation may produce an execution consequence.

## Primary Test Objective

MP005 tests whether a provider can preserve the consumed status of an authorization across an idle forced-process restart.

The scored procedure requires:

1. Issue a valid provider-specific authorization.
2. Submit the authorization through the intermediary.
3. Verify durable consumption and exactly one recorded execution.
4. Capture the original provider process and persistent state.
5. Reach the required idle checkpoint.
6. Terminate the provider process under operator control.
7. Restart the same provider implementation using the same persistent state.
8. Submit the exact previously consumed authorization again.
9. Verify denial without additional consumption or execution.
10. Submit a separate fresh authorization.
11. Verify successful consumption and exactly one fresh execution.

The restart must be established using actual process identity evidence, not merely an application-reported restart status.

The provider's persistent consumption history must survive the process transition.

## Durable Authority Enforcement

MP005 extends the provider implementation with a durable, hash-linked authorization consumption ledger.

Each provider maintains:

- An append-only consumption ledger.
- A materialized spent-authority snapshot.
- An execution log.

The ledger records authorization identity, operation identity, sequence, previous-entry hash, and current-entry hash.

Provider-local consumption precedes execution.

For an accepted request, the implementation:

1. Verifies provider-specific authorization.
2. Checks that the authority has not already been consumed.
3. Appends the consumption record.
4. Flushes and calls `fsync` on the consumption ledger.
5. Persists the spent-state snapshot.
6. Emits a signed START boundary event.
7. Records execution.
8. Emits a signed COMPLETE boundary event.

If required consumption persistence fails, execution is not admitted.

The validated ledger is authoritative for reconstructing consumed authority following process restart.

The materialized snapshot is reconciled against that ledger.

A previously consumed authorization must not become executable merely because the process has restarted or the snapshot is behind the validated ledger.

### Important Boundary

The provider's consumption ledger is local to that provider.

Provider A does not depend on Provider B's ledger.

Provider B does not depend on Provider A's ledger.

Neither ledger is maintained by the NUVL intermediary.

The association recorder receives signed observations but does not control consumption or execution.

## Experimental Progression

MP005 preserves the complete progression from baseline characterization through hardened testing and the final scored campaign.

| Campaign | Classification | Result |
|---|---|---|
| Simulation R1 | Baseline characterization | Rollback weakness observed |
| Simulation R2 | Hardened implementation | Tested cases passed; reconciliation blocker identified |
| Simulation R3 | Revised hardened implementation | 12/12 PASS |
| Physical preflight | Host and configuration verification | Recorded |
| Physical rehearsal | Provider A and B restart tests | R01 PASS / R02 PASS |
| Scored R2 | Initial scored campaign | R01 NON-PASS / R02 NOT_RUN |
| Scored R3 | Final scored campaign | R01 PASS / R02 PASS |

### Baseline Finding

The original R1 simulation demonstrated that rolling back the earlier implementation's materialized spent state could restore previously consumed authority.

The R1 S03 cases recorded successful characterization of this weakness.

Their PASS classification does not mean rollback resistance was established.

### Hardening

The subsequent implementation introduced a durable provider-local consumption ledger.

R2 simulation established the tested hardened behavior but also exposed a reconciliation semantics issue during independent review.

R3 refined startup snapshot reconciliation and passed all 12 recorded simulation cases.

### Physical Scored R2

The initial scored R2 campaign did not satisfy all acceptance requirements.

Provider A successfully demonstrated consumption persistence and replay denial, but the fresh authorization was consumed without the required execution record and signed completion.

R01 remained NON-PASS.

Provider B R02 was NOT_RUN.

The failure and its evidence remain preserved.

### Physical Scored R3

The replacement campaign used separately isolated state and a detached provider-launch procedure.

Both scored cases completed successfully.

The previous R2 evidence was not overwritten or retroactively reclassified.

## Final Scored Results

**Session:** `MP005_SCORED_20261026_R3`

| Requirement | Provider A — R01 | Provider B — R02 |
|---|---|---|
| Initial authorization consumed | PASS | PASS |
| Durable ledger entry verified | PASS | PASS |
| Initial execution recorded | PASS | PASS |
| New process instance established | PASS | PASS |
| Existing state preserved | PASS | PASS |
| Exact replay denied `auth_spent` | PASS | PASS |
| No replay execution | PASS | PASS |
| No additional replay consumption | PASS | PASS |
| Fresh authorization executed once | PASS | PASS |
| Fresh ledger entry verified | PASS | PASS |
| **Final case status** | **PASS** | **PASS** |

Both cases used the same host and operating-system boot before and after process restart.

The evidence includes process identities, consumption-ledger snapshots, execution records, signed boundary observations, and SHA-256 inventories.

The results establish the tested restart-durability behavior.

They do not establish durability across every possible interruption or adversarial condition.

### Primary Evidence

**Provider A — R01**

- [R01 case results](evidence/scored/MP005_SCORED_20261026_R3/R01/case_results.json)
- [R01 complete evidence](evidence/scored/MP005_SCORED_20261026_R3/R01/)
- [R01 SHA-256 inventory](evidence/scored/MP005_SCORED_20261026_R3/R01/SHA256SUMS.txt)

**Provider B — R02**

- [R02 case results](evidence/scored/MP005_SCORED_20261026_R3/R02/case_results.json)
- [R02 complete evidence](evidence/scored/MP005_SCORED_20261026_R3/R02/)
- [R02 SHA-256 inventory](evidence/scored/MP005_SCORED_20261026_R3/R02/SHA256SUMS.txt)

**Additional evidence**

- [R3 association records](evidence/scored/MP005_SCORED_20261026_R3/association/)
- [R3 runtime logs](evidence/scored/MP005_SCORED_20261026_R3/runtime/)
- [Preserved unsuccessful R2 campaign](evidence/scored/MP005_SCORED_20261025_R2/)
- [Accepted physical rehearsal](evidence/preflight/MP005_REHEARSAL_20261024_R1/)

## Repository Structure

| Directory | Purpose |
|---|---|
| [provider_a/](provider_a/) | Provider A authorization, consumption, execution, and signing |
| [provider_b/](provider_b/) | Provider B authorization, policy enforcement, consumption, and signing |
| [intermediary/](intermediary/) | Stateless NUVL request forwarding |
| [association/](association/) | Independent signed boundary evidence recorder |
| [harness/](harness/) | Test execution, state inspection, process verification, and scoring |
| [configs/](configs/) | Test contracts, manifests, configuration locks, and historical revisions |
| [evidence/](evidence/) | Simulation, preflight, rehearsal, scored results, and technical reviews |
| [simulation/](simulation/) | Linux-local simulation implementation |
| [baseline/](baseline/) | Preserved earlier implementation and configuration snapshots |
| [live_state/](live_state/) | Retained provider-local state histories |
| [notes/](notes/) | Technical review records and implementation comparisons |
| [provenance/](provenance/) | Integrity contexts, source identities, and campaign configuration mapping |
| [scripts/](scripts/) | Historical laboratory operator tooling |

The repository contains 1,404 published files, including implementation, configurations, evidence, and historical records.

The evidence directory contains 1,247 files.

The historical material is retained to support inspection of both successful and unsuccessful observations.

## Source and Configuration Integrity

The experiment preserves SHA-256 identities for the tested implementation and harness.

Primary references:

- [Source manifest](configs/MP005_SOURCE_MANIFEST.json)
- [Implementation manifest](configs/MP005_IMPLEMENTATION_MANIFEST.json)
- [Harness manifest](configs/MP005_HARNESS_MANIFEST.json)
- [Run manifest](configs/MP005_RUN_MANIFEST.json)
- [Experimental contract](configs/MP005_CONTRACT.md)
- [Final configuration lock](configs/MP005_LOCK_SHA256SUMS.txt)
- [Validated code inventory](provenance/R3_VALIDATED_CODE_SHA256SUMS.txt)

Earlier campaign configurations are preserved separately under:

[configs/history/](configs/history/)

The correspondence between historical configurations and recorded campaigns is documented in:

[CAMPAIGN_CONFIGURATION_MAP.json](provenance/CAMPAIGN_CONFIGURATION_MAP.json)

Historical evidence must be verified against the configuration that was active for its original campaign.

Later configuration revisions must not be substituted for earlier experimental records.

## Authority and Observation Boundaries

MP005 distinguishes four separate functions.

**Intermediary:** Receives and forwards request material. It does not issue provider authority or decide whether execution is permitted.

**Provider:** Validates authorization, enforces policy, durably consumes authority, and determines whether execution is admitted.

**Association recorder:** Receives and verifies signed provider boundary events. It records observations without controlling provider execution.

**Test harness:** Verifies implementation identity, captures evidence, correlates observations, and scores defined experimental conditions.

The intermediary may fail, suppress, duplicate, or alter forwarded material.

Provider authorization constraints must not depend on trusting the intermediary.

A successful HTTP `204 No Content` response does not establish provider authorization or completed execution.

Execution evidence is evaluated using provider-local records and correlated signed boundary observations.

## Laboratory Deployment

The final physical experiment used separate networked systems.

| Role | Host | Recorded IP |
|---|---|---|
| Provider A | Dell `Xer0trust-3` | `192.168.1.118` |
| Provider B | HP `Xer0trust2` | `192.168.1.107` |
| NUVL intermediary | Raspberry Pi `nuvl-relay` | `192.168.1.100` |
| Association / controller | OmniBook `Xer0trust` | `192.168.1.102` |

The provider implementations ran on Linux hosts.

The addresses and filesystem paths are specific to the recorded laboratory configuration.

The included PowerShell launch script is historical operator tooling and references the original workspace layout.

It is not a portable, ready-to-run deployment procedure.

The repository also contains laboratory signing keys used by the test implementations.

These keys are published test fixtures, not production credentials.

The root-level rehearsal and scored authorization JSON files preserve historical operator phase approvals. They are distinct from the provider-signed authorization artifacts used to control execution.

## Evidence Preservation

The published experiment retains:

- Original simulation evidence.
- Historical implementation baselines.
- Configuration revisions.
- Physical preflight records.
- Accepted rehearsal evidence.
- The unsuccessful R2 scored campaign.
- The successful R3 scored campaign.
- Provider-local consumption and execution records.
- Signed association observations.
- Technical reviews.
- SHA-256 evidence inventories.

Historical source, configuration, and evidence files are preserved rather than rewritten to reflect later results.

The publication preparation included integrity verification and removal of redundant or obsolete publication material.

No additional physical experiment was performed as part of publication preparation.

The original captured evidence remains the basis for the reported experimental outcomes.

## Limitations

**The principal established result is preservation of consumed provider authority across the specific idle forced-process restarts tested.**

MP005 does not establish:

- Resistance to rollback of both the consumption ledger and materialized snapshot to an older mutually consistent history.
- Automatic enforcement of externally preserved ledger-head freshness.
- Persistence through physical power loss.
- Host reboot durability.
- Crash-window correctness during incomplete consumption.
- Concurrent double-spend resistance.
- Independent operating-system execution attestation.
- Physical actuator execution.
- Guaranteed transmission or delivery of signed boundary observations.

The hash-linked ledger provides internally verifiable consumption history.

It does not independently prove that the entire local history has not been replaced with an older mutually consistent version.

Signed provider boundary events support evidence correlation but are not independent hardware execution attestations.

These limitations remain applicable despite the final scored PASS results.

## Documentation

For detailed experimental outcomes:

[RESULTS.md](RESULTS.md)

For source, configuration, and evidence integrity:

[PROVENANCE.md](PROVENANCE.md)

For the complete evidence organization:

[evidence/README.md](evidence/README.md)

For implementation-specific behavior, consult the README in each component directory.

## Conclusion

MP005 demonstrates that two independently controlled providers can preserve locally consumed authority across the tested idle forced-process restart conditions.

Both providers rejected exact replay without additional execution and subsequently admitted separate fresh authorization.

The observed result depends on provider-local durable consumption enforcement rather than authority held by the intermediary.

**Forwarding does not create authority. Observation does not create authority. Execution remains provider-controlled.**

---

**Xer0trust — Define the boundary. Defend the authority.**
```

