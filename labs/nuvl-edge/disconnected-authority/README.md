# Disconnected Authority Tests

This directory contains the NUVL Edge Lab tests for provider-issued authority that remains bounded during temporary provider disconnection.

The tests examine whether a constrained endpoint or local verification boundary can exercise a narrowly scoped provider-issued artifact without converting that artifact into reusable, expandable, or locally minted authority.

The tested design separates:

- Provider issuance
- Local artifact verification
- Single-use enforcement
- Persistent replay state
- Endpoint action
- Recovery after restart, power loss, or injected crash

The core rule is:

> Disconnection may change availability, but it must not enlarge authority.

## What Is Being Tested

The disconnected-authority sequence evaluates whether a provider-issued artifact remains constrained by its original bounds when the provider is unavailable.

Depending on the test, those bounds include:

- Authorized device
- Authorized action
- Authorized context
- Nonce
- Validity period
- Signature
- Single-use state
- Replay state
- Persistent commit state

The test set includes valid use and deliberate negative cases. A PASS requires both correct acceptance and correct rejection.

## Directory Structure

```text
disconnected-authority/
├── README.md
│
├── poc003-single-use/
│   └── README.md
│
├── poc004b-power-loss/
│   └── README.md
│
├── poc005-double-spend/
│   └── README.md
│
├── poc006a-commit-before-accept/
│   └── README.md
│
└── wp2-t1-pre-replace/
    └── README.md
```

The earlier POC004 process-restart test is documented in the project history but is not included here as a complete reproduction package until the exact boundary version is tied conclusively to the recorded run.

## Test Sequence

The tests build on one another.

| Test | Result | Property exercised |
|---|---|---|
| POC003 | PASS | Provider-issued authority remains bounded and single-use during disconnection |
| POC004 | PASS | Replay state survives process restart |
| POC004B | PASS | Completed replay-state commit survives abrupt Raspberry Pi power loss |
| POC005 | PASS | Overlapping attempts produce exactly one acceptance |
| POC006A | PASS | Crash after commit but before response does not permit reuse |
| WP2-T1 | PASS | Crash before atomic replacement does not falsely consume the artifact |

POC004 remains part of the evidence history but is not yet treated as a complete public reproduction package.

## Common Architecture

The general disconnected-authority path is:

```text
Provider
   |
   | issues signed, bounded artifact
   v
Raspberry Pi verification boundary
   |
   | verifies signature and explicit bounds
   | checks persistent single-use state
   v
ESP32-S3 endpoint
   |
   | presents artifact or test request
   v
Accepted once or rejected
```

The provider retains the private signing key.

The local verification boundary may hold:

- Provider public verification material
- Bounded artifact data
- Persistent spent-state
- Temporary commit state required by the tested persistence method

The endpoint does not receive the provider private key and does not independently mint provider authority.

## Common Artifact Properties

The tested artifacts are intended to bind authority to explicit fields rather than functioning as general bearer credentials.

The tested field set varies by file version, but the validation matrix includes:

```text
device
action
context
nonce
validity period
signature
single-use status
```

A valid signature alone is not sufficient for acceptance.

The artifact must also satisfy the expected device, action, context, freshness, and replay conditions.

## POC003 — Bounded Disconnected Single Use

Folder:

```text
poc003-single-use/
```

POC003 establishes the base disconnected-authority behavior.

The provider issues a signed artifact before disconnection. The artifact is then exercised through the local boundary while the provider is unavailable.

The tested matrix includes:

- Valid bounded offline use
- Replay
- Context mismatch
- Action mismatch
- Nonce mismatch
- Device mismatch
- Tampered artifact
- Unsigned artifact
- Expired artifact
- Missing artifact

Expected behavior:

```text
valid bounded use        -> accepted once
replay                   -> denied
context mismatch         -> denied
action mismatch          -> denied
nonce mismatch           -> denied
device mismatch          -> denied
tampering                -> denied
unsigned material        -> denied
expired artifact         -> denied
missing artifact         -> denied
```

Known client-side files include:

```text
poc003_esp32_prepare_housewifi.py
poc003_esp32_spend_v2_housewifi.py
```

Known boundary candidate:

```text
poc003_pi_boundary_housewifi.py
```

Two provider candidates exist in the original working set:

```text
poc003_ed25519_provider.py
poc003_ed25519_provider_1h.py
```

