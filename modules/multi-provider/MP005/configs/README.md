```markdown
# MP005 — Configuration and Integrity Manifests

## Purpose

This directory preserves the configuration, source identities, test contract, and integrity requirements used for the MP005 multi-provider durability experiment.

MP005 evaluates whether provider-controlled, single-use execution authority remains consumed across an idle forced process restart.

The configuration defines the experimental conditions. It does not originate provider authorization or grant execution authority to the intermediary, association recorder, or test harness.

Provider A and Provider B remain independently responsible for authorization validation, consumption enforcement, and execution.

## Directory Contents

| File | Purpose |
|---|---|
| [MP005_CONTRACT.md](MP005_CONTRACT.md) | Experimental objectives, acceptance criteria, deployment requirements, and limitations |
| [MP005_RUN_MANIFEST.json](MP005_RUN_MANIFEST.json) | Test cases, topology, runtime paths, campaign configuration, and phase information |
| [MP005_SOURCE_MANIFEST.json](MP005_SOURCE_MANIFEST.json) | Baseline and frozen implementation source identities |
| [MP005_IMPLEMENTATION_MANIFEST.json](MP005_IMPLEMENTATION_MANIFEST.json) | Implementation provenance, source hashes, hardening history, and harness identities |
| [MP005_HARNESS_MANIFEST.json](MP005_HARNESS_MANIFEST.json) | SHA-256 identities of the test harness and simulation code |
| [MP005_LOCK_SHA256SUMS.txt](MP005_LOCK_SHA256SUMS.txt) | Canonical integrity inventory for the five primary configuration files |
| [history/](history/) | Preserved configuration revisions associated with earlier campaigns |

The files are retained as experimental records.

Configuration revisions must not be treated as interchangeable merely because they describe the same test architecture.

## Test Contract

[MP005_CONTRACT.md](MP005_CONTRACT.md) defines the scored restart-durability requirements.

The principal claim is that previously consumed authorization remains spent after termination and restart of the same provider implementation using the same durable consumption history.

The scored experiment requires:

1. Valid provider authorization consumption.
2. A durable, hash-linked consumption ledger entry.
3. Recorded execution and signed boundary observations.
4. An operator-controlled idle process termination.
5. A genuinely new provider process instance.
6. Preservation of the existing consumption and execution history.
7. Rejection of exact authorization replay.
8. No additional consumption or execution from the replay.
9. Successful consumption and execution using separate fresh authority.

The contract also defines exclusions, including full-history rollback, power loss, host reboot, crash-window behavior, concurrency, and physical actuation.

The contract contains historical revisions and superseding campaign-specific sections.

Earlier planning or authorization language must be interpreted in its original campaign context, not as the final result of all subsequent testing.

## Run Manifest

[MP005_RUN_MANIFEST.json](MP005_RUN_MANIFEST.json) records the configured test environment.

### Scored Cases

| Case | Provider | Test |
|---|---|---|
| R01_PROVIDER_A_RESTART_DURABILITY | Provider A | Consumption persistence, restart, replay rejection, and fresh execution |
| R02_PROVIDER_B_RESTART_DURABILITY | Provider B | Consumption persistence, restart, replay rejection, and fresh execution |

The manifest also records simulation campaigns and their respective classifications.

### Physical Laboratory Topology

| Component | Recorded Address | Port |
|---|---|---|
| Provider A — Dell `Xer0trust-3` | `192.168.1.118` | 9090 |
| Provider B — HP `Xer0trust2` | `192.168.1.107` | 9090 |
| NUVL intermediary — Raspberry Pi | `192.168.1.100` | 8080 |
| Association recorder — OmniBook | `192.168.1.102` | 9191 |

Endpoints:

- Relay: `http://192.168.1.100:8080/nuvl`
- Provider A: `http://192.168.1.118:9090/ingest`
- Provider B: `http://192.168.1.107:9090/ingest`
- Association: `http://192.168.1.102:9191/boundary`

These addresses describe the recorded laboratory deployment.

They are not production defaults or evidence that the same addresses remain valid in a different environment.

### Provider State

The final R3 scored campaign used separate provider-local directories:

Provider A:

`/home/seth/MULTI_PROVIDER_005/live_state/scored/MP005_SCORED_20261026_R3/provider_a`

Provider B:

`/home/seth/MULTI_PROVIDER_005/live_state/scored/MP005_SCORED_20261026_R3/provider_b`

