# FLEET-014 — Persistent Single-Use Authority Coupled to Actuator

**Date:** 2026-08-21  
**Status:** PASS  
**Classification:** Category 2 — optional capability / integration test  
**Architecture change:** No

## Purpose

FLEET-014 coupled the previously demonstrated persistent single-use authority mechanism to a physical actuator command path.

The test evaluated whether one provider-issued, single-use authority could:

1. produce an actuator command on its first admissible spend;
2. be denied when the same authority was presented again;
3. remain denied after restart of the persistent enforcement boundary; and
4. prevent additional actuator commands on the denied replay paths.

An independent ESP32 PWM witness observed the actuator control signal.

The witness was observational only and was not part of the authority, decision, or enforcement path.

## Module / Use Case

Persistent bounded authority applied to a physical effector.

The tested path was:

```text
provider-issued single-use authority
        |
        v
persistent enforcement boundary
        |
        v
endpoint decision
        |
        +-- accepted --> actuator command
        |
        +-- denied ----> no actuator command
```

The actuator endpoint retained the previously tested execution invariant:

> Physical execution occurs only after an accepted decision.

## Test Configuration

Physical effector:

```text
esp32-xiao-servo-01
```

Qualified autonomous XIAO baseline SHA-256:

```text
B34E5A910E8ED91D6E303A1532CC7D8D6DFB72D614767AF7DD93C40732375048
```

A controlled FLEET-014 endpoint derivative was used so the same bounded request could be presented repeatedly.

Test derivative:

```text
esp32-xiao-servo-01_main_fleet014_fixed_nonce.py
```

Tested SHA-256:

```text
658D2B02628BC8B06F32BB79C5227719EAFBE1B8A3C00615948720C7333F785F
```

Intentional changes from the qualified autonomous baseline were limited to the isolated test path and controlled nonce required for the replay test.

```text
NUVL port:
8089 -> 18089

nonce:
dynamic -> FLEET014-SINGLE-USE-REPLAY-01
```

The actuator gating logic was unchanged.

The servo command remained reachable only from the accepted decision branch.

FLEET-014 used isolated persistent state and a cached authority package so normal fleet replay state was not reused for the test.

## Provider-Issued Authority

One provider-signed single-use authority was issued for:

```text
device=esp32-xiao-servo-01
context=field_led_demo
action=accept
```

Artifact identifier:

```text
c0a45bcf966a2939d152b171
```

Provider issuance timestamp:

```text
2026-08-21T21:26:47.9340282-04:00
```

Artifact expiry:

```text
1787365607
```

The provider issuance was recorded by the retained provider log.

## Phase 1 — First Admissible Spend

The first presentation of the single-use authority produced:

```text
decision=accepted
reason=offline_artifact_admissible
elapsed_ms=119
spent_count=1
replay_state_persisted_before_accept=True
```

The persistent replay state was committed before the accepted result was returned.

Result:

**PASS**

The fresh single-use authority was admitted once and recorded as consumed.

## Independent Actuator-Command Observation

The independent GPIO5 PWM witness was active before the transaction and continuously reported an IDLE control line.

Immediately following the first admissible spend, the witness observed one PWM command burst.

Witness burst start:

```text
2026-08-21T21:26:48.0101278-04:00
```

Witness burst end:

```text
2026-08-21T21:26:49.1788853-04:00
```

Observed command:

```text
pulses=50
duration_ms=979
pulse_min_us=802
pulse_max_us=2001
```

The witness then returned to continuous IDLE observations.

Observed command bursts associated with the first admissible spend:

```text
1
```

Result:

**PASS**

The first admissible spend was accompanied by one independently observed actuator-command burst.

## Phase 2 — Same-Authority Replay Before Restart

The same authority and identical bounded request were then presented repeatedly.

Observed replay results:

```text
21:26:56.191  denied / replay_detected
21:27:04.643  denied / replay_detected
21:27:12.819  denied / replay_detected
21:27:21.625  denied / replay_detected
```

Summary:

```text
4 / 4 denied
reason=replay_detected
spent_count=1
```

No new authority was issued for these replay attempts.

The independent PWM witness remained IDLE after the single initial command burst.

Additional witnessed PWM bursts:

```text
0
```

Result:

**PASS**

Reuse of the consumed authority was denied and produced no additional independently observed actuator command.

## Phase 3 — Persistent Boundary Restart

The persistent enforcement process was stopped and restarted.

On restart, the boundary recovered the previously persisted replay state and cached authority information.

Observed recovery:

```text
Persistent replay entries loaded: 1
Authority package loaded: True
Artifact ID loaded: c0a45bcf966a2939d152b171
```

The consumed authority therefore remained represented in persistent state before the boundary resumed serving requests.

Result:

**PASS**

The persistent replay record survived process restart.

## Phase 4 — Same-Authority Replay After Restart

The same consumed authority was presented again after recovery.

Observed results:

```text
21:29:29.609  denied / replay_detected
21:29:38.388  denied / replay_detected
21:29:47.104  denied / replay_detected
21:29:55.338  denied / replay_detected
21:30:03.470  denied / replay_detected
21:30:12.086  denied / replay_detected
21:30:20.563  denied / replay_detected
```

Summary:

```text
7 / 7 denied
reason=replay_detected
spent_count=1
```

