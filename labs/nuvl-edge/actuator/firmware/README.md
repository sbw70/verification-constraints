# Actuator Firmware

This directory contains the ESP32-S3 endpoint firmware used for the NUVL physical actuator integration.

The actuator firmware extends the existing NUVL endpoint behavior with a deliberately narrow physical execution gate:

```text
accepted / provider_admissible
        ↓
actuator permitted
        ↓
servo command
```

Non-accepted outcomes do not invoke the actuator.

The physical actuator capability does not give the endpoint independent authority to determine whether an action is admissible.

---

## File

### `esp32_xiao_servo_nuvl.py`

Publication copy of the firmware qualified during ACT-001 through ACT-005.

Original qualified source:

`esp32_xiao_servo_nuvl_archer.py`

Original tested size:

`9,790 bytes`

Original tested SHA-256:

`C29AD7BB8362BD532C62A87CE5D8BE3ED30C25E4543FF52A2CC98992E493AD84`

The same original firmware hash was verified on both qualified actuator endpoints:

* `esp32-xiao-servo-01`
* `esp32-xiao-servo-02`

The repository copy has been sanitized for publication.

Accordingly, the original qualification hash above identifies the original tested artifact and must not be represented as the hash of the sanitized repository copy unless the repository bytes independently produce the same hash.

---

# Architecture Role

The actuator firmware is an **optional capability integration**, not a change to the underlying NUVL authority architecture.

The endpoint gains a physical execution capability.

It does not gain additional authorization authority.

The tested relationship is:

```text
external NUVL decision
        ↓
endpoint receives result
        ↓
result evaluated
        ↓
accepted?
   ┌────┴────┐
   │         │
  yes        no
   │         │
actuator   no actuator
permitted   call
```

The actuator is therefore downstream of the NUVL decision.

Physical capability and authorization authority remain separate in the tested implementation.

---

# Qualified Hardware

The firmware was qualified on:

* Seeed XIAO ESP32-S3
* ESP32-S3 rev 0.2
* 8 MB flash
* 8 MB PSRAM
* MicroPython v1.28.0
* MG90S-class micro servo

Servo signal:

`D4 / GPIO5`

PWM frequency:

`50 Hz`

The qualified bench powered the servo from the XIAO 5V/VBUS path.

No brownout or endpoint reset was observed during the qualified actuator tests.

That bench configuration is not a general recommendation for higher-current or production actuators.

---

# Endpoint Identity

Both actuator endpoints run the same firmware.

Their logical identities are stored separately in:

`device_id.txt`

Qualified identities:

`esp32-xiao-servo-01`

`esp32-xiao-servo-02`

This allows identical firmware to be deployed while preserving distinct endpoint identities.

USB COM-port assignments and DHCP addresses are not used as durable endpoint identities.

---

# Actuator Gate

The firmware permits physical actuator invocation only from the accepted path.

Conceptually:

```python
if decision == "accepted":
    actuate()
```

Non-accepted paths do not call the actuator function.

Qualified non-actuation conditions included:

* `denied / unauthorized_request`
* `denied / stale_replay_malformed`
* authorization boundary unavailable

During the documented tests, these outcomes reported no actuator attempt and produced no observed physical movement.

---

# Actuator Telemetry

The firmware exposes three fields used by the test oracle:

`actuator_attempted`

`actuator_command_completed`

`actuator_error`

For an accepted result, the qualified expected state is:

```text
actuator_attempted=True
actuator_command_completed=True
actuator_error=None
```

For a non-accepted result:

```text
actuator_attempted=False
actuator_command_completed=False
actuator_error=None
```

These fields allow the coordinator-side test harness to distinguish the authorization result from the subsequent software execution state.

---

# Physical Evidence Boundary

`actuator_attempted=True`

means the firmware entered the actuator routine.

`actuator_command_completed=True`

means the software actuator routine completed without a reported error.

Neither field independently proves final mechanical position.

During qualification, physical servo movement was separately observed and selected runs were captured on video.

No independent encoder, position sensor, or electrical signal witness was used.

---

# Servo Control

The qualified implementation used hardware PWM on:

`GPIO5 / D4`

Frequency:

`50 Hz`

During hardware qualification, approximately:

* 1.0 ms
* 1.5 ms
* 2.0 ms

pulse positions produced distinguishable servo positions.

The actuator path used an approximately 2.0 ms command pulse.

PWM remained active for approximately one second and was then released.

The servo was therefore not continuously held under PWM following the command interval.

---

# Startup and Idle Behavior

Servo positioning performed during bench setup is out-of-band test preparation.

It is not part of the NUVL authorization path.

During normal actuator firmware operation, the physical effector is expected to remain untouched until an accepted result reaches the actuator gate.

This distinction is important when reproducing the tests:

**setup movement is not authorization-gated actuator evidence.**

Only physical movement following the documented accepted NUVL path was counted as test evidence.

---

# Network and Boundary Relationship

