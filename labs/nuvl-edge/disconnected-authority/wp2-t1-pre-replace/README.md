# WP2-T1 — Pre-Replace Crash Window

## Status

PASS

## Classification

Category 1 — NUVL core, no architecture change.

WP2-T1 tests a persistence crash window inside the disconnected single-use authority path.

The test does not introduce a new authority source, delegate provider authority, or permit the enforcement boundary to originate or enlarge authority.

## Purpose

Earlier persistence tests established that consumed single-use authority remained consumed across process restart, host power loss, and concurrent contention.

WP2-T1 narrows the focus to the persistence operation itself.

The specific question is:

> What happens if the boundary crashes after the replacement state has been written and `fsync()`ed to a temporary file, but before that temporary file replaces the established persistent state file?

The required behavior is fail closed with respect to authority.

A temporary file created during an interrupted persistence attempt must not be mistaken for committed authority history.

At the same time, an authority whose consumption was not committed must not be falsely treated as spent merely because an orphan temporary file exists.

## Authority Property Under Test

The tested sequence is:

```text
valid single-use authority
        ->
spend begins
        ->
candidate spent state written to temporary file
        ->
temporary file flushed and fsync()ed
        ->
boundary crashes BEFORE os.replace()
        ->
temporary file remains
        ->
boundary restarts
        ->
established state remains authoritative
        ->
same authority retried
        ->
ACCEPT
        ->
consumption committed normally
        ->
same authority replayed
        ->
DENY
```

The key distinction is between:

```text
durable temporary data
```

and:

```text
committed authoritative state
```

An `fsync()`ed temporary file is not, by itself, the committed replay-state record.

## Repository Files

The directory contains four test clients:

- `wp2_t1_prepare_temp_fsync_artifact_archer.py`
- `wp2_t1_crash_spend_archer.py`
- `wp2_t1_retry_commit_after_restart_archer.py`
- `wp2_t1_replay_check_archer.py`

### `wp2_t1_prepare_temp_fsync_artifact_archer.py`

Prepares the provider-issued bounded authority used throughout the test.

The client:

- requests issuance through `/issue`;
- requires `decision=issued`;
- requires `reason=provider_signed_bounded_artifact`;
- requires successful provider verification;
- saves the returned package and original issuance binding into `wp2_t1_temp_fsync_artifact.json`;
- instructs the operator to stop the provider before the crash phase.

### `wp2_t1_crash_spend_archer.py`

Executes the spend associated with the controlled pre-replace crash.

The client:

- verifies that the provider is offline;
- loads the retained authority package;
- submits the spend directly over a socket;
- requires the request transmission to complete;
- expects the boundary connection to terminate without a valid HTTP response;
- preserves the authority artifact for post-restart testing.

The expected client-side result is:

```text
EXPECTED_CRASH_NO_RESPONSE
```

The absence of a valid response is intentional for this phase.

### `wp2_t1_retry_commit_after_restart_archer.py`

Retries the same authority after the boundary restarts.

The provider must remain offline.

The required result is:

```text
decision=accepted
reason=offline_artifact_admissible
provider_verified=True
provider_contacted_for_spend=False
replay_state_persisted_before_accept=True
```

This establishes that the interrupted pre-replace operation did not falsely commit the authority as spent.

### `wp2_t1_replay_check_archer.py`

Submits the same authority once more after the successful retry has committed consumption.

The required result is:

```text
decision=denied
reason=replay_detected
provider_verified=True
provider_contacted_for_spend=False
```

This confirms that the subsequent normal commit became authoritative and that the authority could not then be reused.

## Persistence Window Under Test

The relevant persistence sequence is conceptually:

```text
construct candidate state
        ->
write temporary file
        ->
flush temporary file
        ->
fsync temporary file
        ->
os.replace(temp, persistent)
        ->
fsync containing directory
```

WP2-T1 interrupts execution here:

```text
construct candidate state
        ->
write temporary file
        ->
flush temporary file
        ->
fsync temporary file
        ->
CRASH
        ->
os.replace() never occurs
```

The resulting temporary file may contain a complete and durable representation of the candidate state.

That does not make it the established state.

## Test Procedure

### 1. Prepare the Authority

Run:

```text
wp2_t1_prepare_temp_fsync_artifact_archer.py
```

The issuance step must complete successfully.

The authority package is retained in:

```text
wp2_t1_temp_fsync_artifact.json
```

### 2. Make the Provider Unavailable

Stop the provider before beginning the crash-spend phase.

The remaining spend and replay decisions are evaluated without provider contact.

### 3. Execute the Controlled Crash Spend

