# NUVL Physical Actuator Validation — Limitations

## Scope

ACT-001 through ACT-005 extend the NUVL validation bench from logical endpoint outcomes to observable physical actuation using two Seeed XIAO ESP32-S3 endpoints and MG90S-class servo effectors.

The series demonstrates physical decision binding **in the tested paths**.

It does not establish a general-purpose actuator safety architecture, deterministic real-time control system, exactly-once physical execution mechanism, or independently instrumented proof of mechanical state.

The limitations below define the boundary of the evidence.

---

## 1. Software Command Completion Is Not Mechanical-State Proof

The actuator firmware reports:

* `actuator_attempted`
* `actuator_command_completed`
* `actuator_error`

For accepted runs, the expected state was:

```text
actuator_attempted=True
actuator_command_completed=True
actuator_error=None
```

This establishes that the endpoint entered the actuator path and completed the software actuator routine without a reported error.

It does **not** independently prove that the servo:

* reached the commanded angular position,
* reached the position within a specified tolerance,
* remained at that position,
* completed useful mechanical work,
* encountered no obstruction,
* or moved exactly once.

Physical movement was separately observed during the documented tests, with selected runs captured on video.

No independent position sensor or encoder was used.

---

## 2. No Independent Physical Signal Witness

ACT-001 through ACT-005 did not use an independent electrical instrument to witness the actuator signal.

No oscilloscope, logic analyzer, or external signal-capture device was used to independently record GPIO5 / D4 during the qualified NUVL runs.

PWM behavior was tested during servo bring-up, including settled MicroPython duty readback and observable response to different pulse widths.

That is sufficient for the documented bench qualification but does not provide an independently timestamped electrical record of each actuator command.

---

## 3. No Exactly-Once Physical Execution Claim

The actuator series does not demonstrate exactly-once physical execution.

An accepted result followed by one observed movement does not establish that every possible failure condition guarantees one and only one physical action.

The tests did not exercise crash boundaries such as:

* failure immediately before actuator invocation,
* failure during PWM initialization,
* failure during the physical command,
* failure immediately after mechanical movement,
* reboot after command issuance but before result reporting,
* duplicated accepted result delivery.

Accordingly, the actuator evidence should be described as **authorization-to-actuation binding**, not exactly-once actuation.

---

## 4. Persistent Single-Use Authority Was Not Integrated Into These Actuator Tests

Separate NUVL testing has examined bounded single-use authority and persistence behavior.

ACT-001 through ACT-005 do not combine those mechanisms with the physical servo execution path.

The actuator series therefore does not independently establish:

* single-use physical actuation,
* persistent actuator-side spent state,
* physical replay prevention across restart,
* physical replay prevention across power loss,
* crash-safe physical-use accounting,
* or persistent remaining-use counts tied to an actuator.

Those require separate integration evidence.

---

## 5. `stale_replay_malformed` Is a Decision-Class Test, Not a Persistent Replay Test

ACT-001 included:

`denied / stale_replay_malformed`

The endpoint correctly reported:

```text
actuator_attempted=False
actuator_command_completed=False
actuator_error=None
```

No physical movement was observed.

This demonstrates that the tested `stale_replay_malformed` rejection class does not enter the actuator path.

It does **not** demonstrate persistent replay-state enforcement by the actuator endpoint.

The result must not be represented as equivalent to the persistent replay, restart, power-loss, or double-spend tests performed elsewhere in the NUVL test program.

---

## 6. Authorization Latency Is Not Physical-Action Latency

The actuator launchers report `elapsed_ms`.

This value is captured after the NUVL response and before completion of the approximately one-second servo hold.

Reported values such as:

`33 ms`

or:

`37 ms`

therefore describe the authorization/request portion of the tested path.

They do **not** mean that the physical actuator completed its mechanical movement in 33 or 37 milliseconds.

The tests did not independently measure:

* time from request creation to initial shaft movement,
* time from accepted decision to first physical motion,
* time to final commanded position,
* mechanical settling time,
* or total request-to-physical-completion latency.

Authorization latency and mechanical execution time must remain separate measurements.

---

## 7. No Endpoint-Enforced Execution Deadline Was Demonstrated

The actuator tests used a 250 ms request-latency budget in the test oracle.

Results were classified against that budget.

