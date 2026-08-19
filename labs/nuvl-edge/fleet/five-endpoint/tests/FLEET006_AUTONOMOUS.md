# FLEET-006 — Five-Endpoint Autonomous Asynchronous Operation

## Purpose

FLEET-006 extended the qualified five-endpoint NUVL Edge Lab configuration from coordinated launcher-controlled operation to autonomous endpoint-local request generation.

The test retained the heterogeneous physical fleet established under FLEET-005:

- three ESP32-S3 DevKitC-1 status/load endpoints; and
- two Seeed XIAO ESP32-S3 physical-effector endpoints.

The primary objective was to determine whether the five endpoints could independently originate requests on their own schedules while preserving:

- endpoint identity;
- unique transaction identification;
- provider-controlled authorization;
- correct result binding;
- physical execution gating; and
- continued multi-endpoint operation over a sustained period.

FLEET-006 changed the workload-generation model.

It did not change the underlying NUVL authority architecture.

---

## Test Classification

**Classification:** NUVL core — no architecture change.

**Use case:** autonomous asynchronous multi-endpoint operation.

**New evidence supported:** heterogeneous physical endpoints can independently originate requests without a central launcher controlling each transaction while remaining subject to the same provider-controlled authority path.

**Not established:** geographically distributed operation, independently hosted providers, tactical-network operation, deterministic latency, or production fleet scalability.

---

## Relationship to FLEET-005

FLEET-005 established the five-endpoint untethered coordinated baseline.

FLEET-006 retained the same general physical fleet but removed coordinated launcher release as the source of individual endpoint transactions.

The distinction is:

    FLEET-005
        five endpoints
        untethered runtime
        coordinated request initiation

    FLEET-006
        five endpoints
        untethered runtime
        endpoint-local request initiation
        asynchronous schedules
        endpoint-generated transaction IDs

The endpoint became responsible for determining when to initiate its own request.

It did not become the authority for deciding whether the requested operation was admissible.

---

## Tested Fleet

The autonomous fleet consisted of:

    esp32-field-01
    esp32-s3-02
    esp32-s3-03
    esp32-xiao-servo-01
    esp32-xiao-servo-02

The three DevKit endpoints operated as status/load endpoints.

The two XIAO endpoints were connected to physical servo actuators.

---

## Authority Path

The authority path remained:

    endpoint-local request generation
                |
                v
          NUVL boundary
                |
                v
      provider-controlled decision
                |
                v
          endpoint result
                |
                v
       accepted result path
                |
                v
      physical execution
      where applicable

Autonomous request generation did not create autonomous execution authority.

The endpoint could determine when to request an operation.

The provider-controlled path continued to determine whether that operation was accepted.

For the XIAO endpoints, physical actuator execution remained downstream of the accepted result path.

---

## Autonomous Firmware

DevKit firmware:

    esp32_autonomous_async_archer.py

SHA-256:

    BE3103D0958AAB49EF325982C02A43CCD702544764526448B9CD77C8F684D954

XIAO servo firmware:

    FLEET006_xiao_autonomous_async_archer.py

SHA-256:

    B34E5A910E8ED91D6E303A1532CC7D8D6DFB72D614767AF7DD93C40732375048

The endpoints generated transaction identifiers locally using endpoint identity, local timing information, and an endpoint-local counter.

This removed dependence on a central launcher for assignment of individual transaction identifiers during autonomous runtime.

---

## Asynchronous Scheduling

The endpoints operated on endpoint-local schedules rather than a common coordinated release.

This intentionally allowed transactions from different endpoints to arrive independently and overlap naturally over time.

The resulting workload was therefore driven by the physical endpoints themselves rather than by a launcher iterating through a fixed fleet transaction sequence.

The coordinator remained available for result collection and observation.

It was not the source of the individual autonomous endpoint requests.

---

## Primary Sustained Observation

The primary FLEET-006 autonomous observation captured:

    total transactions: 2,125
    unique run IDs: 2,125
    duplicate run IDs: 0

