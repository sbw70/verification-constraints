# FLEET-017 — Dual Physical Endpoint Single-Use Authority Race

## Status

PASS

## Classification

Category 1 — NUVL core, no architecture change.

FLEET-017 extends the disconnected single-use authority path from software-only concurrent contention to two independently connected physical actuator endpoints.

The test does not create a new authority source, delegate provider authority, or permit either endpoint or the enforcement boundary to enlarge the provider-established authority.

## Purpose

POC-005 established that two concurrent spend attempts against the same single-use authority produced one accepted result and one denied result.

FLEET-017 tests the same bounded-authority property across two separate physical actuator endpoints.

The question is:

> If two independently connected physical endpoints contend for the same provider-issued single-use authority, can concurrent physical request paths multiply that authority into more than one admitted execution path?

The required result is:

```text
one provider-issued authority
max_uses = 1

        +

two physical endpoint contenders

        ->

one accepted
one denied
```

The specific endpoint that wins the race is not predetermined.

The authority property is that the single-use constraint remains single-use under physical endpoint contention.

## Authority Property Under Test

The tested invariant is:

```text
provider establishes one bounded authority
        ->
authority permits one use
        ->
two independent physical endpoints contend
        ->
boundary serializes consumption
        ->
one contender consumes authority
        ->
competing contender observes authority as spent
        ->
one ACCEPT
one DENY
```

Concurrency, endpoint multiplicity, or physical separation must not enlarge the authority.

## Test Topology

```text
                    Provider
                       |
                       | establishes signed
                       | single-use authority
                       v
              Provider-signed artifact
                       |
                       v
              Raspberry Pi boundary
                       |
              persistent spent state
                       |
              +--------+--------+
              |                 |
              |                 |
              v                 v
     XIAO ESP32-S3       XIAO ESP32-S3
      servo endpoint      servo endpoint
           A                   B
              \               /
               \             /
                \           /
                 race coordinator
                       |
                  coordinated
                    release
```

Each XIAO endpoint is a separate physical requester and actuator-control endpoint.

Both contend for the same authority.

The race coordinator controls release timing but does not grant authority.

## Repository Structure

```text
fleet017-dual-physical-race/
├── README.md
├── fleet017_race_coordinator.py
├── fleet017_xiao_race_main.py
├── fleet017_prepare_race.py
├── fleet017_device_id_A.txt
├── fleet017_device_id_B.txt
├── evidence/
│   ├── FLEET017_RACE_RESULT.json
│   ├── FLEET017_BOUNDARY.log
│   ├── fleet017_spent_state.json
│   └── SHA256SUMS.txt
└── WITHHELD.md
```

## Repository Files

### `fleet017_race_coordinator.py`

Coordinates the two physical endpoint contenders and releases the race.

The coordinator is test orchestration only.

It does not:

- issue authority;
- verify provider signatures as an authority source;
- create replacement authority;
- alter `max_uses`;
- override the enforcement boundary.

Its purpose is to create a controlled concurrent spend condition and record the resulting endpoint outcomes.

### `fleet017_xiao_race_main.py`

XIAO ESP32-S3 endpoint firmware used for the physical race.

The same race-capable firmware is used by both physical endpoints, with endpoint identity supplied separately.

Physical actuator execution remains downstream of an accepted authority result.

A denied result does not enter the actuator-command path.

Publication copies must use sanitized network configuration.

### `fleet017_prepare_race.py`

Prepares the single provider-issued authority used by both physical contenders.

The resulting authority is common to both endpoints.

The test therefore does not compare two separately issued permissions.

It tests contention for one bounded authority.

Publication copies must use sanitized deployment addressing.

### `fleet017_device_id_A.txt`

Endpoint identity for physical contender A.

### `fleet017_device_id_B.txt`

Endpoint identity for physical contender B.

The separate identity files allow two physical endpoints to participate in the same race while remaining independently identifiable.

## Evidence

### `FLEET017_RACE_RESULT.json`

Machine-readable result record for the valid dual-physical race.

This artifact records the competing endpoint outcomes associated with the same single-use authority.

### `FLEET017_BOUNDARY.log`

Boundary-side execution evidence for the race.

This log provides the authority-path record needed to correlate the competing requests with their enforcement outcomes.

### `fleet017_spent_state.json`

Persistent spent-state evidence after the valid race.

The state record provides evidence that the common authority was recorded as consumed.

### `SHA256SUMS.txt`

SHA-256 manifest for the published FLEET-017 evidence set.

Hashes apply to the published files represented in this directory.

Modified or sanitized publication copies must receive their own hashes rather than inheriting hashes from nonidentical originals.

## Withheld Implementation

The persistent boundary implementation used for the test is not published in this directory.

The withheld implementation contains persistence-ordering and concurrency-control logic already treated as publication-sensitive within the disconnected-authority work.

Its exclusion does not change the externally observable test contract:

```text
same authority
+
two physical contenders
=
no more than one admitted use
```

See `WITHHELD.md` for the publication boundary.

Generated provider-signed authority artifacts are also excluded from the public repository.

## Test Procedure

### 1. Establish Two Physical Endpoints

Connect and power both XIAO ESP32-S3 servo endpoints independently.

Assign their endpoint identities using:

```text
fleet017_device_id_A.txt
fleet017_device_id_B.txt
```

