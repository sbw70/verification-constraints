# POC-004B — Persistent Replay State Across Host Power Loss

## Status

PASS

## Classification

Category 1 — NUVL core, no architecture change.

POC-004B extends persistent single-use authority enforcement from process restart to complete Raspberry Pi power loss.

The test does not introduce a new authority source, delegate provider authority, or permit the enforcement boundary to originate or enlarge authority.

## Purpose

POC-004 established that consumed single-use authority remained consumed after the enforcement-boundary process was restarted.

POC-004B tests a stronger persistence boundary:

> Does complete loss of power to the boundary host erase the fact that authority has already been consumed?

The required behavior is fail-closed persistence.

A provider-issued single-use artifact consumed before power loss must remain spent after the Raspberry Pi is powered back on and the boundary is restarted.

Power loss must not recreate authority.

## Authority Property Under Test

The tested invariant is:

```text
authority consumed
        ->
spent state durably persisted
        ->
boundary host loses power
        ->
host powers back on
        ->
persistent state reloaded
        ->
same authority presented again
        ->
DENY
```

The relevant authority is provider-issued, bounded, and single-use.

The test determines whether durable spent-state enforcement survives loss of the boundary host's volatile runtime state.

## Test Topology

```text
Provider
   |
   | issues signed bounded authority
   v
Provider-signed single-use artifact
   |
   v
ESP32-S3 requester
   |
   | /spend
   v
Raspberry Pi persistent boundary
   |
   +---- verifies provider signature
   +---- verifies artifact/request binding
   +---- enforces single-use constraint
   +---- persists spent state
   |
   v
ACCEPT

        [Raspberry Pi power removed]

        [Raspberry Pi powered back on]

ESP32-S3 requester
   |
   | same artifact / same authority
   v
Raspberry Pi persistent boundary
   |
   +---- reloads durable spent state
   +---- recognizes artifact as consumed
   |
   v
DENY / replay_detected
```

## Repository Files

### `poc004b_prepare_powercycle_artifact_archer.py`

Prepares the authority artifact used for the power-loss test.

The resulting authority is retained across the initial spend and subsequent power-cycle replay so that the same bounded authority can be presented on both sides of the host power-loss event.

### `poc004b_initial_spend_archer.py`

Executes the initial spend before power is removed from the Raspberry Pi.

The client submits the prepared single-use authority to the enforcement boundary.

The required result is an accepted spend with the authority recorded as consumed before the power-loss phase begins.

### `poc004b_replay_after_powerloss_archer.py`

Executes the replay attempt after the Raspberry Pi has been powered back on and the enforcement boundary has restarted.

The same authority used before power loss is submitted again.

The required result is denial because the authority was already consumed before the host lost power.

## Test Procedure

### 1. Prepare the Authority

Run:

```text
poc004b_prepare_powercycle_artifact_archer.py
```

Prepare and retain the provider-issued single-use authority that will be used throughout the test.

The same artifact must be used for both the initial spend and the post-power-loss replay.

### 2. Perform the Initial Spend

Run:

```text
poc004b_initial_spend_archer.py
```

Submit the single-use authority to the persistent enforcement boundary.

The initial spend must be accepted.

At this point, the authority is consumed and its spent state must exist outside volatile process memory.

### 3. Remove Power From the Boundary Host

After the accepted spend has completed, remove power from the Raspberry Pi.

This terminates:

- the enforcement-boundary process;
- the operating-system runtime;
- volatile application state;
- volatile process memory.

The persistent storage containing the spent-state record is retained.

### 4. Restore Power

Power the Raspberry Pi back on.

Restart the persistent enforcement boundary.

The boundary must recover the previously recorded spent state from persistent storage.

No manual recreation of the consumed-state entry is permitted.

### 5. Replay the Same Authority

Run:

```text
poc004b_replay_after_powerloss_archer.py
```

Submit the same single-use authority that was accepted before power loss.

The expected result is:

```text
decision=denied
reason=replay_detected
```

## PASS Criteria

POC-004B passes only if all of the following occur:

1. A provider-issued single-use authority is prepared.
2. The authority is accepted during its initial spend.
3. The accepted authority is recorded as consumed.
4. The Raspberry Pi subsequently loses power.
5. The Raspberry Pi is powered back on.
6. The enforcement boundary restarts.
7. Previously persisted spent state remains available after restart.
8. The exact previously consumed authority is presented again.
9. The replay is denied.
10. Power loss does not restore, refresh, or recreate the consumed authority.

## Observed Result

PASS.

The single-use authority was accepted before the Raspberry Pi power-loss event.

After the accepted spend, power to the Raspberry Pi was removed.

The Raspberry Pi was subsequently powered back on and the persistent enforcement boundary restarted.

The same previously consumed authority was then presented again.

The replay was denied.

The consumed state therefore survived the complete boundary-host power cycle.

## Supported Claim

Within the tested implementation and conditions:

> Consumption of provider-issued single-use authority survived complete power loss and restart of the enforcement-boundary host, and the previously consumed authority remained unavailable for reuse after recovery.

The test supports the bounded-authority invariant:

```text
loss of volatile host state
must not
recreate previously consumed authority
```

POC-004B therefore extends the persistence result beyond an application-process restart to loss and restoration of the boundary host itself.

## What This Test Does Not Prove

POC-004B does not establish:

- correctness for power loss occurring at every possible point inside the persistence operation;
- behavior if power is removed before durable persistence completes;
- atomicity across every filesystem or storage failure;
- resistance to deliberate modification or deletion of persistent state;
- startup behavior with corrupted, malformed, missing, zero-byte, or inaccessible state;
- arbitrary concurrent double-spend resistance;
- multi-use authority accounting;
- exactly-once physical execution;
- production storage durability guarantees;
- safety certification.

Those conditions require separate tests.

## Relationship to Other Tests

POC-004B extends the persistence sequence established by POC-003 and POC-004.

```text
POC-003
single-use disconnected authority
first use accepted
reuse denied

        ↓

POC-004
authority consumed
boundary process restarted
reuse still denied

        ↓

POC-004B
authority consumed
boundary host loses power
host restarts
reuse still denied
```

The progression distinguishes persistence across ordinary process restart from persistence across complete loss of the host's volatile runtime state.

Later tests examine additional failure boundaries, including concurrent contention and interruption during persistence.

## Publication Notes

The repository files are publication copies of the test artifacts.

Environment-specific deployment values are replaced with placeholders where required.

The test should be interpreted as evidence for the specific persistence and bounded-authority property documented here. It is not presented as a general-purpose authorization, persistence, or storage implementation.
