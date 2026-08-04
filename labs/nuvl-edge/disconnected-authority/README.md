# NUVL Edge — Disconnected Authority

This directory contains the NUVL Edge Lab tests for provider-issued authority that remains bounded during temporary provider disconnection.

The tests examine whether a constrained endpoint and local verification boundary can exercise a narrowly scoped, provider-issued artifact without converting it into reusable, expandable, or locally minted authority.

The governing rule is:

> Disconnection may change availability, but it must not enlarge authority.

## What These Tests Demonstrate

The disconnected-authority tests cover:

- Provider issuance of a signed, bounded artifact
- Local verification using provider public verification material
- Device, action, context, nonce, and validity constraints
- Single-use enforcement
- Replay denial
- Persistent spent-state
- Process-restart recovery
- Abrupt power-loss recovery
- Overlapping spend attempts
- Crash after persistent commit but before response
- Crash before atomic state replacement

Together, the tests examine whether bounded authority remains bounded when the provider is temporarily unavailable and when the local verification path is interrupted.

## Architecture

The general test path is:

```text
Provider
   |
   | issues signed, bounded artifact
   v
ESP32-S3 endpoint or test client
   |
   | presents artifact and bounded request
   v
Raspberry Pi verification boundary
   |
   | verifies provider signature
   | verifies device, action, context, nonce, and validity
   | checks single-use or spent-state
   v
Accepted once or denied
```

The provider retains the private signing key.

The local verification boundary may hold:

- Provider public verification material
- The presented artifact
- Persistent spent-state
- Temporary state required by the tested commit procedure

The endpoint does not receive the provider private key and does not independently mint provider authority.

## Artifact Bounds

The exact artifact structure varies between tests, but the validation set includes checks for:

```text
device
action
context
nonce
validity period
signature
single-use status
```

A valid signature alone is not enough for acceptance.

The artifact must also match the expected device, action, context, nonce, validity period, and replay state.

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

The earlier POC004 process-restart test remains part of the test history but is not currently presented as a complete public reproduction package because the exact boundary version associated with the recorded run has not been conclusively identified.

## Test Summary

| Test | Result | Property exercised |
|---|---|---|
| POC003 | PASS | Provider-issued authority remains bounded and single-use during disconnection |
| POC004 | PASS | Replay state survives verification-boundary process restart |
| POC004B | PASS | A completed spent-state commit survives abrupt Raspberry Pi power loss |
| POC005 | PASS | Overlapping attempts produce exactly one acceptance |
| POC006A | PASS | A crash after commit but before response does not permit reuse |
| WP2-T1 | PASS | A crash before atomic replacement does not falsely consume the artifact |

The results apply to the tested paths and fault-injection points.

## POC003 — Bounded Disconnected Single Use

Folder:

```text
poc003-single-use/
```

POC003 establishes the base disconnected-authority behavior.

The provider issues a signed artifact before disconnection. The artifact is then presented to the local verification boundary while the provider is unavailable.

The test matrix includes:

- Valid bounded use
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

The recorded behavior demonstrated that provider disconnection did not convert the artifact into general or reusable authority.

TThe POC003 source set includes:

```text
poc003_ed25519_provider_1h.py
poc003_pi_boundary_housewifi.py
poc003_esp32_prepare_housewifi.py
poc003_esp32_spend_v2_housewifi.py
```

The provider issues an Ed25519-signed, single-use artifact before disconnection. The Raspberry Pi boundary verifies and enforces that artifact while the provider is unavailable.

## POC004 — Replay State Across Process Restart

POC004 tested whether spent-state enforcement survived restart of the Raspberry Pi verification-boundary process.

The test sequence was:

```text
prepare single-use artifact
perform initial valid spend
confirm acceptance
stop verification-boundary process
restart verification-boundary process
replay the same artifact
confirm denial
```

Observed result:

> Replay remained denied after verification-boundary process restart.

Files from the original test history include:

```text
poc004_pi_boundary_persistent.py
poc004_pi_boundary_persistent_archer.py
poc004_esp32_spend_before_restart.py
poc004_esp32_replay_after_restart.py
```

The exact boundary variant used in the recorded run has not been conclusively mapped, so POC004 is documented as a demonstrated result but is not currently included as a complete standalone folder.

## POC004B — Replay State Across Power Loss

Folder:

```text
poc004b-power-loss/
```

POC004B extends the persistent replay test from process restart to abrupt Raspberry Pi power loss.

The test sequence was:

```text
prepare artifact
start persistent verification boundary
perform initial valid spend
confirm acceptance
remove Raspberry Pi power
restore Raspberry Pi power
restart verification boundary
replay the spent artifact
confirm denial
restore fleet services
```

Observed result:

> A completed persistent-state commit remained effective after abrupt Raspberry Pi power loss.

Client-side files include:

```text
poc004b_prepare_powercycle_artifact_archer.py
poc004b_initial_spend_archer.py
poc004b_replay_after_powerloss_archer.py
```

The recorded verification-boundary implementation was:

```text
poc004b_pi_boundary_powercycle_archer.py
```

Evidence includes:

```text
poc004b_archer_evidence_20260730_225507.log
post_powercycle_fleet_restoration_20260730_231251.log
poc004b_local_manifest_20260731_232149.txt
```

### Recovery Result

After power restoration:

- The verification boundary recovered
- The fleet coordinator recovered
- The three-endpoint fleet eventually returned to normal operation
- One endpoint required reset before timely participation resumed

The recovery result is recorded as:

```text
PASS with anomaly
```

The endpoint reset does not invalidate the persistent replay result. It remains a documented operational recovery limitation.

## POC005 — Overlapping Double-Spend Attempts

Folder:

```text
poc005-double-spend/
```

POC005 submits two overlapping attempts against one single-use artifact.

Client-side files include:

```text
poc005_prepare_race.py
poc005_concurrent_double_spend.py
```

The recorded verification-boundary implementation was:

```text
poc005_pi_boundary_persistent_archer.py
```

Expected outcome:

```text
attempts started:  2
accepted:          1
denied:            1
duplicate accept:  0
```

PASS requires exactly one successful exercise.

```text
0 accepted -> FAIL
1 accepted -> PASS
2 accepted -> FAIL
```

This test does not claim mathematically simultaneous execution.

It demonstrates single-use enforcement under near-concurrent competing attempts in the tested path.

## POC006A — Crash After Commit, Before Response

Folder:

```text
poc006a-commit-before-accept/
```

POC006A tests the crash window after persistent spent-state has been committed but before the successful response is returned to the client.

Client-side files include:

```text
poc006_prepare_crash_artifact_archer.py
poc006_crash_spend_archer.py
poc006_replay_after_crash_archer.py
```

The recorded verification-boundary implementation was:

```text
poc006_crash_window_boundary_archer.py
```

The test sequence was:

```text
prepare artifact
submit valid spend
commit spent-state
inject crash before response
restart verification boundary
retry the same artifact
confirm replay denial
```

Observed result:

> A crash after persistent commit but before response did not permit the artifact to be accepted again.

The missing successful response did not reverse the completed commit.

## WP2-T1 — Crash Before Atomic Replacement

Folder:

```text
wp2-t1-pre-replace/
```

WP2-T1 tests the opposite persistence window: a crash before atomic replacement of the committed state file.

Client-side files include:

```text
wp2_t1_prepare_temp_fsync_artifact_archer.py
wp2_t1_crash_spend_archer.py
wp2_t1_retry_commit_after_restart_archer.py
wp2_t1_replay_check_archer.py
```

The recorded verification boundary was:

```text
wp2_t1_pre_replace_boundary_archer.py
```

Confirmed SHA-256:

```text
87351DBDF539E0E44480B28B205AE04FAD796D9C60DA9C4084FDEFDA49A9BFC8
```

Do not confuse it with:

```text
wp2_t1_temp_fsync_boundary_archer.py
```

That similarly named file has different contents and was not the verification boundary used in the recorded WP2-T1 test.

The test sequence was:

```text
prepare artifact
begin persistent-state update
write and fsync temporary state
inject crash before atomic replacement
restart verification boundary
retry the interrupted commit
confirm successful completion
attempt replay
confirm replay denial
```

Observed result:

> A crash before atomic replacement did not falsely consume the artifact. The interrupted commit could be retried after restart, after which replay remained denied.

Final evidence:

```text
wp2_t1_final_evidence_20260801_010225.log
```

Evidence details:

```text
Size:
5,374 bytes

SHA-256:
5BB1053A0AF88831F59D8D346D524F10F1E432C5B6D7A3A2A2342312120BBF20
```

## Public Test Packages

Some test folders do not include the mechanism-level verification-boundary implementation.

Those folders provide the available material needed to understand and evaluate the recorded test, including:

- Client sequence
- Boundary interface
- Request and response behavior
- Failure-injection point
- Expected result
- Observed result
- PASS criteria
- Evidence
- Relevant hashes
- Known limitations

Where a boundary source is not included, the test-folder README states that directly.

The omission is intentional and does not indicate that the file was accidentally lost from the repository.

## Common Test Flow

The disconnected-authority tests follow the same general operating sequence:

1. Start the provider when artifact issuance is required.
2. Issue a bounded artifact.
3. Transfer or prepare the artifact for the endpoint.
4. Start the Raspberry Pi verification boundary.
5. Confirm the provider public verification material is available locally.
6. Perform the initial valid exercise.
7. Apply the test-specific restart, outage, race, or crash condition.
8. Retry or replay the artifact.
9. Compare the result with the documented PASS criteria.
10. Preserve the test output and recovery result.

Each test-folder README provides its exact command sequence and prerequisites.

## Evidence

Evidence for these tests is stored under:

```text
../evidence/
```

The current public evidence set includes:

```text
poc004b_archer_evidence_20260730_225507.log
post_powercycle_fleet_restoration_20260730_231251.log
poc004b_local_manifest_20260731_232149.txt
wp2_t1_final_evidence_20260801_010225.log
```

See [`../evidence/README.md`](../evidence/README.md) for descriptions and verification commands.

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

1. Reproduce the original fleet baseline.
2. Run POC003 valid bounded single use.
3. Run the POC003 negative-path matrix.
4. Run POC004B power-loss persistence.
5. Run POC005 overlapping double-spend.
6. Run POC006A crash after commit.
7. Run WP2-T1 crash before atomic replacement.

Normal provider, endpoint, coordinator, and verification-boundary operation should be confirmed before attempting power-loss or crash-injection tests.
