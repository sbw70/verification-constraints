
# NUVL Physical Actuator Hardware Setup

## Overview

This document records the hardware configuration used for the NUVL physical actuator validation series, ACT-001 through ACT-005.

The qualified actuator configuration used Seeed XIAO ESP32-S3 endpoints driving MG90S-class micro servos. The physical actuator was added as an execution output behind the existing NUVL decision path.

The hardware configuration was intentionally simple:

`NUVL decision → XIAO ESP32-S3 → GPIO5 / D4 → servo`

An accepted result permitted the endpoint to issue the servo command. Non-accepted results did not invoke the actuator.

This document describes the tested bench configuration. It is not a general-purpose servo wiring specification or production hardware design.

---

# Hardware Inventory

## Actuator endpoints

Two Seeed XIAO ESP32-S3 boards were qualified for the two-endpoint actuator tests.

### Endpoint 1

Device identity:

`esp32-xiao-servo-01`

Hardware:

* Seeed XIAO ESP32-S3
* ESP32-S3 rev 0.2
* 8 MB flash
* 8 MB PSRAM
* MicroPython v1.28.0
* MG90S-class servo
* Servo signal on D4 / GPIO5

USB port during initial qualification:

`COM3`

Wi-Fi MAC:

`1c:db:d4:45:11:e8`

IP during actuator validation:

`192.168.0.81`

The COM assignment and IP address are observations from the tested bench and should not be treated as permanent endpoint identifiers.

---

### Endpoint 2

Device identity:

`esp32-xiao-servo-02`

Hardware:

* Seeed XIAO ESP32-S3
* ESP32-S3 rev 0.2
* 8 MB flash
* 8 MB PSRAM
* MicroPython v1.28.0
* MG90S-class servo
* Servo signal on D4 / GPIO5

USB enumeration during provisioning changed from:

`COM15`

to:

`COM16`

Wi-Fi MAC:

`1c:db:d4:45:10:a4`

IP during actuator validation:

`192.168.0.186`

As with endpoint 1, USB COM assignments and DHCP addresses are not durable identities.

The persistent logical endpoint identity was provided through:

`device_id.txt`

---

# Servo Wiring

The qualified XIAO actuator configuration used:

| Servo connection | XIAO connection |
| ---------------- | --------------- |
| Signal           | D4 / GPIO5      |
| Power            | XIAO 5V / VBUS  |
| Ground           | XIAO GND        |

The servo was powered directly from the XIAO 5V/VBUS path during the documented tests.

No external actuator power supply was used for the qualified ACT-001 through ACT-005 runs.

No brownout or endpoint reset was observed during the qualified XIAO servo tests.

This bench configuration should not be interpreted as a recommendation to power arbitrary servos or higher-current actuators directly from the XIAO.

---

# Servo Control

The qualified actuator implementation used hardware PWM.

Configuration:

* Signal pin: GPIO5 / D4
* PWM frequency: 50 Hz
* PWM period: approximately 20 ms

Approximate tested pulse positions:

| Pulse width | Observed purpose         |
| ----------: | ------------------------ |
|     ~1.0 ms | one servo position       |
|     ~1.5 ms | center                   |
|     ~2.0 ms | alternate servo position |

Corresponding settled MicroPython duty readbacks observed during qualification included approximately:

* `3272` for ~1.0 ms
* `4912` for ~1.5 ms
* `6552` for ~2.0 ms

The actuator firmware used an approximately 2.0 ms pulse command for the NUVL accepted-path movement.

PWM remained active for approximately one second and was then deinitialized.

The servo therefore was not continuously held under PWM after the command interval.

---

# Initial Servo Qualification

## Full-size ESP32-S3 attempt

Before the XIAO configuration was selected, MG90S-class servos were tested with full-size ESP32-S3 development boards.

Tested configuration included:

* full-size ESP32-S3 boards
* GPIO4 signal
* board 5V power
* 50 Hz PWM
* direct bit-bang pulse generation

Software PWM generation was observed, but physical servo movement was not obtained.

The cause was not isolated.

Possible board or power-path behavior was considered, but no electrical measurement was performed that established the fault domain.

Accordingly:

**The full-size ESP32-S3 servo path remained unresolved and was not used for actuator qualification.**

One instrumentation issue was identified during this work: immediate MicroPython PWM readback could return the previous duty value. After approximately 100 ms of settling time, the reported duty matched the requested value.

This was treated as an instrumentation/harness timing issue rather than evidence of PWM failure.

---

# XIAO Servo Qualification

## Endpoint 1

The first XIAO ESP32-S3 demonstrated physical servo movement using D4 / GPIO5.

Both direct pulse generation and hardware PWM produced movement.