Each provider maintained its own:

- Consumption ledger.
- Materialized spent-authority snapshot.
- Execution log.

State histories were isolated from earlier rehearsal and scored campaigns.

The intermediary did not maintain these provider consumption records.

### Historical Status Fields

Some fields in the frozen run manifest retain `NOT_RUN` values, including planning-time scored-case and campaign status entries.

These are preserved configuration values, not the final disposition of the completed experiments.

The final campaign results are established from the original scored evidence and case-result files.

For the successful R3 campaign:

- R01 Provider A: PASS.
- R02 Provider B: PASS.

See:

- [R01 results](../evidence/scored/MP005_SCORED_20261026_R3/R01/case_results.json)
- [R02 results](../evidence/scored/MP005_SCORED_20261026_R3/R02/case_results.json)

The frozen manifest is not rewritten retrospectively to replace historical planning values with later outcomes.

## Source Manifest

[MP005_SOURCE_MANIFEST.json](MP005_SOURCE_MANIFEST.json) identifies the source files used by the experiment.

It distinguishes baseline material from the frozen MP005 implementation.

The frozen implementation includes:

- Provider A runtime.
- Provider B runtime.
- NUVL intermediary.
- Association recorder.
- Provider registry and trust keys.
- Provider-specific authorization issuers.
- Laboratory signing and verification keys.

Each listed file has an associated SHA-256 identity.

The baseline source commit is:

`fa541618b1a3bc58700a81b29129b17b35b1e0fc`

This identifies the earlier MP003 source baseline.

It does not mean that the hardened MP005 provider implementations are byte-identical to their MP003 predecessors.

Provider A and Provider B were modified for MP005 persistence and reconciliation behavior.

Their original and subsequent identities are retained for comparison.

## Implementation Manifest

[MP005_IMPLEMENTATION_MANIFEST.json](MP005_IMPLEMENTATION_MANIFEST.json) preserves the implementation history and integrity information.

It identifies:

- Frozen implementation files.
- Baseline source provenance.
- Hardened provider versions.
- R3 candidate versions.
- Test harness identities.
- Referenced review evidence.

### Provider Implementation History

| Provider | MP003 Baseline SHA-256 | R2 Hardened SHA-256 | R3 Candidate SHA-256 |
|---|---|---|---|
| Provider A | `c875582b...` | `a8ab30e1...` | `79e4994c...` |
| Provider B | `5e0ab4b7...` | `c7d3ab6d...` | `618ec76e...` |

The abbreviated values above are for identification only.

The complete SHA-256 values are preserved in the implementation manifest.

The R3 provider changes concerned snapshot reconciliation and related validation behavior.

The reviewed changes are documented in:

- [Provider A R3 patch](../notes/provider_a_R3_REVIEW_FROM_R2.patch)
- [Provider B R3 patch](../notes/provider_b_R3_REVIEW_FROM_R2.patch)
- [R3 review supplement](../notes/MP005_R3_REVIEW_SUPPLEMENT.json)

These records distinguish implementation changes from experimental observations.

## Harness Manifest

[MP005_HARNESS_MANIFEST.json](MP005_HARNESS_MANIFEST.json) records the SHA-256 identities of the frozen test code.

The manifest includes:

- Shared evidence functions.
- Provider and service launchers.
- Ledger inspection and validation.
- Live case orchestration.
- Host-local preflight checks.
- Offline hardening tests.
- Snapshot reconciliation tests.
- Simulation execution and review code.

The manifest contains 13 test-code entries.

The harness verifies relevant source and test-code identities before authorized operations.

The test harness does not replace the provider's persistence implementation or authorize execution independently.

See [harness/README.md](../harness/README.md).

## Canonical Configuration Lock

[MP005_LOCK_SHA256SUMS.txt](MP005_LOCK_SHA256SUMS.txt) preserves the final R3 configuration lock.

The lock covers five files:

1. `configs/MP005_CONTRACT.md`
2. `configs/MP005_SOURCE_MANIFEST.json`
3. `configs/MP005_HARNESS_MANIFEST.json`
4. `configs/MP005_IMPLEMENTATION_MANIFEST.json`
5. `configs/MP005_RUN_MANIFEST.json`

All paths in this lock are relative to the MP005 repository root.

The lock provides exact byte identities for the reviewed configuration.

