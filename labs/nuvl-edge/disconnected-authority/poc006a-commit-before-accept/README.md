# POC-006A — Commit Before Accept Under Boundary Crash

## Status

PASS

## Classification

Category 1 — NUVL core, no architecture change.

POC-006A extends persistent single-use authority enforcement by testing interruption after durable consumption of authority but before the requester can rely on an accepted result.

The test does not introduce a new authority source, delegate provider authority, or permit the enforcement boundary to originate or enlarge authority.

## Purpose

Earlier disconnected-authority tests established that consumed single-use authority remained consumed across replay, process restart, host power loss, and concurrent contention.

POC-006A tests a critical crash boundary:

> What happens if the enforcement boundary durably consumes a single-use authority and then crashes before the accepted result is successfully completed to the requester?

The safe behavior is not to restore the authority merely because the requester did not receive ACCEPT.

Once authority has been durably consumed, uncertainty about delivery of the result must not recreate that authority.

## Authority Property Under Test

The tested invariant is:

```text
valid single-use authority
        ->
spend accepted internally
        ->
spent state durably committed
        ->
boundary crashes before ACCEPT completes
        ->
boundary restarts
        ->
same authority presented again
        ->
DENY
```

The critical ordering is:

```text
validate authority
        ->
commit consumption
        ->
ACCEPT may be returned
```

not:

```text
validate authority
        ->
return ACCEPT
        ->
attempt to record consumption later
```

The requester receiving no successful accepted response does not imply that the authority remains available.

## Test Topology

```text
Provider
   |
   | issues bounded single-use authority
   v
Provider-signed authority artifact
   |
   v
ESP32-S3 requester
   |
   | /spend
   v
Raspberry Pi persistent boundary
   |
   +---- verifies authority
   +---- verifies request binding
   +---- checks spent state
   +---- commits authority as spent
   |
   X
BOUNDARY TERMINATED
before accepted result completes
   |
   | restart
   v
Raspberry Pi persistent boundary
   |
   +---- reloads spent state
   |
   ^
   | same authority replayed
   |
ESP32-S3 requester
   |
   v
DENY / replay_detected
```

## Repository Files

### `poc006_prepare_crash_artifact_archer.py`

Prepares the provider-issued single-use authority artifact used for the crash test.

The artifact is retained so that the exact same authority can be presented again after the boundary restarts.

### `poc006_crash_spend_archer.py`

Executes the spend associated with the controlled crash condition.

The test is designed around the boundary being terminated after the authority's consumed state has become durable but before the accepted response successfully completes to the requester.

The resulting requester-side failure or absence of ACCEPT is intentionally ambiguous with respect to whether authority was consumed.

That ambiguity must not be resolved by granting the authority again.

### `poc006_replay_after_crash_archer.py`

Executes the post-restart replay attempt.

After the boundary is restarted, the same authority used in the interrupted spend is submitted again.

The required result is:

```text
decision=denied
reason=replay_detected
```

A second ACCEPT would indicate that interruption reopened authority that had already been durably consumed.

## Test Procedure

### 1. Prepare Single-Use Authority

Run:

```text
poc006_prepare_crash_artifact_archer.py
```

Prepare one provider-issued bounded authority artifact with a single permitted use.

Retain the artifact for the entire test.

### 2. Begin the Crash Spend

Run:

```text
poc006_crash_spend_archer.py
```

Submit the authority to the enforcement boundary.

The boundary validates the authority and enters the consumption path.

### 3. Commit Consumption

The boundary records the artifact as spent using its persistent replay-state mechanism.

The relevant ordering requirement is:

```text
durable spent-state persistence
BEFORE
successful ACCEPT completion
```

Once that durable commit occurs, the authority is consumed.

### 4. Terminate the Boundary

Terminate the enforcement-boundary process after durable persistence but before the accepted result successfully completes to the requester.

The requester therefore cannot infer from the missing result that the authority was not consumed.

### 5. Restart the Boundary

