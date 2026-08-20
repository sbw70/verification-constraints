# FLEET-009 — Shared Boundary Outage and Recovery

## Classification

**Category 1 — NUVL core / no architecture change**

FLEET-009 exercises the existing five-endpoint NUVL authority path under deliberate shared-boundary unavailability and subsequent restoration.

No endpoint firmware, authority model, coordinator behavior, or authorization rule was changed for this test.

## Module / Use Case

Five-endpoint autonomous fleet.

Shared authority-path failure, fail-closed behavior, and recovery without endpoint reset.

## Objective

Determine whether all five autonomous fleet participants:

- fail closed when the shared NUVL boundary becomes unavailable;
- avoid fallback acceptance while that boundary is unavailable;
- continue generating independent transactions during the outage;
- preserve endpoint identity and transaction uniqueness;
- recover expected authorization behavior after the boundary is restored; and
- recover without resetting or reflashing any endpoint.

## Fleet

The tested fleet consisted of:

- `esp32-field-01`
- `esp32-s3-02`
- `esp32-s3-03`
- `esp32-xiao-servo-01`
- `esp32-xiao-servo-02`

Shared infrastructure included:

- Raspberry Pi 5 boundary/coordinator;
- Archer network;
- autonomous endpoint-local request schedules; and
- the existing provider-controlled authority path.

The tested path remained:

```text
endpoint
  ->
network
  ->
NUVL boundary
  ->
provider-controlled decision
  ->
endpoint action
```

## Fault Injection

The running boundary process was identified before fault injection as:

```text
python3 -u nuvl_local_hardened_latency.py
```

The boundary process was then stopped.

The coordinator remained running so endpoint behavior could continue to be recorded during the outage.

No endpoint was reset, reflashed, or removed from autonomous operation.

The boundary was later restored using the same boundary program.

## Test Phases

The retained coordinator evidence contains three behaviorally observed phases.

### Pre-Outage

Observed line range:

```text
77261-77288
```

The final pre-outage accepted transaction occurred at:

```text
77288
```

### Outage

The first observed unavailable result occurred at:

```text
77289
```

The final observed unavailable result occurred at:

```text
77595
```

### Recovery

The first recovered accepted result occurred at:

```text
77596
```

The recovery observation continued through:

```text
77785
```

These behavioral boundaries are preserved separately from the operator-action timestamp markers.

## Operator Markers

Measured test start:

```text
2026-08-19T21:33:12.973544575-04:00
```

Recorded start line:

```text
77260
```

Boundary absence confirmed:

```text
2026-08-19T21:34:03.834042133-04:00
```

Recorded outage marker line:

```text
77312
```

Outage observation end marker:

```text
2026-08-19T21:37:29.828477452-04:00
```

Recorded line:

```text
77531
```

Boundary restoration initiated:

```text
2026-08-19T21:38:29.210487942-04:00
```

Recorded restore marker line:

```text
77594
```

Recovery observation end:

```text
2026-08-19T21:41:34.852957606-04:00
```

Recorded line:

```text
77785
```

## Results

### Dataset Summary

```text
parsed_transactions=525
unique_run_ids=525
duplicate_run_ids=0
```

## Pre-Outage Phase

```text
transactions=28
accepted=28
unavailable=0
other=0
```

All 28 transactions produced:

```text
decision=accepted
reason=provider_admissible
```

Per-endpoint participation:

```text
esp32-field-01         11 accepted
esp32-s3-02             7 accepted
esp32-s3-03             5 accepted
esp32-xiao-servo-01     3 accepted
esp32-xiao-servo-02     2 accepted
```

Latency:

```text
minimum=30 ms
mean=35.93 ms
median=34.0 ms
maximum=65 ms

over_250_ms=0
over_1000_ms=0
over_3000_ms=0
```

## Outage Phase

```text
transactions=307
accepted=0
unavailable=307
other=0
```