Run:

```text
wp2_t1_crash_spend_archer.py
```

The boundary is deliberately terminated after the candidate state has been written and `fsync()`ed to the temporary file but before the replacement operation commits that file as the established persistent state.

The client must observe no valid HTTP response.

### 4. Restart the Boundary

Restart the enforcement boundary.

The orphan temporary file must not be promoted merely because it exists.

The previously established persistent state remains authoritative.

### 5. Retry the Same Authority

Run:

```text
wp2_t1_retry_commit_after_restart_archer.py
```

Because the interrupted operation never reached the replacement commit point, the authority should still be available.

The required result is:

```text
decision=accepted
reason=offline_artifact_admissible
replay_state_persisted_before_accept=True
```

The retry now completes the normal persistent-consumption path.

### 6. Verify Replay Denial

Run:

```text
wp2_t1_replay_check_archer.py
```

Submit the same authority again.

The required result is:

```text
decision=denied
reason=replay_detected
```

## PASS Criteria

WP2-T1 passes only if all of the following occur:

1. A valid provider-issued single-use authority is prepared.
2. The provider is unavailable before the crash-spend phase.
3. The spend request reaches the enforcement boundary.
4. The candidate replay state is written to the temporary state file.
5. The temporary state file is flushed and `fsync()`ed.
6. The boundary is terminated before the replacement operation commits the candidate state.
7. The client receives no valid HTTP response from the interrupted spend.
8. The boundary restarts without treating the orphan temporary file as committed authority history.
9. The same authority can be retried successfully.
10. The successful retry persists consumption before ACCEPT.
11. A subsequent use of the same authority is denied as replay.
12. The interrupted temporary state neither falsely consumes authority nor enlarges authority.

## Observed Result

PASS.

The controlled crash occurred after the temporary replay-state file had been written and `fsync()`ed but before the replacement step.

The interrupted request produced no valid HTTP response.

After restart, the orphan temporary file was not treated as the committed replay-state record.

The same authority was retried and was accepted.

That successful retry persisted the authority as consumed.

A subsequent attempt to use the same authority was then denied as:

```text
decision=denied
reason=replay_detected
```

The test therefore distinguished durable temporary data from committed persistent authority state.

## Supported Claim

Within the tested implementation and crash position:

> A crash after temporary-file `fsync()` but before replacement did not cause the uncommitted temporary state to become authoritative after restart. The same authority remained usable once, was then durably consumed by a successful retry, and subsequent replay was denied.

The test supports the persistence invariant:

```text
temporary persistence
does not equal
committed authority state
```

It also preserves the bounded-authority rule in both directions:

```text
an incomplete commit must not
silently consume authority

and

a later successful commit must not
permit authority reuse
```

## Why This Matters

Crash-safe persistence is not only about preventing lost writes.

For bounded authority, the system must also know which state representation is authoritative after interruption.

A temporary file may be:

- complete;
- flushed;
- present on persistent storage;
- individually durable.

None of those properties alone establish that it replaced the prior authoritative state.

Treating an orphan temporary file as committed could falsely consume authority.

Ignoring a properly committed replacement could recreate authority.

WP2-T1 tests the first side of that boundary.

## What This Test Does Not Prove

WP2-T1 does not establish:

- behavior for a crash before the temporary file is flushed;
- behavior during `fsync()` itself;
- behavior during `os.replace()`;
- behavior after replacement but before directory `fsync()`;
- behavior under underlying storage corruption;
- behavior when the established persistent state is missing or malformed;
- exactly-once physical execution;
- arbitrary distributed consensus;
- multi-use authority accounting;
- production storage guarantees;
- safety certification.

Those are separate failure windows and require separate tests.

## Relationship to Other Tests

WP2-T1 extends the persistence work from coarse restart events into a specific internal commit window.

```text
POC-004
process restart after committed spend

        ↓

POC-004B
host power loss after committed spend

        ↓

POC-006A
crash after committed consumption
before ACCEPT completion

        ↓

WP2-T1
crash BEFORE replacement commit
after temporary-file fsync
```

The distinction is important:

```text
POC-006A:
consumption already committed
-> authority must remain spent

WP2-T1:
consumption not yet committed
-> authority must not be falsely marked spent
```

Together, the tests define both sides of the persistence commit boundary.

## Publication Notes

The repository contains the client-side test harnesses for this failure-window test.

Environment-specific deployment values should be sanitized in publication copies where required.

The test should be interpreted narrowly as evidence for the specific pre-replace crash window exercised here.

It does not establish that every possible filesystem, storage, or interruption window has been tested.
