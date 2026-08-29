# POC-005 — Concurrent Double-Spend Resistance

## Status

PASS

## Classification

Category 1 — NUVL core, no architecture change.

POC-005 extends disconnected single-use authority enforcement by testing concurrent contention for the same provider-issued authority.

The test does not introduce a new authority source, delegate provider authority, or permit the enforcement boundary to originate or enlarge authority.

## Purpose

Earlier disconnected-authority tests established that:

- a provider-issued single-use authority could be consumed while disconnected;
- subsequent replay was denied;
- consumed authority remained consumed across process restart;
- consumed authority remained consumed across boundary-host power loss.

POC-005 tests a different failure mode:

> What happens when two requests attempt to consume the same single-use authority at effectively the same time?

Sequential replay protection alone is insufficient to establish this property.

If two contenders can independently observe an authority as unused before either records its consumption, both could be accepted.

The required result is therefore:

```text
same single-use authority
        ->
two concurrent spend attempts
        ->
exactly one accepted
        ->
exactly one denied
```

## Authority Property Under Test

The tested invariant is:

```text
one provider-issued authority
with
max_uses = 1

        +

two competing spend attempts

        ->

one successful consumption only
```

Concurrency must not enlarge the authority from one permitted use into two.

The enforcement boundary must serialize the authoritative check-and-consume operation so that once one contender consumes the authority, the competing contender observes it as spent.

## Test Topology

```text
Provider
   |
   | issues bounded single-use authority
   v
Provider-signed authority artifact
   |
   +----------------------+
   |                      |
   v                      v
Contender A          Contender B
   |                      |
   |      concurrent      |
   |       /spend         |
   +----------+-----------+
              |
              v
     Raspberry Pi boundary
              |
              +---- verifies authority
              +---- checks spent state
              +---- serializes consumption
              +---- commits first valid spend
              +---- detects competing reuse
              |
         +----+----+
         |         |
         v         v
      ACCEPT      DENY
                 replay_detected
```

The identities of the winning and losing contenders are not the authority property under test.

The required property is that only one contender can successfully consume the single-use authority.

## Repository Files

### `poc005_prepare_race.py`

Prepares the authority artifact used for the concurrent-spend test.

The prepared artifact represents one bounded authority with a single permitted use.

The same authority is supplied to both contenders.

### `poc005_concurrent_double_spend.py`

Executes the concurrent double-spend attempt.

The test coordinates two competing requests against the same single-use authority and records the outcome of each attempt.

The test evaluates the combined result rather than requiring a predetermined contender to win.

The valid outcome is:

```text
1 accepted
1 denied
```

The denied contender must be rejected because the single-use authority has already been consumed.

## Test Procedure

### 1. Prepare a Single-Use Authority

Run:

```text
poc005_prepare_race.py
```

Prepare one provider-issued authority artifact constrained to a single permitted use.

The same artifact is retained for both competing requests.

### 2. Establish the Race

Run:

```text
poc005_concurrent_double_spend.py
```

Two contenders submit spend attempts against the same authority with closely coordinated release timing.

Neither contender is assigned authority independently.

Both are attempting to consume the same bounded authority.

### 3. Observe Both Results

The two requests are allowed to contend at the enforcement boundary.

One request may acquire the authoritative consumption path first.

That request is expected to receive:

```text
decision=accepted
```

The competing request is expected to receive:

```text
decision=denied
reason=replay_detected
```

Which contender wins is not material to PASS.

The aggregate result is material.

## PASS Criteria

POC-005 passes only if:

1. One provider-issued single-use authority is prepared.
2. Both contenders use that same authority.
3. The spend attempts overlap as a concurrent contention test.
4. Exactly one request is accepted.
5. Exactly one request is denied.
6. The denied request is recognized as reuse of consumed authority.
7. No execution path produces two accepted spends.
8. Concurrency does not enlarge `max_uses = 1` into multiple permitted uses.

The required aggregate result is:

```text
accepted = 1
denied   = 1
```

The following result is a failure:

```text
accepted = 2
```

## Observed Result

PASS.

Two competing requests were released against the same single-use authority.

The measured release skew was approximately:

```text
96 microseconds
```

The resulting authority decisions were:

```text
accepted = 1
denied   = 1
```

One contender successfully consumed the authority.

The competing contender was denied.

No double acceptance was observed.

## Supported Claim

Within the tested implementation and conditions:

> Two concurrent attempts to consume the same provider-issued single-use authority produced one accepted spend and one denied spend; concurrent contention did not enlarge the authority beyond its permitted single use.

The test supports the bounded-authority invariant:

```text
concurrency
must not
increase available authority
```

The enforcement result remained bounded by the provider-established single-use constraint despite competing requests.

## Why This Matters

A single-use constraint is meaningful only if it remains single-use under contention.

A design that performs an uncoordinated sequence such as:

```text
check unused
        ->
perform work
        ->
record used
```

can permit multiple contenders to observe the same authority as available.

The required authority operation is instead conceptually:

```text
check
+
consume
+
commit
```

within a serialized authoritative operation.

POC-005 tests the externally observable result of that requirement.

## What This Test Does Not Prove

POC-005 does not establish:

- correctness under every possible concurrency level;
- behavior with large numbers of simultaneous contenders;
- distributed consensus across multiple independent enforcement boundaries;
- multi-use authority accounting;
- exactly-once physical execution;
- absence of every possible storage or filesystem race;
- correctness under interruption during the persistence operation;
- behavior after corruption or loss of persistent state;
- production-scale transaction throughput;
- real-time scheduling guarantees;
- safety certification.

The test establishes the result for the specific two-contender single-use race that was executed.

## Relationship to Other Tests

POC-005 extends the disconnected-authority sequence from replay persistence into concurrent contention.

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
two concurrent contenders
same single-use authority
one accepted
one denied
```

The progression tests the same bounded-authority property against increasingly different ways that consumed authority could otherwise be recreated or multiplied.

Later tests examine interruption around durable consumption and extend contention testing into independently observable physical actuator paths.

## Publication Notes

The repository files are publication copies of the test artifacts.

Environment-specific deployment values are replaced with placeholders where required.

The test should be interpreted as evidence for the specific concurrent single-use authority property documented here.

It does not establish arbitrary distributed exactly-once execution or general-purpose consensus.