Decision results:

    accepted: 2,125
    provider_admissible: 2,125

All five endpoint identities were represented in the dataset.

No duplicate transaction identifier was observed in the captured window.

The expected provider-controlled outcome remained correctly associated with the originating endpoint throughout the observation.

---

## Physical Execution

Both XIAO physical-effector endpoints continued operating as part of the autonomous fleet.

Physical servo actuation was repeatedly observed during the run.

The firmware retained the execution boundary established during the actuator test series:

    physical execution occurs only after the accepted result path

The autonomous scheduling change therefore affected when an endpoint requested an operation.

It did not move the physical execution decision ahead of provider-controlled acceptance.

Physical observation was intermittent rather than continuous across every transaction.

Accordingly, FLEET-006 does not claim independent observation of every physical actuation represented in the software record.

Intermittent shortened servo travel previously observed in the five-endpoint configuration also remained a physical limitation.

No independent actuator-position, PWM, or command witness was used.

---

## Latency-Degradation Observation

During the sustained autonomous observation, a pronounced latency-degradation condition developed late in the captured window.

The degradation affected multiple endpoint identities.

Authorization correctness remained intact during the observed condition.

The captured FLEET-006 window contained:

    transactions: 2,125
    transactions over 250 ms: 120

Slow transactions were observed across all five endpoint identities.

The largest observed transaction latency in the captured window was:

    5,509 ms

The latency condition occurred in bursts, including multi-endpoint bursts.

This behavior differed materially from the previously observed normal warmed fleet latency.

The condition was therefore treated as a test anomaly and investigated rather than excluded from the record.

---

## Diagnostic Disposition

The latency investigation was used to determine whether the observed degradation could be attributed to an obvious resource, provider, boundary, LAN, or endpoint-runtime failure.

The investigation did not establish an exact internal mechanism.

Observed evidence did not support a simple explanation based solely on:

- Raspberry Pi CPU exhaustion;
- Raspberry Pi memory exhaustion;
- swap exhaustion;
- TCP resource exhaustion;
- persistent provider-processing degradation;
- persistent NUVL boundary-processing degradation;
- general laptop-to-Pi LAN degradation; or
- persistent corrupted runtime state in the continuously operating `esp32-field-01`.

During isolation work, removal of the other fleet endpoints coincided with restoration of normal latency for the continuously operating `esp32-field-01`.

That endpoint was not restarted to obtain the recovery.

Restoring the full five-endpoint autonomous workload did not immediately reproduce the sustained degraded state.

The fault was therefore closed at the observed fault-domain level without assigning an unsupported internal mechanism.

The detailed diagnostic investigation is not required to reproduce the core FLEET-006 autonomous capability and may be retained separately from the primary public fleet evidence.

---

## Correctness During Degradation

The latency event is significant because degraded timing did not produce a corresponding loss of authorization correctness in the captured dataset.

During the primary observation:

    2,125 / 2,125 transactions produced the expected accepted outcome

and:

    2,125 / 2,125 transactions produced provider_admissible

No duplicate run IDs were observed.

This supports a narrow finding:

> Authorization correctness remained intact during the latency degradation observed in the tested NUVL Edge Lab configuration.

It does not establish a deterministic latency guarantee, operational network resilience, tactical-network performance, or a general guarantee that all forms of network degradation preserve application behavior.

---

## Restoration Observation

Following the investigation, the full five-endpoint autonomous workload was restored.

A subsequent observation captured:

    599 transactions
    599 unique run IDs
    0 duplicate run IDs

Decision results:

    599 / 599 accepted
    599 / 599 provider_admissible

Fleet median latency:

    35 ms

Two transactions exceeded 250 ms.

Neither exceeded one second.

The earlier sustained degraded condition did not reproduce during this observation.

---

## Overnight Endurance Observation

The restored autonomous fleet was subsequently operated overnight.

Observation duration:

    7 hours 17 minutes 53 seconds

The captured overnight dataset contained:

    27,080 transactions
    27,080 unique run IDs
    0 duplicate run IDs