Hardware PWM was retained for the actuator firmware.

The qualified servo path demonstrated distinguishable positions around:

* 1.0 ms
* 1.5 ms
* 2.0 ms

No brownout or reset was observed.

---

## Endpoint 2

The second XIAO was independently erased, flashed, provisioned, and physically qualified before being added to ACT-002.

MicroPython image:

`ESP32_GENERIC_S3-20260406-v1.28.0.bin`

Flash operation:

**PASS**

Flash verification:

**PASS**

Interpreter:

**PASS**

Device identity:

`esp32-xiao-servo-02`

Initial physical servo testing produced movement but did not immediately show the expected full sequence. The endpoint was therefore not considered qualified at that point.

Individual pulse positions were then tested.

Approximately 2.0 ms produced physical movement and a settled duty readback near:

`6552`

Approximately 1.0 ms produced a substantially different physical position and a settled duty readback near:

`3272`

The full position sequence was subsequently verified:

* ~1.0 ms → distinct position
* ~1.5 ms → center
* ~2.0 ms → alternate position

Settled duty values matched the requested pulse positions.

No brownout or reset was observed.

**Endpoint 2 servo bring-up: PASS**

Only after this independent physical qualification was the second endpoint added to the two-effector NUVL tests.

---

# Endpoint Provisioning

Each XIAO maintained a distinct logical identity in:

`device_id.txt`

Endpoint 1:

`esp32-xiao-servo-01`

Endpoint 2:

`esp32-xiao-servo-02`

Both endpoints subsequently ran the same actuator firmware.

Original qualified firmware:

`esp32_xiao_servo_nuvl_archer.py`

Original tested size:

`9,790 bytes`

Original tested SHA-256:

`C29AD7BB8362BD532C62A87CE5D8BE3ED30C25E4543FF52A2CC98992E493AD84`

The firmware hash was verified directly on both XIAO filesystems.

Separate `device_id.txt` files provided the distinct endpoint identities.

For publication, the sanitized firmware copy is stored as:

`firmware/esp32_xiao_servo_nuvl.py`

The original qualification hash above belongs to the original tested source. It must not be represented as the hash of a sanitized or otherwise modified publication copy unless that copy independently hashes identically.

---

# Network Configuration

The actuator tests used the existing Archer-based NUVL bench network.

During the documented tests:

| Endpoint              | MAC                 | Observed IP     |
| --------------------- | ------------------- | --------------- |
| `esp32-xiao-servo-01` | `1c:db:d4:45:11:e8` | `192.168.0.81`  |
| `esp32-xiao-servo-02` | `1c:db:d4:45:10:a4` | `192.168.0.186` |

Both endpoints were simultaneously observed as `REACHABLE` from the Raspberry Pi before ACT-002.

The test launchers checked expected endpoint identity and IP binding.

The IP addresses above are evidence from the qualified configuration, not architectural requirements.

---

# Raspberry Pi Boundary

The Raspberry Pi provided the external NUVL boundary used by the actuator endpoints.

Boundary service during testing:

`/home/seth/nuvl_local_hardened_latency.py`

NUVL service port:

`8089`

Health endpoint:

`/health`

Healthy response:

`ok`

The coordinator service used during the actuator testing was available on port:

`19052`

The actuator endpoints did not bypass the external decision path to determine their own admissibility.

The physical execution path was therefore:

`launcher → coordinator → XIAO request → Pi NUVL boundary → returned result → endpoint actuator gate → servo`

---

# Physical Execution Gate

The actuator integration was intentionally narrow.

Conceptually:

```text
if decision == accepted:
    invoke actuator
else:
    do not invoke actuator
```

The actual test telemetry distinguished three software actuator states:

`actuator_attempted`

`actuator_command_completed`

`actuator_error`

For accepted runs, the expected state was:

```text
actuator_attempted=True
actuator_command_completed=True
actuator_error=None
```

For denied, stale/replay/malformed-class, and unavailable results:

```text
actuator_attempted=False
actuator_command_completed=False
actuator_error=None
```

The actuator function was not called from the tested non-accepted branches.

---

# Idle and Startup Behavior

Servo reset or initial positioning was treated as out-of-band test preparation.

It was not considered part of the NUVL authorization path.

During normal actuator firmware startup and idle polling, the servo was expected to remain untouched until an accepted decision reached the execution gate.

For the first actuator endpoint, the servo remained physically inactive after firmware boot and network association before the first authorization test was executed.

This distinction matters when interpreting the physical evidence:

**Test preparation movement is not authorized actuator execution.**

Only movement following the documented accepted decision path was counted as NUVL-gated physical actuation.

---

# ACT-001 Hardware Configuration