Only the provider version tied to the recorded house-network test should be identified as the canonical reproduction file.

Best last-known end-to-end client:

```text
poc003_esp32_spend_v2_housewifi.py
```

## POC004 — Replay State Across Restart

POC004 demonstrated that spent-state enforcement survived boundary process restart.

Known files from the original test history include:

```text
poc004_pi_boundary_persistent.py
poc004_pi_boundary_persistent_archer.py
poc004_esp32_spend_before_restart.py
poc004_esp32_replay_after_restart.py
```

The exact boundary version associated with the recorded run has not yet been mapped conclusively.

For that reason, POC004 is documented as a demonstrated result but is not currently presented as a complete public reproduction folder.

The test should not be reconstructed by mixing the original and Archer boundary variants without source-history or hash confirmation.

## POC004B — Replay State Across Power Loss

Folder:

```text
poc004b-power-loss/
```

POC004B extends persistent replay enforcement from process restart to abrupt Raspberry Pi power loss.

Test sequence:

```text
prepare artifact
start persistent boundary
perform initial valid spend
confirm acceptance
remove Raspberry Pi power
restore Raspberry Pi power
restart boundary
replay the spent artifact
confirm denial
restore fleet services
```

Observed property:

> A completed persistent-state commit remained effective after abrupt Raspberry Pi power loss.

Known client-side files include:

```text
poc004b_prepare_powercycle_artifact_archer.py
poc004b_initial_spend_archer.py
poc004b_replay_after_powerloss_archer.py
```

The tested boundary implementation was:

```text
poc004b_pi_boundary_powercycle_archer.py
```

Its public release is a separate publication decision.

Curated evidence includes:

```text
poc004b_archer_evidence_20260730_225507.log
post_powercycle_fleet_restoration_20260730_231251.log
poc004b_local_manifest_20260731_232149.txt
```

The restoration sequence eventually returned the three-endpoint fleet to normal operation.

One endpoint required reset before timely participation resumed. That anomaly remains part of the test record.

## POC005 — Concurrent Double-Spend

Folder:

```text
poc005-double-spend/
```

POC005 submits overlapping attempts against one single-use artifact.

Known client-side files include:

```text
poc005_prepare_race.py
poc005_concurrent_double_spend.py
```

The tested boundary implementation was:

```text
poc005_pi_boundary_persistent_archer.py
```

Its public release is a separate publication decision.

Expected outcome:

```text
attempts started:  2
accepted:          1
denied:            1
duplicate accept:  0
```

PASS requires exactly one successful exercise.

Zero accepts is not PASS.

More than one accept is not PASS.

This test does not claim mathematically simultaneous execution. It demonstrates single-use enforcement under near-concurrent competing attempts.

## POC006A — Commit Before Accept

Folder:

```text
poc006a-commit-before-accept/
```

POC006A tests the crash window after persistent state has been committed but before the successful response is returned.

Known client-side files include:

```text
poc006_prepare_crash_artifact_archer.py
poc006_crash_spend_archer.py
poc006_replay_after_crash_archer.py
```

The tested boundary implementation was:

```text
poc006_crash_window_boundary_archer.py
```

Its public release is a separate publication decision.

Test sequence:

```text
prepare artifact
submit valid spend
commit spent-state
inject crash before response
restart boundary
retry the same artifact
confirm replay denial
```

Observed property:

> A crash after persistent commit but before response did not permit the artifact to be accepted again.

The absence of a successful response did not reverse the completed commit.

## WP2-T1 — Crash Before Atomic Replacement

Folder:

```text
wp2-t1-pre-replace/
```

WP2-T1 tests the opposite persistence window: a crash before atomic replacement of the committed state file.

Known client-side files include:

```text
wp2_t1_prepare_temp_fsync_artifact_archer.py
wp2_t1_crash_spend_archer.py
wp2_t1_retry_commit_after_restart_archer.py
wp2_t1_replay_check_archer.py
```

The tested boundary was:

```text
wp2_t1_pre_replace_boundary_archer.py
```

Confirmed SHA-256:

```text
87351DBDF539E0E44480B28B205AE04FAD796D9C60DA9C4084FDEFDA49A9BFC8
```

Do not substitute:

```text
wp2_t1_temp_fsync_boundary_archer.py
```