This is not equivalent to proving that the endpoint itself enforces a maximum authorization-to-execution deadline.

The series does not establish that an accepted result arriving after an execution deadline would necessarily be rejected locally rather than actuated.

A deadline-enforcement claim requires a separate endpoint execution-time policy and corresponding tests.

---

## 8. Near-Concurrent Fan-In Is Not Parallel Boundary Processing

ACT-002 through ACT-005 coordinated two physical endpoints through the shared NUVL path.

ACT-003 demonstrated both endpoints receiving admissible results and both servos moving during the same coordinated run.

This supports **near-concurrent coordinated physical fan-in**.

It does not establish true parallel request processing at the boundary.

No parallel-boundary-processing claim should be made from ACT-003.

---

## 9. No Cross-Actuation Was Observed, but the Test Population Is Small

ACT-002 reversed the mixed authorization assignment:

```text
servo-01 ACCEPT / servo-02 DENY
```

and:

```text
servo-01 DENY / servo-02 ACCEPT
```

Each assignment was executed twice.

The correct servo moved in every documented run, while the denied servo remained inactive.

No cross-actuation was observed.

This is meaningful evidence of per-device physical outcome binding in the tested configuration, but it is not statistical proof that cross-assignment is impossible under all fleet sizes, timing conditions, or fault states.

The tested physical fleet contained two effectors.

---

## 10. Physical Fleet Scale Is Limited

The actuator series used:

* one physical effector for ACT-001,
* two physical effectors for ACT-002 through ACT-005.

The tests therefore do not establish actuator behavior at large fleet scale.

They do not determine:

* maximum physical endpoint count,
* boundary saturation behavior with large actuator fleets,
* network contention limits,
* actuator synchronization limits,
* or large-fleet tail latency.

The evidence applies to the tested one- and two-effector configurations.

---

## 11. Shared-Boundary Outage Was a Specific Failure Mode

ACT-005 deliberately stopped the shared NUVL boundary and confirmed that port 8089 was unavailable.

Both endpoints requested accept.

Both returned:

`unavailable / OSError(104,)`

Neither endpoint invoked its actuator.

No physical movement was observed.

This demonstrates fail-unavailable behavior for the tested boundary-loss condition.

It does not exhaustively demonstrate behavior under every degraded-network condition.

The series did not systematically test actuator behavior under:

* severe packet loss,
* intermittent connectivity,
* partial responses,
* extremely delayed responses,
* connection flapping,
* asymmetric network failure,
* malformed boundary responses,
* or prolonged connection timeout loops.

Boundary absence and degraded boundary connectivity are distinct failure conditions.

---

## 12. Recovery Was Demonstrated Without Endpoint Reset, Not Across Every Recovery Mode

ACT-001 and ACT-005 demonstrated recovery after the external boundary was restored.

The XIAO endpoints were not reset.

Accepted physical actuation resumed.

This demonstrates recovery for the tested external-boundary restart sequence.

It does not establish recovery behavior after:

* endpoint reset,
* endpoint power loss,
* network infrastructure restart,
* coordinator restart during execution,
* corrupted local endpoint state,
* or simultaneous multi-component failure.

---

## 13. Servo Reset and Initial Positioning Are Out-of-Band

Servo reset or initial positioning was treated as test preparation.

It was not part of the NUVL decision path.

Movement performed to place a servo in a useful starting position must not be counted as authorized physical execution.

Only movement occurring after the documented NUVL accepted path was treated as authorization-gated actuator evidence.

---

## 14. Hobby Servo Hardware Limits the Mechanical Claim

The qualified effectors were MG90S-class hobby servos.

The tests demonstrate a visible, low-energy physical consequence suitable for bench validation.

They do not establish behavior for:

* industrial actuators,
* motors,
* valves,
* relays controlling high-energy loads,
* robotic systems,
* vehicle controls,
* weapons,
* safety-critical effectors,
* or other consequential machinery.

The authority-binding concept may be evaluated with other effectors, but ACT-001 through ACT-005 provide evidence only for the hardware actually tested.

---

## 15. Board-Powered Servo Configuration Is Bench-Specific

The qualified XIAO configuration powered the servo from the board's 5V/VBUS path.

No external servo power supply was used.

No brownout or reset was observed during the qualified tests.

This does not establish that board-powered actuation is appropriate for:

* higher-current servos,
* multiple servos per endpoint,
* heavily loaded actuators,
* continuous-duty operation,
* or production deployment.

Appropriate power engineering is required for other actuator classes and loads.

---

## 16. Full-Size ESP32-S3 Servo Failure Was Not Root-Caused

Before the XIAO actuator path was selected, MG90S-class servos were tested with full-size ESP32-S3 development boards.

Software PWM generation was exercised, but physical servo movement was not obtained.

The cause was not conclusively isolated.

No electrical measurement was performed that established whether the failure involved:

* board power delivery,
* wiring,
* servo behavior,
* signal characteristics,
* or another hardware-specific condition.

The full-size-board servo path should therefore be described as **unresolved**, not as a proven board defect.

It was excluded from the qualified actuator configuration.

---

## 17. PWM Readback Required Settling

During early servo bring-up, immediate MicroPython PWM readback could report the previous duty value.

After approximately 100 ms of settling, commanded and reported pulse widths matched.

This was treated as a test-harness/instrumentation timing assumption rather than a demonstrated PWM-generation failure.

The observation matters when reproducing the hardware qualification: immediate software readback should not be treated as definitive evidence of the settled PWM state.

---

## 18. IP Addresses and COM Ports Are Not Durable Identities

The test records include observed values such as:

* `COM3`
* `COM16`
* `192.168.0.81`
* `192.168.0.186`

These identify the tested configuration at the time of execution.

They are not permanent device identities.

Endpoint identity was maintained separately using `device_id.txt`.

Reproduction should not assume identical COM-port assignments or DHCP addresses.

---

## 19. The Raspberry Pi Remains a Trusted Local Boundary in This Configuration

The actuator endpoints consume the result returned through the existing NUVL boundary path.

The physical actuator tests do not change that trust relationship.

The endpoints do not independently verify provider cryptographic authority before executing the servo command in this tested configuration.

Accordingly, compromise of the trusted local boundary remains outside what ACT-001 through ACT-005 resolve.

The actuator tests demonstrate binding from the returned NUVL result to physical execution; they do not eliminate the existing trust-boundary limitation.

---

## 20. No Autonomous Local Authorization Claim

The XIAO actuator endpoints do not demonstrate autonomous authority to decide whether consequential action is admissible.

The physical actuator integration was specifically structured so that execution follows the externally returned decision.

The tests therefore support separation between endpoint execution capability and externally controlled admissibility.

They do not demonstrate or require the endpoint to independently mint, enlarge, or substitute authorization.

---

## 21. No Safety Certification

ACT-001 through ACT-005 are engineering validation tests.

They are not:

* functional-safety certification,
* weapons-safety certification,
* industrial-control certification,
* real-time certification,
* reliability qualification,
* environmental qualification,
* electromagnetic compatibility testing,
* or production hardware certification.

No SIL, ASIL, DAL, or comparable safety-integrity claim follows from these results.

---

## 22. Physical Observation Is Human Observation

Physical movement and non-movement were observed directly during the tests, with video captured for selected runs.

There was no automated independent mechanical witness for every run.

Accordingly, statements such as:

`physical movement observed`

and:

`no physical movement observed`

describe the documented test observation.

They should not be rewritten as:

`mechanically proven`

or:

`sensor verified`

unless later testing adds independent instrumentation.

---

# Claim Boundary

The actuator series supports the following bounded conclusion:

> In the tested single- and two-endpoint paths, externally determined NUVL admissibility remained bound to physical actuator execution. Accepted decisions produced the intended observable physical actuation, while unauthorized, stale/replay/malformed-class, and boundary-unavailable outcomes did not enter the actuator path. Across two effectors, per-device authorization remained associated with the correct physical output, including mixed outcomes, reversed outcomes, dual acceptance, dual denial, and shared-boundary outage/recovery.

The series does **not** support stronger claims of:

* exactly-once physical execution,
* sensor-confirmed mechanical completion,
* persistent physical replay prevention,
* deterministic execution timing,
* endpoint-enforced execution deadlines,
* parallel boundary processing,
* arbitrary fleet scale,
* exhaustive degraded-network tolerance,
* independent endpoint authorization,
* or safety-critical deployment readiness.

All results and conclusions remain qualified by:

**in the tested paths and configurations.**

