# FLEET-015 — Independent Actuator-Command Witness

## Status

PASS

Test date:

```text
2026-08-19 / 2026-08-20
```

## Classification

Category 2 — optional capability / evidence integration.

FLEET-015 does not change the NUVL authority path.

The added witness is observational only. It does not participate in authorization, validation, denial, actuator control, or provider communication.

## Module / Use Case

Independent physical-effect command observation.

The test evaluates whether a physically separate observer can distinguish actuator-command activity associated with:

- provider-admissible ACCEPT
- explicit DENY
- provider/boundary UNAVAILABLE

without becoming part of the execution path.

## New Claim Supported by This Test

Within the tested intervals, a physically separate observer detected servo-control PWM following accepted provider-controlled decisions, while denied and unavailable outcomes produced no independently observed actuator-command bursts.

## Claims Not Supported

FLEET-015 does not establish:

- independent mechanical-motion measurement
- calibrated servo angle or travel
- exactly-once physical execution
- exactly-once electrical command issuance as a general property
- actuator success after every PWM command
- persistent single-use authority coupled to physical execution
- crash consistency around physical execution
- safety certification
- arbitrary actuator or endpoint behavior

The witness observes the electrical actuator-control signal. It is not a mechanical position or motion sensor.

## Test Topology

The actuator under observation was:

```text
device_id=esp32-xiao-servo-01
```

The independent witness used the DevKit normally identified as:

```text
device_id=esp32-s3-03
```

During FLEET-015, that DevKit was temporarily used as an observer rather than as an autonomous fleet participant.

Its normal `main.py` was not replaced.

The witness program was executed temporarily through `mpremote run`.

The FLEET-015 topology therefore should not be interpreted as a five-autonomous-endpoint runtime test. It is an actuator instrumentation test using separate physical hardware.

## Witness Wiring

The witness was connected in parallel with the servo-control line.

Observed connection:

```text
XIAO servo signal: GPIO5 / D4
Witness input:     GPIO5
Ground:            shared
Servo power:       unchanged
```

The witness received its own USB power.

The witness did not provide actuator power.

It was not connected inline between the actuator endpoint and the servo.

It had no ability to authorize, deny, enlarge, originate, or execute provider authority.

Conceptually:

```text
Provider / NUVL authority path
          |
          v
esp32-xiao-servo-01
          |
          +------ servo signal ------> servo
          |
          +------ signal tee --------> independent GPIO witness
```

## Witness Method

The witness monitored the servo PWM signal using MicroPython `time_pulse_us()`.

Expected servo-control frequency:

```text
50 Hz
```

The witness reported:

```text
WITNESS_BURST_START
WITNESS_BURST_END
WITNESS_HEARTBEAT
```

A command burst was characterized primarily by:

- repeated PWM pulses
- approximately 50 pulses per actuation
- approximately 978–980 ms observed burst duration

Pulse-width extrema were retained as observed and were not used as a calibrated mechanical-position measurement.

## Source Versions

### Normal XIAO Servo Firmware

Pre-test and restored firmware:

```text
FLEET006_xiao_autonomous_async_archer.py
SHA-256:
B34E5A910E8ED91D6E303A1532CC7D8D6DFB72D614767AF7DD93C40732375048
```

A copy retrieved before the DENY modification produced the same hash.

After the DENY phase, the original firmware was restored and again produced the same hash.

### FLEET-015 DENY Firmware

The DENY test version changed only:

```text
mode = "accept"
```

to:

```text
mode = "deny"
```

Confirmed test-source SHA-256:

```text
77D5959F83BC9DC1BB207821D415A4368D5D16E510BF66B40CA2CC316364A644
```

The exact local firmware may contain environment-specific configuration and should not be published without sanitization.

Any sanitized publication derivative must receive a new SHA-256.

### Witness DevKit Baseline

The DevKit used as the witness retained its existing autonomous `main.py`.

Confirmed baseline hash:

```text
BE3103D0958AAB49EF325982C02A43CCD702544764526448B9CD77C8F684D954
```

The witness code was run temporarily and did not overwrite that file.

## Test Conditions

FLEET-015 exercised three authorization/result conditions:

```text
ACCEPT
DENY
UNAVAILABLE
```

The independent electrical observer was active during each retained synchronized interval.

## ACCEPT Condition

### Purpose

Verify that provider-admissible actuator transactions are associated with independently observed servo-control PWM.

### Retained Correlated Evidence

Coordinator:

```text
FLEET015_SYNC_ACCEPT_COORDINATOR_V2.log
```

Witness:

```text
FLEET015_SYNC_ACCEPT_WITNESS_CORRELATED_V2.log
```

The retained witness interval ran approximately:

```text
2026-08-20T00:24:32.501-04:00
through
2026-08-20T00:26:47.956-04:00
```

Within that interval:

```text
accepted provider_admissible results: 14
independently observed PWM bursts:     14
```

The observed association was one-for-one within the retained interval.

Representative coordinator events included:

```text
00:24:37.970 accepted
00:24:47.471 accepted
00:24:56.818 accepted
...
00:26:32.026 accepted
00:26:41.831 accepted
```

Corresponding witness burst starts occurred approximately 0.46–0.49 seconds later.

Each retained command burst contained approximately:

```text
50 pulses
978–980 ms duration
```

### ACCEPT Result

PASS.

Observed:

```text
14 accepted decisions
14 independent actuator-command bursts
```

No general exactly-once claim is made from this finite interval.

## DENY Condition

### Purpose

Verify that explicitly denied actuator requests do not produce independently observed servo-control PWM.

The XIAO test firmware requested:

```text
mode=deny
```

The coordinator returned:

```text
decision=denied
reason=unauthorized_request
```

### Retained Correlated Evidence

Coordinator:

```text
FLEET015_SYNC_DENY_COORDINATOR.log
```

Witness:

```text
FLEET015_SYNC_DENY_WITNESS_CORRELATED.log
```

During the directly overlapping retained interval:

```text
denied / unauthorized results: 4
observed PWM bursts:            0
```

The witness continued to emit:

```text
state=IDLE
```

heartbeats during the correlated denied interval.

### DENY Result

PASS.

Observed:

```text
DENY -> no independently witnessed actuator-command burst
```

## UNAVAILABLE Condition

### Purpose

Verify that provider/boundary unavailability does not produce an actuator-control PWM burst and that command activity returns after the authority path is restored.

### Controlled Fault

Boundary process before fault:

```text
PID 1942
```

Controlled stop marker:

```text
2026-08-20T01:12:12.826175944-04:00
FLEET015_CONTROLLED_BOUNDARY_STOP pid=1942
```

Restore marker:

```text
2026-08-20T01:13:47.845095312-04:00
FLEET015_CONTROLLED_BOUNDARY_RESTORE
```

The restored boundary subsequently ran under a new PID.

### Important Transition Detail

A PWM burst began immediately before the controlled boundary stop:

```text
burst start:
2026-08-20T01:12:12.1784400-04:00

boundary stop:
2026-08-20T01:12:12.826175944-04:00

burst end:
2026-08-20T01:12:13.3375257-04:00
```

That burst was already in progress when the fault was injected.

It is therefore classified as a pre-fault accepted execution and is excluded from the unavailable no-command interval.

### Unavailable Results

The first retained unavailable result occurred at:

```text
2026-08-20T01:12:20.097788003-04:00
```

The final retained unavailable result occurred at:

```text
2026-08-20T01:13:45.357045200-04:00
```

Observed outage results:

```text
11 / 11 unavailable
reason=OSError(104,)
elapsed_ms=12 for all 11
```

No accepted result was observed in that retained unavailable sequence.

### Independent Witness During Outage

After the pre-fault burst ended at approximately:

```text
01:12:13.337
```

the independent witness remained IDLE through the controlled outage.

Observed:

```text
unavailable results: 11
new PWM bursts during unavailable interval: 0
```

Witness heartbeats continued at approximately five-second intervals throughout the outage.

### Restoration

Boundary restoration marker:

```text
01:13:47.845
```

First restored provider-admissible result:

```text
01:13:54.965
decision=accepted
reason=provider_admissible
elapsed_ms=32
```

First post-recovery witness burst:

```text
01:13:55.525
```