The independent PWM witness remained IDLE across:

- the pre-restart replay attempts;
- boundary shutdown;
- boundary restart;
- persistent-state recovery; and
- all seven observed post-restart replay attempts.

Additional witnessed PWM bursts after the original accepted transaction:

```text
0
```

Result:

**PASS**

The consumed single-use authority remained consumed across process restart and did not produce another actuator command.

## Witness Summary

The retained witness record shows:

```text
before first spend:       IDLE
first admissible spend:   one PWM burst
observed burst:           50 pulses / 979 ms
pre-restart replays:      IDLE
boundary restart period:  IDLE
post-restart replays:     IDLE
```

The witness firmware identified itself as:

```text
FLEET015_WITNESS_READY
```

This is expected.

FLEET-014 reused the previously established independent GPIO5 PWM witness implementation rather than creating a separate FLEET-014-specific observer.

The witness remained outside the authority and enforcement path.

## Persistence Verification

The persistent spent-state document and cached authority package were retained as test evidence.

The replay state continued to report:

```text
spent_count=1
```

before and after boundary restart.

The same artifact identifier remained associated with the recovered authority package:

```text
c0a45bcf966a2939d152b171
```

Their exact retained-file SHA-256 values are tracked in the repository evidence ledger rather than duplicated here.

## Restoration

After FLEET-014, `esp32-xiao-servo-01` was restored to the qualified autonomous fleet firmware.

Restored SHA-256:

```text
B34E5A910E8ED91D6E303A1532CC7D8D6DFB72D614767AF7DD93C40732375048
```

Post-restoration observation:

```text
5 / 5 transactions accepted
reason=provider_admissible
latency=31–33 ms
```

Normal endpoint operation was therefore restored.

## Setup Anomaly

During preparation, a board initially believed to be the actuator endpoint was later identified as:

```text
esp32-field-01
```

The FLEET-014 endpoint derivative was temporarily written to that board.

This occurred before the FLEET-014 enforcement bridge was started.

Therefore:

- no FLEET-014 authority had been issued;
- no FLEET-014 authority had been spent; and
- no FLEET-014 test transaction occurred on that board.

The endpoint was restored before test execution.

Restored `esp32-field-01` SHA-256:

```text
BE3103D0958AAB49EF325982C02A43CCD702544764526448B9CD77C8F684D954
```

The preparation anomaly is retained in the test record rather than omitted.

## Result

**FLEET-014: PASS**

Observed sequence:

```text
provider-issued single-use authority
        |
        v
first presentation
        |
        v
ACCEPT
        |
        +--> spent state persisted
        |
        +--> spent_count=1
        |
        +--> one independently witnessed PWM command burst

same authority
        |
        v
4 pre-restart attempts
        |
        v
DENY / replay_detected
        |
        +--> zero additional PWM bursts

persistent boundary restart
        |
        v
spent state recovered
        |
        v
same authority
        |
        v
7 post-restart attempts
        |
        v
DENY / replay_detected
        |
        +--> zero additional PWM bursts
```

Final observed totals:

```text
initial admissible spends:     1
accepted:                      1
pre-restart replay denials:    4
post-restart replay denials:   7
total replay denials:          11
witnessed PWM command bursts:  1
additional PWM bursts:         0
persistent spent_count:        1
```

## Supported Claim

> A provider-issued single-use authority produced one independently witnessed actuator command on its first admissible spend. Reuse of that same authority was denied without an additional observed actuator command, and the replay denial remained effective after restart of the persistent enforcement boundary.

## What This Test Establishes

For the tested configuration, FLEET-014 demonstrates the coupling of:

```text
provider-bounded authority
        +
single-use enforcement
        +
persistent replay state
        +
physical actuator-command gating
```

The test shows that consuming the authority once did not enlarge it into reusable execution authority.

Persistent replay enforcement continued to prevent reuse after boundary restart.

The independent witness also establishes that the replay-denied paths did not present additional PWM commands on the observed actuator control line.

## Not Established

FLEET-014 does **not** establish:

- exactly-once mechanical execution;
- mechanical position or movement verification;
- universal exactly-once electrical execution;
- crash-safe physical execution;
- arbitrary actuator behavior;
- distributed consensus;
- multi-boundary coordination; or
- general exactly-once actuator semantics.

The independent witness measured the electrical PWM command presented to the actuator control line.

It did not independently measure mechanical servo movement.

Crash behavior around durable consumption and physical execution is evaluated separately.

## Evidence

Retained FLEET-014 evidence includes:

- the endpoint test derivative;
- provider issuance log;
- independent witness log;
- final witness log;
- generated single-use authority package;
- generated persistent spent-state document; and
- repository SHA-256 evidence entries.

The enforcement-side FLEET-014 bridge implementation is retained separately from the public repository.

## Publication Boundary

The public repository may contain:

- this test description;
- the endpoint test derivative;
- provider issuance evidence;
- independent witness evidence;
- the generated authority package;
- the generated spent-state document; and
- SHA-256 values for the retained evidence.

The persistent enforcement-boundary / bridge implementation source is retained separately and is not required for publication of this result.

Actual credentials, passwords, or private key material must not be committed to the public repository.

Test artifact identifiers, non-secret test state, timestamps, local test addressing, and other evidentiary metadata do not require removal merely because they describe the test environment.