Decision results:

    27,080 / 27,080 accepted
    27,080 / 27,080 provider_admissible

Fleet latency:

    minimum: 28 ms
    median: 35 ms
    mean: 35.55 ms
    maximum: 1,080 ms

Transactions over 250 ms:

    5

Transactions over 1,000 ms:

    1

Transactions over 3,000 ms:

    0

Neither XIAO physical-effector endpoint produced a transaction over 250 ms during the captured overnight window.

The earlier sustained latency-degradation condition did not reproduce.

Two brief multi-endpoint slow clusters were observed, but neither developed into the sustained condition seen during the primary FLEET-006 observation.

---

## Endurance Finding

The overnight observation substantially exceeded the primary FLEET-006 window in both elapsed runtime and transaction count without reproducing the earlier sustained degraded state.

The evidence therefore does not support the conclusion that any one of the following alone was sufficient to produce the earlier condition:

- five-endpoint autonomous operation;
- elapsed runtime; or
- accumulated transaction count.

The exact cause of the earlier degradation remains unresolved.

The overnight run is presented as laboratory endurance and correctness evidence.

It is not presented as a deterministic network-performance benchmark.

---

## Supported Findings

FLEET-006 supports the following findings within the tested laboratory configuration:

- five heterogeneous physical endpoints operated concurrently through the same provider-controlled authority path;
- individual endpoints originated their own requests without a central launcher triggering each transaction;
- endpoints operated according to independent local schedules;
- transaction identifiers were generated at the endpoints;
- no duplicate transaction identifiers were observed in the captured sustained or overnight datasets;
- provider-controlled outcomes remained correctly associated with the originating endpoints;
- the two physical-effector endpoints remained part of the autonomous workload;
- physical execution remained downstream of the accepted result path;
- authorization correctness remained intact during the observed sustained latency-degradation event;
- the continuously operating isolated endpoint returned to normal latency without endpoint restart during investigation;
- restoration of the five-endpoint workload did not immediately reproduce the sustained degraded condition; and
- a later overnight observation completed 27,080 unique transactions without reproducing the sustained degradation.

---

## What FLEET-006 Does Not Establish

FLEET-006 does not establish:

- geographically distributed fleet operation;
- independently hosted provider infrastructure;
- independent administrative domains;
- tactical RF performance;
- contested-spectrum performance;
- GPS-denied performance;
- deterministic authorization latency;
- guaranteed latency bounds;
- true parallel processing by the current boundary implementation;
- production fleet scalability;
- production reliability or availability;
- calibrated actuator position;
- identical mechanical stroke for every accepted transaction;
- exactly-once physical execution;
- independent actuator-command witnessing;
- operational UAS or C-UAS integration;
- operational TACOS performance; or
- the internal cause of the observed latency-degradation event.

All findings are bounded to the tested NUVL Edge Lab hardware, firmware, network, provider path, and observation windows.

---

## Evidence Handling

The primary autonomous evidence should remain distinguishable from the diagnostic investigation.

Core publication evidence includes the primary autonomous observation and subsequent restoration/endurance observations.

Diagnostic windows used to investigate the unresolved latency event may be retained separately without treating each diagnostic step as an independent fleet qualification test.

Failures and anomalies are not removed from the technical record merely because they did not reproduce.

The sustained latency event remains part of the FLEET-006 result and is explicitly bounded as unresolved.

---

## Overall Result

**PASS with preserved latency anomaly.**

FLEET-006 demonstrated autonomous asynchronous request generation across the five-endpoint heterogeneous NUVL Edge Lab fleet while preserving expected provider-controlled authorization outcomes and endpoint binding.

The test also exposed a sustained multi-endpoint latency-degradation condition whose exact internal mechanism was not established.

Authorization correctness remained intact during that condition.

Subsequent restored operation and an overnight 27,080-transaction observation did not reproduce the sustained degradation.

The test therefore extends the five-endpoint baseline from coordinated untethered operation to sustained autonomous endpoint-local request generation while preserving the unresolved latency event as part of the evidence record.
