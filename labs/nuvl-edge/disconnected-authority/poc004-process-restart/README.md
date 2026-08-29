# POC-004 — Persistent Replay State Across Boundary Restart

## Status

PASS

## Classification

Category 1 — NUVL core, no architecture change.

POC-004 extends the disconnected single-use authority path by testing whether consumed authority remains consumed after the enforcement-boundary process is restarted.

The test does not introduce a new authority source, delegate provider authority, or permit the boundary to originate or enlarge authority.

## Purpose

POC-003 established that a provider-issued single-use authority artifact could be consumed while the provider was unavailable and that subsequent reuse was denied.

POC-004 tests the next persistence boundary:

> Does restarting the enforcement-boundary process erase the fact that authority has already been consumed?

The required behavior is fail-closed persistence.

A provider-issued single-use artifact accepted before restart must remain spent after restart. Restarting the boundary must not recreate authority.

## Authority Property Under Test

The tested invariant is:

```text
authority consumed
        ->
spent state durably persisted
        ->
boundary process restarted
        ->
spent state reloaded
        ->
same authority presented again
        ->
DENY
```

The provider remains unavailable during the spend and replay phases.

The boundary therefore cannot consult the provider to reconstruct, refresh, or reauthorize the consumed authority.

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
   +---- verifies request/artifact binding
   +---- enforces max_uses = 1
   +---- persists spent state before ACCEPT
   |
   v
ACCEPT

        [boundary process restart]

ESP32-S3 requester
   |
   | same artifact / same authority
   v
Raspberry Pi persistent boundary
   |
   +---- reloads persistent spent state
   +---- recognizes artifact as consumed
   |
   v
DENY / replay_detected
```

The provider is not contacted to authorize either the offline spend or the replay decision.

## Repository Files

### `poc004_esp32_spend_before_restart.py`

ESP32-side first-spend test.

The client:

- confirms that the provider is unavailable before proceeding;
- loads the previously issued authority package;
- submits the artifact to `/spend`;
- requires an accepted result;
- requires `reason=offline_artifact_admissible`;
- requires successful provider-signature verification;
- requires `provider_contacted_for_spend=False`;
- requires confirmation that replay state was persisted before ACCEPT;
- preserves the artifact for the post-restart replay test.

The publication copy uses a placeholder for the Raspberry Pi address.

### `poc004_esp32_replay_after_restart.py`

ESP32-side replay test executed after the boundary process is restarted.

The client:

- confirms that the provider remains unavailable;
- checks boundary health;
- requires persistent replay state to be enabled;
- confirms that previously spent state was loaded;
- resubmits the same authority;
- requires `decision=denied`;
- requires `reason=replay_detected`;
- confirms that the provider signature remains valid;
- confirms that the provider was not contacted for the replay decision.

### `poc004_pi_boundary_persistent.py`

Persistent Raspberry Pi enforcement boundary used for the test.

The boundary maintains spent-artifact state outside process memory and reloads that state at startup.

For an accepted spend, the implementation prepares the updated spent-state document and persists it before returning ACCEPT.

The persistence sequence includes:

```text
write temporary state file
        ->
flush
        ->
fsync temporary file
        ->
replace persistent state file
        ->
fsync containing directory
        ->
return ACCEPT
```

This ordering ensures that the tested implementation does not intentionally return an accepted spend before recording the corresponding consumed authority.

## Test Procedure

### 1. Establish Single-Use Authority

A provider-signed bounded authority artifact is prepared through the disconnected-authority issuance path.

The artifact is bound to the expected:

```text
device_id
context
requested_action
nonce
```

and carries single-use offline authority:

```text
offline_allowed = true
max_uses = 1
```

### 2. Make the Provider Unavailable

The provider is taken offline before the authority is spent.

The ESP32 client verifies provider unavailability before continuing.

### 3. Consume the Authority

Run:

```text
poc004_esp32_spend_before_restart.py
```

The required first-spend result is:

```text
decision=accepted
reason=offline_artifact_admissible
provider_verified=True
provider_contacted_for_spend=False
replay_state_persisted_before_accept=True
```

At this point the single-use authority has been consumed.

### 4. Restart the Boundary Process

Restart the Raspberry Pi enforcement-boundary process.

The persistent spent-state file is retained.

The provider remains unavailable.

### 5. Replay the Same Authority

Run:

```text
poc004_esp32_replay_after_restart.py
```

Before submitting the replay, the client confirms that the restarted boundary reports persistent replay-state support and has loaded spent state.

The same previously consumed authority is then submitted again.

The required result is:

```text
decision=denied
reason=replay_detected
provider_verified=True
provider_contacted_for_spend=False
```

## PASS Criteria

POC-004 passes only if all of the following occur:

1. The original single-use authority is accepted while the provider is unavailable.
2. The provider signature is successfully verified locally.
3. The provider is not contacted to authorize the spend.
4. Spent state is persisted before the accepted result is returned.
5. The boundary process is restarted.
6. The restarted boundary reloads the persistent spent state.
7. The provider remains unavailable.
8. The same authority is presented again.
9. The replay is denied as `replay_detected`.
10. Restarting the boundary does not restore or recreate consumed authority.

## Observed Result

PASS.

The original single-use authority was accepted while the provider was unavailable.

The consumed authority was recorded in persistent replay state.

After the Raspberry Pi boundary process was restarted, the persistent state was reloaded.

Reusing the same authority produced:

```text
decision=denied
reason=replay_detected
```

The provider remained unavailable during the replay decision.

The process restart did not restore or recreate the consumed authority.

## Supported Claim

Within the tested implementation and conditions:

> Consumption of provider-issued single-use authority survived an enforcement-boundary process restart, and reuse of that authority after restart was denied without contacting the provider.

The test demonstrates that the tested boundary did not rely solely on volatile process memory to remember consumed authority.

It also supports the bounded-authority invariant:

```text
loss of runtime process state
must not
recreate previously consumed authority
```

## What This Test Does Not Prove

POC-004 does not establish:

- persistence across complete host power loss;
- correctness during interruption inside the persistence operation;
- atomicity across every possible filesystem or storage failure;
- resistance to malicious modification of persistent state;
- exactly-once physical execution;
- multi-use authority accounting;
- arbitrary concurrent double-spend resistance;
- startup behavior when persistent state is missing, truncated, malformed, zero-byte, or inaccessible;
- production storage durability guarantees;
- safety certification.

Those conditions are addressed, where applicable, by separate tests.

## Relationship to Other Tests

POC-004 builds directly on POC-003.

```text
POC-003
single-use disconnected authority
first use accepted
subsequent reuse denied

        ↓

POC-004
single-use disconnected authority
first use accepted
boundary process restarted
reuse still denied
```

Later tests extend the same authority-consumption property across additional failure boundaries, including host power loss, concurrent contention, crash timing, and persistent-state startup integrity.

## Publication Notes

The repository files are publication copies of the test artifacts.

Environment-specific deployment values are replaced with placeholders where required.

The test should be interpreted as evidence for the specific bounded-authority property documented here. It is not presented as a general-purpose authorization, persistence, or storage implementation.