All 307 transactions produced:

```text
decision=unavailable
reason=OSError(104,)
```

Per-endpoint participation:

```text
esp32-field-01        114 unavailable
esp32-s3-02            82 unavailable
esp32-s3-03            51 unavailable
esp32-xiao-servo-01    34 unavailable
esp32-xiao-servo-02    26 unavailable
```

All five autonomous endpoints continued generating transactions while the boundary was unavailable.

No accepted transaction was observed during the behavioral outage phase.

Latency:

```text
minimum=12 ms
mean=14.79 ms
median=13 ms
maximum=57 ms

over_250_ms=0
over_1000_ms=0
over_3000_ms=0
```

The observed failure mode was therefore fast unavailability rather than a long endpoint-side blocking loop.

## Recovery Phase

```text
transactions=190
accepted=190
unavailable=0
other=0
```

All 190 recovery-phase transactions produced:

```text
decision=accepted
reason=provider_admissible
```

Per-endpoint participation:

```text
esp32-field-01         71 accepted
esp32-s3-02            52 accepted
esp32-s3-03            34 accepted
esp32-xiao-servo-01    19 accepted
esp32-xiao-servo-02    14 accepted
```

Latency:

```text
minimum=30 ms
mean=38.45 ms
median=36.0 ms
maximum=90 ms

over_250_ms=0
over_1000_ms=0
over_3000_ms=0
```

All five endpoints returned to expected provider-admissible behavior.

No endpoint reset or reflash was performed.

## Recovery Transition

The restore marker was recorded at:

```text
77594
```

One final unavailable transaction was observed immediately afterward at:

```text
77595
```

The first recovered accepted transaction appeared at:

```text
77596
```

By line:

```text
77606
```

all five fleet participants had produced at least one recovered:

```text
accepted / provider_admissible
```

result.

The transition is retained explicitly rather than presenting restoration as instantaneous.

## Error / Failure Search

The frozen FLEET-009 evidence window was searched for:

```text
traceback
exception
timeout
failed
fail
```

No matches were found.

The expected outage indicators:

```text
decision=unavailable
reason=OSError(104,)
```

were excluded from that search because they were the intended fault response.

## Result

**PASS**

Observed three-phase behavior:

```text
PRE-OUTAGE
28 / 28 accepted

OUTAGE
307 / 307 unavailable

RECOVERY
190 / 190 accepted
```

Across all phases:

```text
525 total transactions
525 unique run IDs
0 duplicate run IDs
0 transactions over 250 ms
```

All five endpoints participated before, during, and after the outage.

No fallback acceptance appeared during the observed boundary outage.

Expected provider-admissible behavior returned after restoration without endpoint resets.

## Supported Claim

FLEET-009 supports the bounded laboratory statement:

> When the shared NUVL boundary became unavailable, all five autonomous fleet participants failed closed with no observed fallback acceptance, and normal provider-admissible operation resumed after boundary restoration without endpoint resets.

The test also supports the observation that autonomous request generation continued during boundary unavailability rather than stopping the endpoint execution loop in a long blocking state.

## Physical-Effector Boundary

Both physical-effector endpoints participated during all three phases.

During the outage they produced only:

```text
decision=unavailable
reason=OSError(104,)
```

During recovery they returned to:

```text
decision=accepted
reason=provider_admissible
```

The coordinator evidence establishes software-observed authorization behavior for those endpoints.

It is not an independent physical witness of every actuator movement.

FLEET-009 therefore does not establish exactly-once physical execution or independently witnessed physical non-execution for every unavailable transaction.

## What This Test Does Not Establish

FLEET-009 does not establish:

- arbitrary network-partition tolerance;
- every possible provider or boundary outage mode;
- arbitrary communications degradation behavior;
- tactical-network resilience;
- guaranteed recovery time;
- deterministic latency;
- arbitrary fleet scalability;
- arbitrary denial-of-service resistance;
- Byzantine fault tolerance;
- exactly-once physical execution;
- independent physical confirmation of every actuator outcome; or
- production operational qualification.

