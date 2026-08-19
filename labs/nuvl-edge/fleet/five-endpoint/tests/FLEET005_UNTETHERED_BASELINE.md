# FLEET-005 — Five-Endpoint Untethered Baseline

## Purpose

FLEET-005 established the initial qualified five-endpoint physical baseline for the NUVL Edge Lab.

The test extended the existing fleet from three homogeneous ESP32-S3 endpoints to five heterogeneous physical endpoints:

- three ESP32-S3 DevKitC-1 status/load endpoints; and
- two Seeed XIAO ESP32-S3 physical-effector endpoints.

The primary objective was to determine whether all five endpoints could operate untethered from controlling hosts while preserving correct endpoint identity, provider-controlled authorization outcomes, result binding, and physical execution behavior.

This test remained within the existing NUVL architecture.

No new authority was introduced at the endpoints.

---

## Test Classification

**Classification:** NUVL core — no architecture change.

**Use case:** heterogeneous multi-endpoint operation with physical effectors.

**New evidence supported:** five independently powered physical endpoints can participate in the same provider-controlled authority path while preserving expected endpoint/result binding.

**Not established:** autonomous endpoint request generation, geographically distributed operation, independently hosted providers, tactical-network performance, or production fleet behavior.

---

## Tested Topology

    esp32-field-01 --------\
    esp32-s3-02 -----------\
    esp32-s3-03 ------------> NUVL boundary -> provider decision
    esp32-xiao-servo-01 ----/                     |
    esp32-xiao-servo-02 ---/                      |
                                                  v
                                           endpoint result
                                                  |
                                     accepted path only
                                                  |
                                                  v
                                       physical execution
                                       where applicable

The fleet consisted of:

    esp32-field-01
    esp32-s3-02
    esp32-s3-03
    esp32-xiao-servo-01
    esp32-xiao-servo-02

The three DevKit endpoints served as status/load endpoints.

The two XIAO endpoints were connected to physical servo actuators.

---

## Hardware

Tested hardware included:

- 3 × ESP32-S3 DevKitC-1
- 2 × Seeed XIAO ESP32-S3
- 2 × servo actuators
- Raspberry Pi 5
- Archer Wi-Fi infrastructure
- external USB power for endpoint runtime
- separate launcher/observer system where required

During the qualified runtime, none of the five endpoints depended on a USB connection to the launcher, Raspberry Pi, or another controlling host.

The endpoint boards were independently powered.

---

## Test Method

FLEET-005 used coordinated release timing to exercise all five endpoints during each run.

The launcher used for the five-endpoint campaign was:

    run_five_endpoint_accept_archer.py

The test intentionally retained coordinated request initiation.

Autonomous endpoint-local request generation was introduced later under FLEET-006.

For each FLEET-005 run, the expected result was:

- all five endpoints participate;
- all five results return;
- endpoint identity remains correctly bound;
- each provider decision matches the expected result;
- no endpoint reports an unavailable result;
- no result is assigned to the wrong endpoint;
- both physical-effector endpoints invoke their actuator function following acceptance; and
- no late or unaccounted endpoint result remains after the run.

---

## Acceptance Criteria

A run was considered PASS only when:

    expected endpoints = 5
    received endpoints = 5
    missing results = 0
    unavailable results = 0
    identity/IP mismatches = 0
    outcome mismatches = 0
    actuator-report mismatches = 0
    late results = 0
    stragglers = 0

Physical actuator movement was also observed for the two XIAO endpoints.

---

## Results

The qualified FLEET-005 campaign completed:

    20 / 20 coordinated runs PASS
    100 / 100 endpoint transactions correct

Across the campaign:

    missing results: 0
    unavailable results: 0
    identity/IP mismatches: 0
    outcome mismatches: 0
    actuator-report mismatches: 0
    late results: 0
    stragglers: 0

Observed authorization latency across the campaign ranged from:

    minimum: 30 ms
    maximum: 49 ms

These latency values describe the tested laboratory configuration only.

They are not presented as deterministic latency guarantees or operational network-performance claims.

---

## Physical Execution

Both XIAO physical-effector endpoints produced observable servo movement during every qualified FLEET-005 run.

Physical execution remained downstream of the accepted result path.

The test therefore extended the five-endpoint fleet result beyond software-only endpoint reporting by including two physical consequences within the same coordinated workload.

---

## Physical Anomaly

Intermittent shortened servo travel was observed during the campaign.

An affected servo did not always appear to complete the same mechanical stroke.

The endpoint nevertheless reported actuator invocation and completion, and physical movement was observed.

The exact cause was not isolated.

Possible mechanical, electrical, power, PWM, or servo-specific causes were not independently distinguished during FLEET-005.

No independent actuator-position sensor, PWM witness, or command witness was used.

The anomaly is therefore retained as a limitation rather than interpreted beyond the available evidence.

FLEET-005 supports:

    accepted authorization -> actuator function invoked -> physical movement observed

It does not establish:

    calibrated actuator position
    identical mechanical stroke on every invocation
    independent verification of the actuator command
    exactly-once physical execution

---

## Supported Finding

FLEET-005 demonstrated that five untethered heterogeneous ESP32-S3 endpoints could participate in a coordinated NUVL provider-controlled authorization workload while preserving expected endpoint identity and outcome binding across 100 endpoint transactions.

Both physical-effector endpoints produced authorized movement during every qualified run.

The test establishes a five-endpoint physical laboratory baseline for subsequent autonomous, failure, recovery, and endurance testing.

---

## Limitations

FLEET-005 does not establish:

- autonomous endpoint-local request generation;
- geographically distributed operation;
- independently hosted provider infrastructure;
- independent administrative domains;
- tactical RF performance;
- contested-spectrum performance;
- deterministic authorization latency;
- production reliability or availability;
- calibrated servo positioning;
- full mechanical stroke for every accepted transaction;
- exactly-once physical execution;
- independent actuator-command witnessing;
- operational UAS or C-UAS integration; or
- production fleet scalability.

All findings are bounded to the tested NUVL Edge Lab hardware, firmware, network, authority path, and test conditions.

---

## Relationship to FLEET-006

FLEET-005 established the qualified five-endpoint untethered baseline.

FLEET-006 retained the five-endpoint heterogeneous physical topology while changing how work originated.

Under FLEET-006, endpoints generated their own transaction identifiers and initiated requests according to endpoint-local schedules rather than relying on coordinated launcher release timing.

Accordingly:

    FLEET-005 = five-endpoint untethered coordinated baseline

    FLEET-006 = five-endpoint autonomous asynchronous operation

The two tests should remain separately documented so that the additional capability introduced by FLEET-006 is not attributed retroactively to the FLEET-005 baseline.