The firmware participates in the existing NUVL request path.

During the qualified actuator series, the path was:

```text
coordinator
    ↓
XIAO endpoint
    ↓
NUVL boundary
    ↓
returned decision
    ↓
XIAO actuator gate
    ↓
servo
```

The XIAO does not convert boundary failure into local permission to execute.

ACT-001 and ACT-005 demonstrated that when the external authorization boundary was unavailable, the tested endpoints returned unavailable outcomes and did not invoke their actuators.

---

# Recovery Behavior

The firmware was also exercised across external-boundary restoration.

During ACT-001:

```text
boundary unavailable
→ no actuation
→ boundary restored
→ accepted result
→ physical actuation
```

During ACT-005, the same behavior was demonstrated across both actuator endpoints.

Neither XIAO was reset during the ACT-005 outage-to-recovery transition.

This demonstrates recovery in the tested external-boundary restart path.

It does not establish recovery across every endpoint, network, or coordinator failure mode.

---

# Qualified Test Coverage

The firmware participated in all actuator-series tests.

## ACT-001

Single physical endpoint:

* accept → MOVE
* unauthorized → NO MOVE
* stale/replay/malformed class → NO MOVE
* boundary unavailable → NO MOVE
* boundary restored → MOVE

Result:

**PASS**

---

## ACT-002

Two physical endpoints with mixed outcomes:

```text
ACCEPT / DENY → MOVE / NO MOVE
DENY / ACCEPT → NO MOVE / MOVE
```

Result:

**PASS x4**

No cross-actuation observed.

---

## ACT-003

Dual accepted:

```text
ACCEPT / ACCEPT → MOVE / MOVE
```

Result:

**PASS x3**

---

## ACT-004

Dual denied:

```text
DENY / DENY → NO MOVE / NO MOVE
```

Result:

**PASS x2**

---

## ACT-005

Shared external boundary unavailable:

```text
request ACCEPT / request ACCEPT
        ↓
boundary unavailable
        ↓
UNAVAILABLE / UNAVAILABLE
        ↓
NO MOVE / NO MOVE
```

After boundary restoration:

```text
ACCEPT / ACCEPT
        ↓
MOVE / MOVE
```

No endpoint resets were required.

Result:

**PASS**

---

# Publication Copy

The repository file:

`esp32_xiao_servo_nuvl.py`

is a sanitized publication copy of the originally qualified source:

`esp32_xiao_servo_nuvl_archer.py`

Sanitization removed local deployment configuration. The actuator decision logic and tested execution path were retained.

Because the publication copy is not byte-identical to the original qualified artifact, the original qualification SHA-256 must not be attributed to the repository copy.

Original qualified SHA-256:

`C29AD7BB8362BD532C62A87CE5D8BE3ED30C25E4543FF52A2CC98992E493AD84`

The original tested artifact and its hash are retained in the local evidence archive.

# Source and Hash Discipline

The original qualified file and the repository publication file have different names:

```text
esp32_xiao_servo_nuvl_archer.py
→
esp32_xiao_servo_nuvl.py
```

The original SHA-256 identifies the exact bytes tested.

If sanitization changed those bytes, the repository file is a derivative artifact.

The repository copy may receive its own publication hash, but that hash represents the publication artifact rather than the original qualified source.

The evidence documentation preserves the original tested filename and hash so the provenance remains explicit.

---

# Known Limitations

This firmware does not independently establish:

* exactly-once physical execution
* persistent actuator-side replay protection
* crash-safe physical execution accounting
* sensor-confirmed mechanical completion
* deterministic physical-action timing
* endpoint-enforced execution deadlines
* independent provider-signature verification at the actuator endpoint
* autonomous local authorization
* safety-critical actuator control

The tested XIAO endpoint consumes the decision returned through the existing NUVL boundary path.

The local boundary therefore remains part of the trusted execution path in this configuration.

A compromised trusted boundary is outside what ACT-001 through ACT-005 resolve.

---

# Related Documentation

Actuator validation:

`../docs/ACTUATOR_VALIDATION.md`

Test matrix:

`../docs/TEST_MATRIX.md`

Hardware setup:

`../docs/HARDWARE_SETUP.md`

Limitations:

`../docs/LIMITATIONS.md`

Test launchers:

`../tests/README.md`

Curated evidence:

`../evidence/README.md`

Detailed results:

`../evidence/ACT001_RESULTS.md`

`../evidence/ACT002_RESULTS.md`

`../evidence/ACT003_RESULTS.md`

`../evidence/ACT004_RESULTS.md`

`../evidence/ACT005_RESULTS.md`

---

# Qualification Statement

The qualified actuator firmware demonstrated that a low-resource physical endpoint can possess execution capability without independently possessing the authority to decide whether that capability may be exercised.

Across ACT-001 through ACT-005, accepted NUVL outcomes entered the physical actuator path while tested non-accepted and unavailable outcomes did not.

That conclusion is limited to **the tested paths and configurations**.