Approximate difference:

```text
560 ms
```

Additional restored accepted results were followed by additional observed command bursts.

### UNAVAILABLE Result

PASS.

Observed:

```text
UNAVAILABLE -> no independently witnessed actuator-command burst
RESTORED ACCEPT -> actuator-command bursts returned
```

## Combined Result

FLEET-015 passed all three tested conditions.

```text
ACCEPT      -> PWM command independently witnessed
DENY        -> no PWM command independently witnessed
UNAVAILABLE -> no PWM command independently witnessed
RECOVERY    -> PWM command observation resumed after accepted results returned
```

## Supported Interpretation

The test strengthens the actuator evidence by separating authorization/result reporting from actuator-command observation.

The actuator endpoint remained responsible for execution.

The witness was physically separate and observational only.

Within the tested intervals:

> A physically separate observer detected actuator-control PWM following accepted provider-controlled decisions, while denied and provider-unavailable outcomes produced no independently observed actuator-command bursts.

This is stronger than relying only on software-reported actuator fields because the observed PWM signal was measured by separate hardware.

## Limitations

The witness measures electrical command activity only.

It does not prove that:

- the servo physically moved every time
- the servo reached an intended position
- the actuator experienced expected force or load
- mechanical execution occurred exactly once
- a command could not be duplicated outside the retained intervals
- physical execution survived a crash or power interruption
- persistent single-use authority was coupled to this actuator path

Visual observation of servo movement during accepted operation is supplemental operator observation and is not treated as an independent mechanical witness.

## External Network Interruption

An uncontrolled household/network interruption occurred between retained FLEET-015 phases.

That interruption stopped the Raspberry Pi services and was not used as controlled test evidence.

The boundary and coordinator were restarted, fresh accepted traffic was confirmed, and the controlled UNAVAILABLE phase was then executed separately.

The uncontrolled interruption is excluded from the FLEET-015 PASS determination.

## Evidence Files

Primary retained evidence:

```text
FLEET015_SYNC_ACCEPT_COORDINATOR_V2.log
FLEET015_SYNC_ACCEPT_WITNESS_CORRELATED_V2.log
FLEET015_SYNC_DENY_COORDINATOR.log
FLEET015_SYNC_DENY_WITNESS_CORRELATED.log
FLEET015_SYNC_UNAVAILABLE_COORDINATOR_FINAL.log
FLEET015_SYNC_UNAVAILABLE_WITNESS_FINAL.log
FLEET015_UNAVAILABLE_STOP_MARKER.txt
FLEET015_UNAVAILABLE_RESTORE_MARKER.txt
```

Witness source:

```text
FLEET015_witness_gpio5.py
```

Additional exploratory or superseded captures may be retained privately but are not required to establish the documented PASS result.

## Known Evidence Hashes

```text
FLEET015_SYNC_ACCEPT_COORDINATOR_V2.log
b16cf1e0abde56c28b7287a2f7adde207df524481e398389a42fa8b09b18cbd3

FLEET015_SYNC_ACCEPT_WITNESS_CORRELATED_V2.log
772047A060A56BE5CEB0FA889D96896EB3F047A1BBA7F2CB77FD613A77AA7524

FLEET015_SYNC_DENY_COORDINATOR.log
364526188f994a726cf81836b2181d22da2d9d1395c181461c01430624cd69ff

FLEET015_SYNC_DENY_WITNESS_CORRELATED.log
28F88E0BAA7F30B9C8224455C75A2549C7CD43523215302C75475E959A543015
```

Hashes for the final UNAVAILABLE files and witness source must be added to `evidence/SHA256SUMS.txt` after the exact publication copies are finalized.

## PASS Criteria

FLEET-015 passes if all of the following are observed:

1. ACCEPT transactions produce independently observed actuator-command PWM.
2. DENY transactions produce no independently observed actuator-command PWM.
3. UNAVAILABLE transactions produce no independently observed actuator-command PWM.
4. Accepted operation and witnessed actuator-command activity resume after boundary restoration.
5. The witness remains outside the authority and execution path.
6. No claim stronger than the witness measurement supports is made.

Observed result:

```text
PASS
```