It is not a substitute for provider authorization, and it does not independently prove that a test was executed.

Changing a locked file invalidates its recorded hash.

Historical configuration files should not be edited merely to make their status fields appear current.

## Historical Configuration Revisions

The [history/](history/) directory preserves configurations associated with earlier campaigns.

### Rehearsal Configuration

[MP005_REHEARSAL_LOCK_20261025/](history/MP005_REHEARSAL_LOCK_20261025/)

Contains the retained contract, run manifest, and lock associated with the accepted physical rehearsal.

Session:

`MP005_REHEARSAL_20261024_R1`

The rehearsal used a different configuration and state context from the final scored R3 campaign.

### Scored R2 Configuration

[MP005_SCORED_20261025_R2/](history/MP005_SCORED_20261025_R2/)

Contains the retained contract, run manifest, and lock associated with the earlier scored campaign.

Session:

`MP005_SCORED_20261025_R2`

The R2 campaign did not satisfy the complete scored requirements.

Provider A R01 was NON-PASS because fresh authorization consumption was not followed by the required execution and signed completion.

Provider B R02 was NOT_RUN.

The original R2 configuration and evidence remain preserved.

### Scored R3 Configuration

The current files in `configs/` represent the final R3 scored configuration.

Session:

`MP005_SCORED_20261026_R3`

Both scored cases passed within the defined experimental scope.

The final R3 configuration must not be substituted when independently validating earlier campaign records.

## Configuration-to-Evidence Mapping

The relationship between configuration revisions and recorded campaigns is preserved in:

[CAMPAIGN_CONFIGURATION_MAP.json](../provenance/CAMPAIGN_CONFIGURATION_MAP.json)

This file identifies:

- Campaign session.
- Applicable configuration directory.
- Association recorder session-start record.
- Contract SHA-256.
- Run manifest SHA-256.
- Operator authorization reference.
- Canonical configuration lock SHA-256.

The recorder's `SESSION_START` evidence preserves the configuration identities observed during each campaign.

A reviewer should resolve a campaign's recorded hashes against its corresponding historical configuration.

For historical file-resolution rules, see:

[INTEGRITY_CONTEXTS.json](../provenance/INTEGRITY_CONTEXTS.json)

Historical records are preserved byte-for-byte.

They must not be silently modified or evaluated against a different campaign's configuration.

## Authorization and Execution Separation

Configuration integrity is distinct from provider execution authority.

The manifests identify the expected implementation and environment.

Provider-issued authorization artifacts determine whether the provider can admit a particular request.

The intermediary does not receive authority to originate or enlarge provider authorization.

The association recorder verifies and preserves signed events but does not authorize execution.

The harness performs checks and collects evidence but does not override provider decisions.

Each provider independently controls its authorization, consumption, and execution boundary.

## Reproduction and Safety Constraints

The published files preserve the tested implementation and historical laboratory configuration.

They do not constitute an authorization to rerun a scored campaign using existing state.

A separate experiment requires:

- Explicit operator authorization.
- Verified source and configuration identities.
- Confirmed network and deployment paths.
- Distinct session identification.
- Fresh, isolated state directories.
- Preserved historical evidence.
- Appropriate preflight and stop-condition checks.

Provider consumption ledgers and spent-state snapshots must not be reset to manufacture a fresh test condition.

The laboratory private keys included in the repository are not production credentials.

The historical launcher and deployment paths are environment-specific and should not be treated as a general deployment procedure.

## Limitations

Configuration and SHA-256 verification establish file identity, not universal correctness or runtime trustworthiness.

MP005 does not establish:

- Resistance to rollback of both the consumption ledger and materialized snapshot to an older mutually consistent history.
- External ledger-head freshness enforcement.
- Durability through physical power loss.
- Host reboot durability.
- Crash-window correctness.
- Concurrent double-spend resistance.
- Hardware execution attestation.
- Physical actuator behavior.

These limitations apply even though the final R3 scored cases passed.

The evidence supports the specific restart-durability behavior tested, not every possible failure or adversarial condition.

## Related Documentation

- [MP005 root](../)
- [Provider A](../provider_a/)
- [Provider B](../provider_b/)
- [NUVL intermediary](../intermediary/)
- [Association recorder](../association/)
- [Test harness](../harness/)
- [Evidence](../evidence/)
- [Provenance records](../provenance/)
```

