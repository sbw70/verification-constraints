```markdown
# MP005 — Test Harness

## Purpose

The MP005 harness provides source-integrity verification, controlled service launching, evidence collection, process identity verification, and independent scoring for the multi-provider durability experiment.

The primary scored objective is to determine whether provider-consumed authorization remains spent across an idle forced process restart, without preventing a separate fresh authorization from executing.

The harness does not originate provider execution authority, replace provider authorization logic, or emulate provider persistence.

Provider A and Provider B retain control over their respective authorization and execution boundaries.

## Implementation

| File | Function |
|---|---|
| [common.py](common.py) | Shared evidence, authorization preparation, process identity, correlation, and scoring functions |
| [launch_provider.py](launch_provider.py) | Loads provider implementations with controlled runtime configuration |
| [launch_service.py](launch_service.py) | Launches the intermediary or association recorder using the selected configuration |
| [ledger_evidence.py](ledger_evidence.py) | Independent consumption-ledger inspection, validation, and explicit state initialization |
| [live_case.py](live_case.py) | Orchestrates authorized live test phases and produces scored results |
| [preflight.py](preflight.py) | Performs host-local source, process, and state checks |
| [test_hardening.py](test_hardening.py) | Offline adversarial validation of ledger and boundary behavior |
| [test_helpers.py](test_helpers.py) | Entry point for the current offline hardening checks |
| [test_reconciliation.py](test_reconciliation.py) | Offline snapshot-reconciliation classification tests |

The harness uses the frozen provider implementations and configuration records retained in the MP005 repository.

## Source Integrity

The harness verifies implementation and test-code identities against:

- [MP005_SOURCE_MANIFEST.json](../configs/MP005_SOURCE_MANIFEST.json)
- [MP005_HARNESS_MANIFEST.json](../configs/MP005_HARNESS_MANIFEST.json)
- [MP005_IMPLEMENTATION_MANIFEST.json](../configs/MP005_IMPLEMENTATION_MANIFEST.json)

Source files are checked using SHA-256.

A source mismatch prevents the corresponding verified operation from proceeding.

The provider launcher configures network addresses and state paths without replacing the provider's authorization, signature, persistence, or execution logic.

The frozen source identities are part of the experimental evidence.

## Execution Environment

The physical MP005 experiment used Linux provider hosts with provider-local persistent state.

The relevant environment includes:

- Python 3.10 or newer.
- The `cryptography` dependency declared in [requirements.txt](../requirements.txt).
- Linux process information under `/proc`.
- Native filesystem operations supporting the persistence calls used by the provider implementation.
- Separate provider state directories for the authorized test campaigns.

The live harness requires explicit phase authorization.

Simulation is restricted to loopback communication and uses separate evidence and state paths.

The simulation environment is not a substitute for physical-host persistence testing.

## Test Phases

The live harness provides the following actions:

| Action | Purpose |
|---|---|
| `initialize-state` | Explicitly initialize a new provider-local consumption ledger and snapshot |
| `prepare` | Prepare a case and its provider-specific authorization |
| `capture` | Capture provider process identity before or after restart |
| `capture-state` | Preserve provider state and execution evidence at a defined checkpoint |
| `consume` | Submit the original authorization and collect associated boundary observations |
| `checkpoint` | Validate the required pre-restart evidence and produce an operator checkpoint |
| `replay` | Resubmit the previously consumed authorization |
| `prepare-fresh` | Prepare a distinct authorization after replay validation |
| `fresh` | Submit the fresh authorization and collect associated boundary observations |
| `score` | Evaluate the preserved evidence against the case requirements |

These actions are implemented in [live_case.py](live_case.py).

The harness does not automatically terminate or restart provider processes.

The forced process termination and subsequent restart are operator-controlled actions.

A checkpoint must establish the required prior consumption and execution evidence before the operator proceeds with termination.

## Process Restart Verification

MP005 does not treat a new process identifier alone as sufficient evidence of a restart.

The harness captures and compares:

- Host identity.
- Operating-system boot identifier.
- Process identifier and start time.
- Runtime path and SHA-256 identity.
- Command line.
- Working directory.
- Persistent state path.

The scored restart must establish a genuinely different process instance using the same provider runtime and durable state.

The tested R3 restart remained on the same host and operating-system boot.

Host reboot and physical power-loss durability were not scored.

## Consumption Ledger Verification

[ledger_evidence.py](ledger_evidence.py) independently inspects provider consumption records.

The verifier checks:

- Provider identity.
- Ledger entry structure.
- Sequential ledger numbering.
- Previous-entry hash linkage.
- Recomputed entry hashes.
- Canonical JSON encoding.
- Duplicate authorization identifiers.
- Agreement between the ledger and materialized spent-state snapshot.

The verifier uses the original captured ledger bytes.

It does not treat a provider-reported PASS result as sufficient evidence of correct ledger behavior.

State initialization is explicit and requires a previously uninitialized ledger and snapshot.

Historical state must not be overwritten or recreated to reproduce a favorable outcome.

## Signed Boundary Correlation

The harness correlates provider-originated boundary records with the preserved authorization identity.

Correlation uses:

- Provider identity.
- Authorization identifier and nonce.
- Operation identifier.
- Request binding.
- Registered provider public key.
- Ed25519 signature verification.

The association recorder provides independently captured observations.

The harness uses recorder-log cursors to distinguish relevant events from earlier observations.

A final replay check also examines the continuous recorder log for late events.

HTTP `204 No Content` is not accepted as proof of authorization or execution.

## Scoring Requirements

The scored campaign contains two cases:

| Case | Provider | Objective |
|---|---|---|
| R01 | Provider A | Restart durability and single-use enforcement |
| R02 | Provider B | Restart durability and single-use enforcement |

Each case must establish the following sequence.

### 1. Initial consumption

A valid provider-specific authorization is accepted.

The provider must record:

- Exactly one new linked consumption entry.
- Exactly one execution.
- Signed `START` and `COMPLETE` observations.
- A spent-state snapshot consistent with the ledger.

### 2. Process restart

After the required idle checkpoint, the original provider process is terminated.

The restarted provider must:

- Be a different process instance.
- Use the same frozen runtime.
- Use the same persistent state.
- Preserve the previously recorded consumption and execution history.

### 3. Exact replay

The original authorization is submitted again.

Required observations include:

- Signed `DENY` with reason `auth_spent`.
- No additional consumption.
- No additional execution.
- No signed `START` or `COMPLETE` for the replay.
- Unchanged relevant persistent state.

### 4. Fresh authorization

A distinct provider authorization is submitted.

Required observations include:

- Successful authorization consumption.
- One additional linked ledger entry.
- One additional execution.
- Signed `START` and `COMPLETE`.
- Consistent updated provider state.

The case receives PASS only when the required checks are satisfied.

Process-local execution sequence continuity is not a scored requirement.

## Offline Validation

The harness includes two supporting offline test programs.

### Hardening checks

[test_hardening.py](test_hardening.py) exercises synthetic ledger structures, invalid entries, signature coverage, and related rejection behavior.

These checks do not start provider servers or execute the live experiment.

### Reconciliation checks

[test_reconciliation.py](test_reconciliation.py) exercises snapshot classification against synthetic ledger histories.

The checks include:

- Exact agreement.
- Valid earlier-prefix acceptance.
- Snapshot-ahead rejection.
- Divergent snapshot rejection.
- Invalid snapshot structures.
- Malformed JSON classification.

These are offline function-level tests.

They do not independently establish crash durability, filesystem persistence under power loss, or physical execution.

The separate Linux simulation campaigns provide additional runtime evidence within their recorded scope.

## Recorded Results

### Scored R2 — NON-PASS

Session: `MP005_SCORED_20261025_R2`

Provider A completed the initial consumption, process restart, and exact-replay requirements.

However, fresh authorization consumption was not followed by the required execution and signed completion.

R01 was classified NON-PASS.

Provider B R02 was NOT_RUN.

The failure remains preserved.

[R2 scored evidence](../evidence/scored/MP005_SCORED_20261025_R2/)

### Scored R3 — PASS

Session: `MP005_SCORED_20261026_R3`

| Case | Result |
|---|---|
| R01 — Provider A | PASS |
| R02 — Provider B | PASS |

Both providers preserved previously consumed authority across their respective idle forced-process restarts.

Exact replay was denied without additional execution.

A distinct fresh authorization subsequently executed once for each provider.

Evidence:

- [R01 case results](../evidence/scored/MP005_SCORED_20261026_R3/R01/case_results.json)
- [R02 case results](../evidence/scored/MP005_SCORED_20261026_R3/R02/case_results.json)
- [R3 scored evidence](../evidence/scored/MP005_SCORED_20261026_R3/)

The preserved case evidence includes original SHA-256 inventories.

## Historical Configuration

The original test configuration is preserved under [configs/](../configs/).

Historical campaign configurations are retained separately from the final R3 configuration.

Some frozen manifests contain planning-time `NOT_RUN` values.

Those values must not be interpreted as the final experimental disposition.

Actual outcomes are established by the preserved case results, association records, and technical reviews.

Configuration-to-campaign mapping is documented in:

[CAMPAIGN_CONFIGURATION_MAP.json](../provenance/CAMPAIGN_CONFIGURATION_MAP.json)

The published harness is a historical test implementation, not an authorization to rerun a scored campaign against existing state.

## Limitations

MP005 does not establish:

- Protection against rollback of the complete consumption ledger and snapshot to an older mutually consistent history.
- Durability across physical power loss.
- Durability across host reboot.
- Crash-window behavior during an incomplete consumption operation.
- Concurrent double-spend resistance.
- Independent operating-system execution attestation.
- Physical actuator behavior.
- Guaranteed delivery of signed boundary events.

The scored experiment evaluates provider-local authority consumption across the defined idle forced-process restart conditions.

It does not establish general durability under every possible system failure.

The harness is an evidence and verification mechanism. It is not an additional source of provider execution authority.

## Related Documentation

- [Provider A](../provider_a/)
- [Provider B](../provider_b/)
- [Association recorder](../association/)
- [NUVL intermediary](../intermediary/)
- [Configuration](../configs/)
- [Evidence](../evidence/)
- [MP005 root](../)
```