That similarly named file has different contents and was not the tested boundary.

Test sequence:

```text
prepare artifact
begin persistent update
write and fsync temporary state
inject crash before atomic replacement
restart boundary
retry the interrupted commit
confirm successful completion
attempt replay
confirm replay denial
```

Observed property:

> A crash before atomic replacement did not falsely consume the artifact. The interrupted commit could be retried after restart, after which replay remained denied.

Curated final evidence:

```text
wp2_t1_final_evidence_20260801_010225.log
```

Known evidence details:

```text
Size: 5,374 bytes
SHA-256:
5BB1053A0AF88831F59D8D346D524F10F1E432C5B6D7A3A2A2342312120BBF20
```

The smaller phase logs should be added only after their exact filenames, sizes, and hashes are captured.

## Intentionally Withheld Boundary Implementations

Some verification-boundary implementations used in these tests are intentionally not included in the current public release.

The public packages may instead include:

- Available client sequence
- Boundary interface
- Expected request structure
- Expected response structure
- Failure-injection procedure
- Expected result
- Observed result
- PASS criteria
- Evidence
- Source and evidence hashes
- Limitations

This is an intentional publication-boundary decision, not a missing-file error.

See the [Publication Boundary](../README.md#publication-boundary) section in the main NUVL Edge Lab README.

## Reproduction Expectations

A test folder should not be considered independently reproducible merely because some files are present.

A complete reproduction package must identify:

- Exact files used
- Public or withheld boundary status
- Provider version
- Public-key deployment method
- Artifact preparation procedure
- Network topology
- Service ports
- Persistent-state location
- State-reset procedure
- Failure-injection step
- Expected outcome
- PASS criteria
- Evidence files
- SHA-256 values
- Known anomalies

A similarly named file must not be substituted for a tested file without hash or source-history confirmation.

## Source Classes

Published files are classified as one of the following:

### Original tested source

The exact file used in the recorded test.

### Sanitized public derivative

A copy modified to remove credentials, private values, or environment-specific configuration.

### Rerun-confirmed public source

A sanitized or reorganized public copy that was executed again and confirmed against the documented PASS criteria.

Do not attach an original tested hash to a modified public copy.

Each sanitized derivative must receive its own SHA-256 in:

```text
../evidence/SHA256SUMS.txt
```

The hash entry should identify the file as a sanitized derivative.

## Generated State

The following are generated runtime state and should not be treated as normal source files:

```text
*_artifact.json
*_spent_state*.json
*_spent_state*.json.tmp
*_crash_stage.txt
*.pid
nohup.out
```

Provider-signed artifacts are not private keys, but they contain test-specific bindings and signatures.

They should remain in the private evidence bundle unless a sanitized fixture is deliberately selected for public release.

## Private Material

Do not publish:

```text
*.pem
*.key
*_private.*
credentials*.json
secrets*.json
.env
.env.*
```

The provider private signing key must remain outside the public repository.

Public verification material may be included only when it is clearly identified as test material and does not expose private signing material.

## Evidence

Curated evidence belongs under:

```text
../evidence/
```

Each test-folder README should identify:

- Evidence filename
- Test identifier
- Date
- File size
- SHA-256
- Relevant source version
- Expected result
- Observed result
- Any anomaly or setup incident

See [`../evidence/README.md`](../evidence/README.md) for the evidence index and verification procedure.

## Limitations and Open Work

The current tests do not establish every possible persistence or concurrency property.

Open work includes:

- Additional crash points outside POC006A and WP2-T1
- Startup with corrupt persistent state
- Startup with truncated persistent state
- Startup with structurally invalid persistent state
- Recovery after persistent-state corruption is detected
- Cross-process contention
- Multi-boundary contention
- Long-duration repeated power-cycle campaigns
- Independent reproduction by an external laboratory

The PASS results apply to the tested paths and fault-injection points.

They should not be generalized beyond those conditions without additional evidence.

## Recommended Test Order

Run the tests in this order:

1. Original fleet baseline
2. POC003 valid bounded single use
3. POC003 negative-path matrix
4. POC004B power-loss persistence
5. POC005 overlapping double-spend
6. POC006A crash after commit
7. WP2-T1 crash before atomic replacement

A reproducer should establish normal fleet and boundary operation before attempting power-loss or crash-injection tests.
