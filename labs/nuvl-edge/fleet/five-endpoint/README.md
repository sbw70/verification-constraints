# NUVL Edge Lab — Five-Endpoint Fleet

This directory contains the five-endpoint NUVL Edge Lab implementation, test procedures, firmware, supporting utilities, and retained evidence for heterogeneous autonomous fleet testing.

The five-endpoint configuration extends the NUVL Edge Lab from the earlier three-endpoint fleet to a physical fleet containing both status/load endpoints and physical effectors.

The expansion changes fleet size, workload, timing, and fault conditions.

It does not change the underlying authority architecture.

The tested authority path remains:

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

An endpoint may originate a request, perform local computation, or operate autonomously, but request origination is not itself execution authority.

For physical-effector endpoints, consequential execution remains downstream of an accepted authorization result.

---

## Test Classification

The five-endpoint fleet work is primarily:

**Category 1 — NUVL core / no architecture change**

Tests in this directory may vary:

- fleet workload;
- endpoint-local timing;
- endpoint behavior;
- authorization outcome;
- network availability;
- authority-path availability;
- endpoint connectivity;
- endpoint restart behavior;
- shared-boundary load; and
- physical-effector participation.

These changes exercise the existing NUVL authority model rather than introducing a different one.

Optional modules, distributed-provider configurations, independently administered domains, and other architecture extensions are separate test tracks unless explicitly documented otherwise.

---

## Physical Fleet

The five-endpoint laboratory fleet consists of:

### Status / Load Endpoints

- `esp32-field-01` — ESP32-S3 DevKitC-1
- `esp32-s3-02` — ESP32-S3 DevKitC-1
- `esp32-s3-03` — ESP32-S3 DevKitC-1

### Physical-Effector Endpoints

- `esp32-xiao-servo-01` — Seeed XIAO ESP32-S3 with servo actuator
- `esp32-xiao-servo-02` — Seeed XIAO ESP32-S3 with servo actuator

### Shared Laboratory Infrastructure

The tested fleet may use:

- Raspberry Pi boundary/coordinator services;
- local network infrastructure;
- provider-controlled authorization logic;
- independently powered ESP32 endpoints; and
- an external workstation for observation, configuration, or evidence collection.

Exact hardware and software configuration for a specific test is documented in the corresponding file under:

```text
tests/
```

---

## Authority Model

The five-endpoint fleet preserves the NUVL separation between:

```text
request origination
```

and:

```text
execution authority
```

An endpoint may:

- generate a request;
- determine when to issue it;
- generate transaction identifiers;
- perform local computation;
- classify or propose an action; or
- operate on an autonomous schedule.

Those capabilities do not independently authorize consequential execution.

The applicable authority path evaluates the request and returns an outcome.

For a physical-effector endpoint, the intended execution sequence is:

```text
request generated
  ->
authority evaluation
  ->
decision returned
  ->
accepted
  ->
physical execution permitted
```

A denied, invalid, stale, replayed, malformed, or unavailable result does not authorize physical execution.

---

## Operating Models

The five-endpoint fleet supports multiple workload and control models.

### Coordinated Operation

A launcher or coordinator may initiate or synchronize requests for controlled fleet tests.

This mode is useful for:

- baseline comparison;
- synchronized fleet observations;
- mixed-outcome testing;
- controlled release timing; and
- repeatable test setup.

### Autonomous Operation

Endpoints may originate requests according to endpoint-local schedules.

In this mode:

- transaction release is decentralized across the fleet;
- endpoints generate their own request timing;
- endpoint-local transaction identifiers may be used;
- the workstation is not required to release every transaction; and
- the same authority boundary remains in force.

Autonomous request origination does not create autonomous authorization authority.

### Fault and Adversarial Conditions

Individual endpoints or shared infrastructure may be deliberately placed into abnormal conditions.

Examples include:

- elevated request frequency;
- repeated unauthorized requests;
- malformed requests;
- stale or replayed requests;
- endpoint disconnect or reconnect;
- endpoint reboot loops;
- authority-path outage;
- boundary outage;
- restoration after failure;
- degraded network behavior; and
- increased shared-boundary load.

Each such condition is documented as a separate test.

---

## Repository Structure