ACT-001 used one physical actuator endpoint:

`esp32-xiao-servo-01`

Configuration:

* XIAO ESP32-S3
* MG90S-class servo
* D4 / GPIO5 signal
* XIAO 5V/VBUS servo power
* external NUVL boundary
* external coordinator
* Archer LAN
* 250 ms NUVL request-latency budget

ACT-001 exercised:

* accepted physical movement
* unauthorized non-actuation
* stale/replay/malformed-class non-actuation
* boundary-unavailable non-actuation
* post-boundary-restoration physical recovery

---

# ACT-002 Through ACT-005 Hardware Configuration

ACT-002 through ACT-005 used both physical endpoints simultaneously:

`esp32-xiao-servo-01`

and

`esp32-xiao-servo-02`

Each endpoint had:

* its own XIAO ESP32-S3
* its own MG90S-class servo
* its own `device_id.txt`
* its own network identity
* the same verified actuator firmware
* its own D4 / GPIO5 physical output

Both shared:

* the Archer network
* Raspberry Pi boundary
* coordinator path
* external authorization service path

This configuration allowed per-device authorization results to be compared directly with separate physical effectors.

---

# Physical Matrix

The two-effector hardware configuration was exercised through all four basic accept/deny combinations:

| Servo 01 | Servo 02 | Expected physical state |
| -------- | -------- | ----------------------- |
| ACCEPT   | DENY     | MOVE / NO MOVE          |
| DENY     | ACCEPT   | NO MOVE / MOVE          |
| ACCEPT   | ACCEPT   | MOVE / MOVE             |
| DENY     | DENY     | NO MOVE / NO MOVE       |

A fifth condition removed the shared authorization boundary while both endpoints requested accept:

| Servo 01 request | Servo 02 request | Boundary    | Expected          |
| ---------------- | ---------------- | ----------- | ----------------- |
| ACCEPT           | ACCEPT           | unavailable | NO MOVE / NO MOVE |

After boundary restoration, both endpoints returned to:

`MOVE / MOVE`

without either XIAO being reset.

---

# Measurement Boundary

The actuator test launchers report `elapsed_ms`.

This value represents the NUVL request/authorization portion of the tested path.

It is captured after the NUVL response and before the approximately one-second servo hold completes.

Therefore:

**`elapsed_ms` is not total physical-action latency.**

For example, a reported authorization latency of 33 ms does not mean that the complete mechanical servo action finished in 33 ms.

The tests intentionally separate:

1. authorization/request latency,
2. software actuator command execution, and
3. observed physical movement.

No independent sensor measured final servo position or mechanical completion time.

---

# Hardware Evidence Boundary

Physical movement was directly observed during the documented tests, with video captured for selected runs.

Software telemetry additionally recorded whether the actuator command was attempted and completed.

These are complementary evidence sources.

However:

`actuator_command_completed=True`

means the software actuator routine completed without a reported error.

It does **not** independently prove:

* final shaft position,
* commanded angular accuracy,
* mechanical load completion,
* absence of obstruction,
* exactly-once physical execution.

No independent encoder, position sensor, current sensor, oscilloscope, or external signal witness was used during ACT-001 through ACT-005.

---

# Reproducing the Hardware Configuration

Minimum physical components for the tested actuator configuration:

* Seeed XIAO ESP32-S3
* MG90S-class servo
* USB power/data connection for provisioning
* Wi-Fi connectivity to the NUVL bench network
* Raspberry Pi running the NUVL boundary/coordinator path

For two-effector testing:

* 2 × Seeed XIAO ESP32-S3
* 2 × MG90S-class servo
* distinct `device_id.txt` identities
* shared access to the same external NUVL boundary

Before running NUVL actuator tests, independently verify:

1. the endpoint boots normally;
2. its device identity is correct;
3. its firmware is the intended build;
4. it joins the expected network;
5. D4 / GPIO5 produces valid servo PWM;
6. distinct pulse widths produce distinguishable physical movement;
7. PWM can be released after the command;
8. the endpoint does not brown out or reset during the qualification movement.

Only after the physical path is independently functional should authorization behavior be interpreted as actuator-binding evidence.

---

# Safety and Scope

The documented bench uses low-power hobby servos with no hazardous mechanical load.

The configuration is a validation platform, not a production actuator-control design.

Higher-current, higher-energy, safety-critical, or mission-critical effectors require appropriate electrical isolation, power design, feedback sensing, interlocks, fault handling, and independent safety engineering.

The actuator series demonstrates authorization-to-execution binding **in the tested paths**.

It does not establish hardware safety certification, deterministic real-time control, mechanical position assurance, or suitability for safety-critical actuation.
