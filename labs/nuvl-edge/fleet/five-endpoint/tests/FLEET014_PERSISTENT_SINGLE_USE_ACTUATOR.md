# FLEET-014 — Persistent Single-Use Authority Coupled to Actuator

**Date:** 2026-08-21  
**Status:** PASS  
**Classification:** Category 2 — optional capability / integration test  
**Architecture change:** No

## Purpose

FLEET-014 coupled the previously demonstrated persistent single-use authority mechanism to a physical actuator command path.

The test asked whether one provider-signed, single-use authority could:

1. produce an actuator command on its first admissible spend;
2. be denied when the same authority was presented again;
3. remain denied after restart of the persistent enforcement boundary; and
4. prevent additional actuator commands on the denied replay paths.

An independent ESP32 PWM witness was used to observe the actuator control signal.

The witness was observational only and was not part of the authority or enforcement path.

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

The physical effector was:

```text
esp32-xiao-servo-01
```

Qualified autonomous XIAO baseline SHA-256:

```text
B34E5A910E8ED91D6E303A1532CC7D8D6DFB72D614767AF7DD93C40732375048
```

A controlled FLEET-014 endpoint derivative was used so the exact same bounded request could be replayed.

Test derivative:

```text
esp32-xiao-servo-01_main_fleet014_fixed_nonce.py
```

Tested SHA-256:

```text
658D2B02628BC8B06F32BB79C5227719EAFBE1B8A3C00615948720C7333F785F
```

Intentional changes from the qualified baseline were limited to:

```text
NUVL test port:
8089 -> isolated FLEET-014 port

nonce generation:
dynamic nonce -> FLEET014-SINGLE-USE-REPLAY-01
```

The actuator gating logic was unchanged.

FLEET-014 used isolated persistent state and a cached authority package so existing persistence evidence and normal fleet state were not repurposed for the test.

## Test Sequence

### Phase 1 — Fresh Single-Use Authority

One provider-signed single-use authority was obtained for the controlled request.

Artifact identifier:

```text
c0a45bcf966a2939d152b171
```

The first presentation produced:

```text
decision=accepted
reason=offline_artifact_admissible
elapsed_ms=119
spent_count=1
replay_state_persisted_before_accept=True
```

The persistent state was therefore committed before the accepted result was returned.

### Independent Actuator-Command Observation

The independent PWM witness observed one command burst corresponding to the accepted transaction.

Accepted result timestamp:

```text
2026-08-21T21:26:47.827569298-04:00
```

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
```

Approximate accepted-result-to-witnessed-command delay:

```text
183 ms
```

Result:

**PASS**

The first admissible spend produced one independently observed actuator-command burst.

## Phase 2 — Same-Authority Replay Before Restart

The same authority and identical bounded request were presented repeatedly.

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

No new authority was issued for these attempts.

The independent witness remained IDLE after the single accepted burst.

Observed additional PWM bursts:

```text
0
```

Result:

**PASS**

Reuse of the consumed authority was denied and produced no independently observed actuator command.

## Phase 3 — Persistent Boundary Restart

Before restart, the persistent evidence hashes were recorded.

Spent-state SHA-256:

```text
cb672486bd8bebf8c982fb4e259201fc61e28f69b080d49ccfd139107741eac3
```

Cached authority-package SHA-256:

```text
a91fef96d60aae0f2fbe305e85d2197913423aeca374e00b3b1af490d80192cf
```

The persistent enforcement process was stopped and restarted.

On restart it reported:

```text
Persistent replay entries loaded: 1
Authority package loaded: True
Artifact ID loaded: c0a45bcf966a2939d152b171
```

The recovered replay state was loaded before the boundary resumed serving requests.

## Phase 4 — Same-Authority Replay After Restart

The same authority was then presented again.

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

- boundary shutdown;
- boundary restart;
- persistent-state recovery; and
- all seven observed post-restart replay attempts.

Observed PWM bursts during post-restart replay:

```text
0
```

Result:

**PASS**

The consumed single-use authority remained consumed across process restart.

## Persistence Verification

Final spent-state SHA-256:

```text
cb672486bd8bebf8c982fb4e259201fc61e28f69b080d49ccfd139107741eac3
```

Final cached authority-package SHA-256:

```text
a91fef96d60aae0f2fbe305e85d2197913423aeca374e00b3b1af490d80192cf
```

Both hashes were unchanged from their pre-restart values.

This confirmed that the tested persisted authority state survived the process restart without reopening the consumed authority.

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

During preparation, a board initially believed to be the actuator endpoint was later identified as `esp32-field-01`.

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

The anomaly is retained in the test record rather than omitted.

## Result

**FLEET-014: PASS**

Observed sequence:

```text
fresh single-use authority
        |
        v
ACCEPT
        |
        +--> persistent spent state committed
        |
        +--> one independently witnessed PWM command burst

same authority
        |
        v
DENY / replay_detected
        |
        +--> zero additional witnessed PWM bursts

persistent boundary restart
        |
        v
spent state recovered
        |
        v
same authority
        |
        v
DENY / replay_detected
        |
        +--> zero witnessed PWM bursts
```

## Supported Claim

> A provider-signed single-use authority produced an independently witnessed actuator command on its first admissible spend. Reuse of that same authority was denied without an observed actuator command, and that replay denial survived restart of the persistent enforcement boundary.

## Not Established

FLEET-014 does **not** establish:

- exactly-once mechanical execution;
- mechanical position or motion verification;
- general exactly-once electrical execution;
- crash-safe physical execution;
- arbitrary actuator behavior;
- distributed consensus; or
- general exactly-once actuator semantics.

The independent witness measured the electrical PWM command presented to the actuator control line.

It did not independently measure mechanical servo movement.

## Publication Boundary

The public repository may contain:

- this test description;
- the sanitized endpoint test derivative;
- curated result evidence;
- independent witness evidence; and
- publication-copy SHA-256 values.

Persistent enforcement-boundary implementation source is retained separately and is not required for publication of this test result.

Generated persistent state and the real signed authority package are also retained as private test evidence rather than published as runtime artifacts.

If any source or evidence file is sanitized for publication, the sanitized derivative must receive a new SHA-256. Original tested-source hashes must not be attached to modified publication copies.