```text
five-endpoint/
├── README.md
│
├── firmware/
│   └── endpoint firmware and sanitized publication derivatives
│
├── launchers/
│   └── fleet launch and controlled-release utilities
│
├── support/
│   └── boundary, coordinator, and supporting laboratory utilities
│
├── tests/
│   └── test definitions, procedures, results, claims, and limitations
│
└── evidence/
    ├── README.md
    ├── SHA256SUMS.txt
    └── retained test-specific evidence artifacts
```

The authoritative description of each test belongs under:

```text
tests/
```

The corresponding retained evidence belongs under:

```text
evidence/
```

Firmware or utilities required for reproduction or inspection belong in their respective implementation directories.

---

## Test Documentation

Each test document should identify, as applicable:

- test classification;
- module or use case;
- objective;
- hardware and software configuration;
- modified test condition;
- procedure;
- observation window;
- PASS criteria;
- results;
- supported claim;
- limitations;
- restoration or final disposition; and
- evidence references.

A test document is the primary source for interpreting its associated evidence.

Directory-level documentation should not substitute for the individual test record.

---

## Test Areas

The five-endpoint test series may cover the following areas.

### Untethered Operation

Tests may determine whether all five physical endpoints can operate without runtime USB attachment to the observation workstation.

### Autonomous Request Origination

Tests may evaluate independently scheduled endpoint-local request generation across the heterogeneous fleet.

### Sustained Operation

Longer observation windows may evaluate continued participation, transaction uniqueness, authorization correctness, timing behavior, and runtime stability.

### Participant Load Isolation

One endpoint may generate disproportionate request traffic while the behavior of the remaining participants is observed.

### Authorization Isolation

Different endpoints may simultaneously receive different authorization outcomes.

This includes conditions in which one participant is repeatedly denied while others remain provider-admissible.

### Invalid or Adversarial Requests

Tests may exercise:

- malformed requests;
- stale requests;
- replay attempts;
- wrong-context requests;
- unauthorized requests; and
- other documented invalid conditions.

### Connectivity Faults

Individual participants may be disconnected, reconnected, restarted, or otherwise made temporarily unavailable.

### Shared Authority-Path Failure

Tests may deliberately remove access to the applicable provider or boundary authority path.

Such tests may evaluate:

- fail-closed behavior;
- absence of fallback acceptance;
- behavior of physical-effectors during unavailability; and
- recovery after restoration.

### Shared-Boundary Load

The common boundary may be exposed to increasing aggregate fleet load to observe authorization correctness, timing, failure behavior, and saturation effects.

### Physical Execution

Physical-effector endpoints may be used to examine whether consequential action remains downstream of accepted authorization.

Dedicated actuator tests provide stronger evidence for physical execution than software-only fleet logs.

---

## Evidence

Primary retained evidence is located under:

```text
evidence/
```

Depending on the test, evidence may include:

- START and END markers;
- phase-transition markers;
- extracted coordinator logs;
- extracted boundary logs;
- analysis utilities;
- transaction counts;
- endpoint participation records;
- authorization decisions;
- decision reasons;
- transaction-identifier uniqueness checks;
- latency observations;
- failure searches; and
- restoration evidence.

Evidence interpretation, sanitization rules, and publication boundaries are documented in:

```text
evidence/README.md
```

Published evidence integrity values are maintained in:

```text
evidence/SHA256SUMS.txt
```

---

## Evidence Integrity

Evidence is preserved before unnecessary publication-specific modification.

Where an artifact contains local deployment information that is not required for technical review, a sanitized publication derivative may be created.

Examples include removal or replacement of:

- Wi-Fi credentials;
- private credentials;
- environment-specific secrets;
- unnecessary local addressing;
- machine-specific filesystem paths; and
- unrelated laboratory configuration.

A modified publication copy receives its own SHA-256 digest.

The digest of an original tested or collected artifact is not reused for a modified file.

Where provenance matters, the applicable test document may record both:

- the original tested or collected hash; and
- the sanitized publication-copy hash.

---

## Physical Execution Boundary

Two fleet participants contain servo actuators:

```text
esp32-xiao-servo-01
esp32-xiao-servo-02
```

Their inclusion allows the fleet to exercise the relationship between authorization outcome and consequential physical action.

Coordinator and boundary records can establish:

- endpoint participation;
- software-observed authorization outcome;
- decision reason;
- transaction identity; and
- timing.

Those records are not, by themselves, independent physical witnesses of every actuator movement.

Unless a test includes independent actuation evidence, the fleet record should not be interpreted as establishing:

- exactly-once physical execution;
- independently witnessed movement for every accepted transaction;
- calibrated actuator position;
- guaranteed completion of every mechanical action; or
- absence of every possible post-authorization execution failure.

Dedicated actuator testing provides the applicable physical-execution evidence.

---

## Latency Interpretation

Latency values reported by this test series are empirical observations from specific laboratory configurations and measured windows.

They are not deterministic timing guarantees.

The technical record may contain:

- normal low-latency operation;
- isolated outliers;
- sustained degradation;
- timeout conditions;
- unavailable conditions; and
- recovery observations.

Material anomalies remain part of the record even when subsequent tests do not reproduce them.

Where an internal mechanism has not been established, the corresponding test documentation should state that limitation directly.

A later successful run does not retroactively eliminate an earlier anomaly.

---

## Failure Interpretation

Failure-oriented tests are intended to determine how the authority path behaves under a defined adverse condition.

A clean unavailable or denied result may be an expected secure outcome.

A PASS result therefore does not necessarily mean uninterrupted service.

Depending on the test objective, PASS may instead require:

- no unauthorized acceptance;
- no fallback authority;
- no cross-endpoint authorization leakage;
- preservation of endpoint identity;
- continued operation by unaffected participants;
- clean fail-closed behavior; or
- successful restoration without prohibited intervention.

The applicable PASS definition is specified by each test document.

---

## Publication Boundary

Public repository material is intended to expose enough implementation detail and evidence to make the tested behavior inspectable without publishing unnecessary local deployment information.

Publication sanitization should not obscure:

- where authority resides;
- where authorization is evaluated;
- what condition permits physical execution;
- what condition causes denial;
- what condition causes unavailability;
- whether a fault occurred;
- whether an anomaly remains unresolved; or
- what limitations apply to the test.

Sanitization is a publication-control measure, not a mechanism for improving apparent test results.

---

## Current Capability Scope

The five-endpoint test series is intended to establish progressively stronger evidence for a heterogeneous autonomous edge fleet operating under a common provider-controlled authority model.

Depending on completed tests, supported laboratory findings may include:

- independently powered endpoint operation;
- untethered runtime participation;
- autonomous endpoint-local request generation;
- unique transaction origination;
- heterogeneous physical fleet participation;
- sustained autonomous workload;
- mixed authorization outcomes;
- participant-specific authorization isolation;
- asymmetric participant-load isolation;
- fail-closed behavior under authority-path loss;
- restoration following failure;
- continued operation by unaffected fleet members; and
- physical-effector participation downstream of authorization.

Only findings supported by completed tests and retained evidence should be asserted.

---

## Claim Boundary

The five-endpoint laboratory series does not, by itself, establish:

- arbitrary fleet scalability;
- unlimited throughput;
- deterministic latency;
- guaranteed availability;
- geographically distributed operation;
- independently hosted provider infrastructure;
- independent administrative domains;
- tactical-network qualification;
- operational UAS or C-UAS performance;
- arbitrary denial-of-service resistance;
- arbitrary Byzantine fault tolerance;
- resistance to every hostile-client behavior;
- resistance to every network degradation mode;
- exactly-once physical execution;
- production operational readiness;
- certification;
- qualification outside the documented laboratory environment; or
- performance under untested hardware, software, workload, or network conditions.

Broader claims require separate evidence.

---

## Relationship to Other NUVL Edge Tests

The five-endpoint fleet builds on earlier NUVL Edge laboratory work while preserving separate evidence boundaries.

Earlier test series may provide evidence for:

- three-endpoint fleet behavior;
- provider-unavailable behavior;
- persistent single-use artifacts;
- replay resistance;
- crash and power-loss behavior;
- mixed authorization outcomes; and
- physical actuator gating.

Those results are not automatically reproduced by the five-endpoint fleet.

Where a capability is exercised again at five-endpoint scale, the corresponding five-endpoint test provides the applicable evidence.

Where it has not yet been exercised, the earlier result remains separate.

---

## Reproduction and Review

Repository users reviewing or reproducing a test should begin with the corresponding file under:

```text
tests/
```

That document identifies the relevant:

- firmware;
- support utilities;
- test condition;
- evidence artifacts;
- expected outcomes;
- integrity hashes; and
- limitations.

The top-level README defines the fleet and repository boundary.

The individual test documents define what was actually tested.