Both endpoints must be reachable and armed for the race.

### 2. Prepare One Single-Use Authority

Run:

```text
fleet017_prepare_race.py
```

Prepare one provider-issued authority with a single permitted use.

The same authority must be supplied to both physical contenders.

The test is invalid if each endpoint receives independently issued authority.

### 3. Establish the Race

Start:

```text
fleet017_race_coordinator.py
```

Both endpoints are prepared to contend for the common authority.

The coordinator releases the requests in a coordinated race window.

### 4. Enforce the Common Authority

The boundary receives the competing spend attempts.

The authoritative check-and-consume path determines which contender first consumes the single-use authority.

The first successful contender may proceed through its accepted actuator-command path.

The competing contender must be denied because the authority is already consumed.

### 5. Preserve Evidence

Retain:

```text
FLEET017_RACE_RESULT.json
FLEET017_BOUNDARY.log
fleet017_spent_state.json
```

Generate or update:

```text
SHA256SUMS.txt
```

after the final publication copies are staged.

## PASS Criteria

FLEET-017 passes only if:

1. Two separate physical actuator endpoints participate.
2. Both endpoints contend for the same provider-issued authority.
3. That authority is limited to one use.
4. The requests overlap as a race rather than a deliberately sequential test.
5. Exactly one contender receives an accepted authority result.
6. Exactly one contender is denied as a competing reuse of the same authority.
7. The accepted path may reach its actuator-command path.
8. The denied path does not reach its actuator-command path.
9. Persistent spent state records the common authority as consumed.
10. No race outcome produces two accepted uses of the single-use authority.

The required aggregate authority result is:

```text
accepted = 1
denied   = 1
```

The following result is a failure:

```text
accepted = 2
```

## Valid Run

PASS.

In the valid FLEET-017 race:

```text
two physical endpoints
same single-use authority
one accepted
one replay-denied
```

One physical endpoint won the authority race and reached the admitted command path.

The competing physical endpoint was denied because the common authority had already been consumed.

No double acceptance was observed.

The persistent spent-state record reflected consumption of the shared authority.

## Invalid Preliminary Run

An earlier attempted race was preserved but is not counted as valid FLEET-017 evidence.

In that run, one servo endpoint was halted at the REPL and was not armed when the competing request executed.

The resulting requests were therefore sequential rather than genuinely concurrent.

That run does not satisfy the FLEET-017 PASS contract and is classified as:

```text
NOT VALID
```

Preserving the failed setup attempt is useful because it distinguishes a genuine dual-endpoint race from a superficially similar sequence of two requests.

The PASS claim is based only on the later valid concurrent run.

## Supported Claim

Within the tested implementation and conditions:

> Two independently connected physical actuator endpoints contended for the same provider-issued single-use authority. One endpoint was accepted and the competing endpoint was denied as reuse of consumed authority. Concurrent physical request paths did not enlarge the authority beyond its single permitted use.

The test supports the bounded-authority invariant:

```text
more requesters
must not mean
more authority
```

It also extends the POC-005 contention result from two software spend attempts to two independently connected physical endpoint paths.

## Physical Execution Boundary

FLEET-017 distinguishes authority admission from physical execution.

The relevant ordering is:

```text
request
        ->
authority decision
        ->
if ACCEPT:
    actuator-command path eligible

if DENY:
    no actuator-command path
```

The endpoint is not permitted to actuate merely because it participated in the race.

Physical command eligibility follows the accepted authority path.

## What This Test Does Not Prove

FLEET-017 does not establish:

- exactly-once mechanical motion;
- exactly-once distributed execution;
- arbitrary numbers of simultaneous physical contenders;
- distributed consensus across multiple independent enforcement boundaries;
- production-scale concurrency guarantees;
- absence of every possible network race;
- absence of every possible storage race;
- safety certification;
- real-time deterministic scheduling;
- operational weapons or C-UAS authorization;
- correctness outside the tested authority and endpoint configuration.

The test establishes one narrower property:

> Two physical endpoints contending for one single-use authority did not produce two admitted uses.

## Relationship to Earlier Tests

FLEET-017 extends the disconnected-authority progression:

```text
POC-003
single-use disconnected authority
one use accepted
replay denied

        ↓

POC-004 / POC-004B
consumption survives
restart and power loss

        ↓

POC-005
two software contenders
one accepted
one denied

        ↓

POC-006A / WP2
crash and persistence
boundaries exercised

        ↓

FLEET-014
persistent single-use authority
coupled to physical execution

        ↓

FLEET-015
independent observation of
actuator-command behavior

        ↓

FLEET-016
interruption around
physical execution path

        ↓

FLEET-017
two physical endpoints
same single-use authority
one admitted execution path
```

FLEET-017 therefore moves the concurrency property from software-only contention into a dual-physical-endpoint test.

## Publication Notes

The public repository contains the race coordinator, endpoint firmware, preparation client, endpoint identity files, and curated evidence needed to inspect the externally observable test behavior.

Environment-specific addresses and Wi-Fi configuration must be sanitized before publication.

The persistent boundary implementation remains withheld.

Generated provider-signed authority artifacts are not published.

The README should be interpreted as documentation of the tested authority property and evidence package, not as a claim of arbitrary distributed exactly-once execution.