Restart the persistent enforcement boundary.

The boundary reloads its durable spent state.

The previously consumed artifact must remain present in that authority history.

### 6. Replay the Same Authority

Run:

```text
poc006_replay_after_crash_archer.py
```

Submit the same authority again.

The expected result is:

```text
decision=denied
reason=replay_detected
```

## PASS Criteria

POC-006A passes only if:

1. A valid provider-issued single-use authority is prepared.
2. The authority enters the valid spend path.
3. The boundary durably records the authority as consumed.
4. Durable consumption occurs before successful ACCEPT completion.
5. The boundary is terminated after the durable commit.
6. The requester does not receive a successful accepted result from the interrupted transaction.
7. The boundary is restarted.
8. Persistent spent state is recovered.
9. The same authority is submitted again.
10. The replay is denied as previously consumed.
11. The crash does not recreate or restore the authority.

## Observed Result

PASS.

The single-use authority entered the valid spend path.

The boundary durably persisted the consumed state.

The boundary was then terminated with `SIGKILL` after persistence and before successful completion of the accepted result to the requester.

After restart, the persistent state still identified the authority as consumed.

The same authority was submitted again.

The replay was denied.

The interrupted response path therefore did not recreate the consumed authority.

## Supported Claim

Within the tested implementation and crash position:

> Provider-issued single-use authority that was durably consumed before a boundary crash remained consumed after restart, even though the accepted result did not successfully reach the requester.

The test supports the bounded-authority invariant:

```text
uncertainty about result delivery
must not
recreate durably consumed authority
```

This is deliberately an authority-preservation rule rather than an availability-first recovery rule.

If the system cannot prove that previously established authority remains available, it must not silently manufacture replacement authority from an ambiguous transaction outcome.

## Why This Matters

Distributed request/response systems contain an unavoidable ambiguity when failure occurs between state change and response delivery.

A requester may observe:

```text
request sent
        ->
connection lost / no ACCEPT received
```

while the enforcement boundary has actually performed:

```text
request validated
        ->
authority consumed
        ->
consumption durably committed
        ->
crash
```

Treating the missing response as proof that the operation never occurred would permit a retry to enlarge single-use authority.

POC-006A tests the opposite rule:

```text
durable authority consumption
takes precedence over
response-delivery uncertainty
```

The consequence is intentionally fail-closed.

A requester may lose the practical benefit of an authority whose result was interrupted, but the boundary does not compensate for that uncertainty by granting another use.

## What This Test Does Not Prove

POC-006A does not establish:

- exactly-once execution;
- exactly-once physical actuation;
- that the requester received the effect associated with the consumed authority;
- behavior for crashes before durable persistence;
- behavior during every internal stage of the persistence operation;
- correctness for every filesystem or storage failure;
- recovery from corrupted or missing persistent state;
- multi-use authority accounting;
- arbitrary distributed consensus;
- production transaction guarantees;
- safety certification.

In particular, this test does not claim that a consumed authority necessarily produced its intended external effect.

It establishes that once consumption became durable, interruption did not make that authority available again.

## Relationship to Other Tests

POC-006A extends the disconnected-authority progression into transaction-interruption behavior.

```text
POC-003
single-use authority
first use accepted
reuse denied

        ↓

POC-004
consumption survives
boundary process restart

        ↓

POC-004B
consumption survives
boundary-host power loss

        ↓

POC-005
concurrent contention
one authority remains one use

        ↓

POC-006A
consumption committed
boundary crashes before ACCEPT completes
authority remains spent
```

The distinction in POC-006A is the placement of the failure relative to authority consumption and result delivery.

## Publication Notes

The repository files are publication copies of the test artifacts.

Environment-specific deployment values are replaced with placeholders where required.

The test documents one deliberately exercised crash window. It should not be interpreted as proof that every possible persistence or crash window has been tested.

The supported property is narrower:

> Once the tested implementation had durably consumed the authority, a subsequent crash and restart did not recreate it.