The result is limited to the documented five-endpoint laboratory configuration and the tested boundary-process outage.

## Evidence Files

Public evidence set:

```text
FLEET009_OUTAGE_START.txt
FLEET009_OUTAGE_APPLIED.txt
FLEET009_OUTAGE_OBSERVED_END.txt
FLEET009_RESTORE.txt
FLEET009_RECOVERY_END.txt
FLEET009_PHASE_BOUNDARIES.txt
FLEET009_RECOVERY_TRANSITION.txt
FLEET009_OUTAGE_RECOVERY_WINDOW.log
FLEET009_OUTAGE_RECOVERY_ANALYSIS.txt
fleet009_outage_recovery_analyze.py
```

## Publication SHA-256

### FLEET009_OUTAGE_START.txt

```text
028dd60eca8c89e84f5f7ff0cfdc069efdc9a2ecd3ed5254b452501d6a30d9bd
```

### FLEET009_OUTAGE_APPLIED.txt

```text
26d31603d3cc41cf8f1c90782a33128fe34aa13a8904a8eea424b0a0407bda13
```

### FLEET009_OUTAGE_OBSERVED_END.txt

```text
a29e92c1683761e15127a5c817927df2137e22fabad575618fb408d962e328b0
```

### FLEET009_RESTORE.txt

```text
587897fb973c2e8ef285757ab1bc91913217462df69a7a094a7816924f4cde0b
```

### FLEET009_RECOVERY_END.txt

```text
54d9349b5d3fa9041b1b8bde815b3f36af537da4bf4604a44e25c93cdc71d561
```

### FLEET009_PHASE_BOUNDARIES.txt

```text
83751ddd9949924334ebfb332713d0e99dcb6b9d8cc753a4c7c65db3a758df89
```

### FLEET009_RECOVERY_TRANSITION.txt

```text
e284c6b384a15b171e1c1587fe9578c56202da8eca979b96e5ba5ef32fd59f05
```

### FLEET009_OUTAGE_RECOVERY_WINDOW.log

```text
1f40f718e4f89b35b819d3ec8f42e4ecce9777dc9e3faeda17a42462c53c78fa
```

### FLEET009_OUTAGE_RECOVERY_ANALYSIS.txt

```text
d65fe0801e5b06f13fc20ea636f822054f2bb4f7b15b9c5b3e9e459293a387d0
```

### fleet009_outage_recovery_analyze.py

```text
08b212264ab4dd75f8c3979b75cccbc8dc6c6e6ede1c22ac240a248f1a036e77
```

## Original Artifact Provenance

Three Pi-side artifacts contained machine-specific `/home/seth/` paths and were sanitized for publication.

The original Pi-side hashes were:

```text
FLEET009_OUTAGE_START.txt
318f53f6b49794e79b49a3400c2acfba774db8e53453eac1943473cfcd1ad948

FLEET009_RESTORE.txt
e2893a8da0442ffc987ba4ea7516b8f433cc126f27c3022113a50a96acbd15ef

fleet009_outage_recovery_analyze.py
5c3b03fa777b5b2963455b3baa55bb91850c3e71922c9ebdda2f0e3eeeb27980
```

The corresponding publication copies differ only by removal of the machine-specific `/home/seth/` path.

The publication copies therefore receive separate SHA-256 values and do not reuse the hashes of the original Pi-side artifacts.

## Final Disposition

FLEET-009 is complete.

The shared boundary was deliberately removed while all five endpoints remained autonomous and active.

During the observed outage:

```text
307 / 307
```

transactions failed closed as unavailable.

After restoration:

```text
190 / 190
```

observed transactions returned to the expected provider-admissible result.

All five endpoints recovered without endpoint reset or reflash.

The restored boundary remained running at the conclusion of the test.
