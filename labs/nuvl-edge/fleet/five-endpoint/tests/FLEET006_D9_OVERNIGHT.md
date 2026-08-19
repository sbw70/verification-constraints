# FLEET-006-D9 — Five-Endpoint Overnight Endurance

## Purpose

FLEET-006-D9 was an extended endurance observation of the restored five-endpoint autonomous NUVL Edge Lab fleet.

The run followed the earlier FLEET-006 autonomous testing, latency-degradation investigation, and restoration of the full five-endpoint workload.

The primary objectives were to determine whether:

- all five endpoints would continue autonomous endpoint-local request generation over an extended period;
- transaction identifiers would remain unique;
- expected provider-controlled authorization outcomes would remain correct;
- the earlier sustained latency-degradation condition would reproduce with substantially greater runtime and transaction accumulation; and
- any new persistent failure condition would emerge during unattended operation.

FLEET-006-D9 did not introduce a new authority architecture.

It extended the observation period of the existing FLEET-006 autonomous configuration.

---

## Test Classification

**Classification:** NUVL core — no architecture change.

**Use case:** sustained autonomous heterogeneous fleet operation.

**New evidence supported:** the restored five-endpoint autonomous fleet sustained an overnight observation containing 27,080 unique transactions while preserving expected authorization outcomes and without reproducing the earlier sustained latency-degradation condition.

**Not established:** production reliability, operational availability, deterministic latency, tactical-network endurance, geographically distributed operation, or independently hosted provider operation.

---

## Tested Fleet

The autonomous fleet consisted of:

    esp32-field-01
    esp32-s3-02
    esp32-s3-03
    esp32-xiao-servo-01
    esp32-xiao-servo-02

Hardware classes:

- 3 × ESP32-S3 DevKitC-1 status/load endpoints
- 2 × Seeed XIAO ESP32-S3 physical-effector endpoints
- Raspberry Pi 5 boundary/coordinator
- Archer network infrastructure

The endpoints continued using endpoint-local autonomous schedules established for FLEET-006.

---

## Authority Path

The authority path remained unchanged:

    endpoint-local request
             |
             v
       NUVL boundary
             |
             v
    provider-controlled
         decision
             |
             v
       endpoint result
             |
             v
    accepted path only
             |
             v
    physical execution
    where applicable

The extended runtime did not introduce local fallback acceptance or transfer provider authority into the endpoints.

---

## Observation Window

FLEET-006-D9 captured approximately:

    7 hours 17 minutes 53 seconds

of autonomous five-endpoint operation.

The analyzed evidence window was:

    FLEET006_D9_WINDOW.log

The window was extracted from the preserved coordinator log associated with the autonomous fleet run.

---

## Dataset Integrity

The D9 dataset contained:

    parsed transactions: 27,080
    unique run IDs:      27,080
    duplicate run IDs:   0

Decision totals:

    accepted:            27,080
    denied:              0
    other decisions:     0

Reason totals:

    provider_admissible: 27,080

All parsed transactions therefore produced the expected result for this acceptance/endurance workload.

No duplicate transaction identifier was observed in the analyzed window.

---

## Per-Endpoint Results

### esp32-field-01

    transactions:       10,165
    accepted:           10,165
    provider_admissible:10,165

    latency minimum:    29 ms
    latency mean:       36.92 ms
    latency median:     36 ms
    latency maximum:    871 ms

    over 250 ms:        3
    over 1,000 ms:      0
    over 3,000 ms:      0

### esp32-s3-02

    transactions:       7,334
    accepted:           7,334
    provider_admissible:7,334

    latency minimum:    29 ms
    latency mean:       35.56 ms
    latency median:     35 ms
    latency maximum:    1,080 ms

    over 250 ms:        1
    over 1,000 ms:      1
    over 3,000 ms:      0

### esp32-s3-03

    transactions:       4,705
    accepted:           4,705
    provider_admissible:4,705

    latency minimum:    29 ms
    latency mean:       35.46 ms
    latency median:     35 ms
    latency maximum:    993 ms

    over 250 ms:        1
    over 1,000 ms:      0
    over 3,000 ms:      0

### esp32-xiao-servo-01

    transactions:       2,769
    accepted:           2,769
    provider_admissible:2,769

    latency minimum:    29 ms
    latency mean:       32.92 ms
    latency median:     32 ms
    latency maximum:    74 ms

    over 250 ms:        0
    over 1,000 ms:      0
    over 3,000 ms:      0

### esp32-xiao-servo-02

    transactions:       2,107
    accepted:           2,107
    provider_admissible:2,107

    latency minimum:    28 ms
    latency mean:       32.60 ms
    latency median:     32 ms
    latency maximum:    82 ms

    over 250 ms:        0
    over 1,000 ms:      0
    over 3,000 ms:      0

---

## Fleet-Level Results

Across all five endpoints:

    transactions:       27,080
    accepted:           27,080
    denied:             0
    other decisions:    0

    latency minimum:    28 ms
    latency mean:       35.55 ms
    latency median:     35 ms
    latency maximum:    1,080 ms

    over 250 ms:        5
    over 1,000 ms:      1
    over 3,000 ms:      0

The latency figures describe only the tested NUVL Edge Lab configuration and observation window.

They are not deterministic latency guarantees or TACOS/network-performance claims.

---

## Slow-Transaction Analysis

Five transactions exceeded 250 ms during the 27,080-transaction observation.

They were:

    1,080 ms — esp32-s3-02
      993 ms — esp32-s3-03
      871 ms — esp32-field-01
      655 ms — esp32-field-01
      269 ms — esp32-field-01

Neither physical XIAO endpoint produced a transaction over 250 ms during the analyzed overnight window.

The slow transactions were concentrated in the three DevKit endpoints.

---

## Multi-Endpoint Clustering

Latency-cluster analysis identified three slow bursts.

Two contained consecutive slow transactions from more than one endpoint.

Observed multi-endpoint clusters included:

    esp32-field-01 + esp32-s3-03
    maximum observed latency: 993 ms

and:

    esp32-field-01 + esp32-s3-02
    maximum observed latency: 1,080 ms

These were brief events.

They did not develop into the sustained multi-endpoint degraded state observed during the earlier FLEET-006 autonomous window.

The presence of brief clusters is retained as part of the evidence.

No claim is made that the overnight network was free of latency disturbances.

---

## Comparison With Earlier FLEET-006 Degradation

The earlier primary FLEET-006 autonomous window contained:

    2,125 transactions
    120 transactions over 250 ms

and developed a sustained multi-endpoint latency-degradation condition.

FLEET-006-D9 contained:

    27,080 transactions
    5 transactions over 250 ms

while running substantially longer.

The earlier persistent degraded condition did not reproduce.

This comparison is useful for fault characterization, but it does not identify the original mechanism.

The D9 evidence weakens simple explanations based solely on:

- five-endpoint autonomous operation;
- elapsed runtime; or
- accumulated transaction count.

Each of those conditions was present to a substantially greater degree during D9 without reproducing the earlier sustained state.

The underlying cause of the original degradation remains unresolved.

---

## Physical-Endpoint Observation

The two XIAO servo endpoints remained active members of the autonomous fleet throughout the analyzed dataset.

Their software records contained:

    esp32-xiao-servo-01: 2,769 accepted transactions
    esp32-xiao-servo-02: 2,107 accepted transactions

Neither produced an analyzed transaction above 250 ms.

FLEET-006-D9 was an unattended endurance observation.

Continuous independent visual or instrumented verification of physical servo movement was not performed for every accepted transaction.

The transaction counts therefore establish software-recorded accepted participation by the physical-effector endpoints.

They do not establish independently witnessed physical movement for all 4,876 accepted XIAO transactions.

Physical execution behavior is supported separately by the dedicated actuator tests and observed five-endpoint fleet testing.

---

## Supported Findings

Within the tested NUVL Edge Lab configuration, FLEET-006-D9 supports the following findings:

- all five autonomous endpoints remained represented in the overnight dataset;
- 27,080 transactions were parsed;
- all 27,080 transaction identifiers were unique;
- no duplicate run ID was observed;
- all 27,080 transactions produced the expected accepted decision;
- all 27,080 transactions recorded `provider_admissible`;
- the fleet median authorization latency was 35 ms in the analyzed window;
- five transactions exceeded 250 ms;
- one transaction exceeded one second;
- no transaction exceeded three seconds;
- neither XIAO physical-effector endpoint exceeded 250 ms;
- brief multi-endpoint latency clusters occurred;
- the earlier sustained latency-degradation condition did not reproduce; and
- substantially greater runtime and transaction accumulation alone were insufficient to reproduce the earlier sustained condition in this observation.

---

## Limitations

FLEET-006-D9 does not establish:

- deterministic authorization latency;
- guaranteed latency bounds;
- production reliability;
- operational availability;
- TACOS Ao >= 0.999;
- tactical-network endurance;
- contested-spectrum performance;
- RF-jammed performance;
- GPS-denied performance;
- geographically distributed operation;
- independently hosted provider infrastructure;
- independent administrative domains;
- production fleet scalability;
- true parallel processing by the current boundary implementation;
- independently witnessed physical execution for every XIAO transaction;
- calibrated servo position;
- exactly-once physical execution;
- operational UAS or C-UAS integration; or
- the cause of the earlier FLEET-006 latency-degradation event.

The absence of a reproduced sustained degradation during D9 does not prove that the condition cannot recur.

All findings are bounded to the tested hardware, firmware, network, provider path, and analyzed observation window.

---

## Evidence

Primary analyzed window:

    FLEET006_D9_WINDOW.log

Analysis scripts:

    fleet006_d9_analyze.py
    fleet006_d9_latency_clusters.py

Preserved source log:

    coordinator_restore_20260730_230109.log

Where retained, start/end markers should be preserved with the evidence package to document the extraction boundary for the D9 observation.

---

## Result

**PASS — with brief latency outliers preserved.**

FLEET-006-D9 completed an overnight autonomous five-endpoint observation containing 27,080 unique transactions.

All 27,080 transactions produced the expected provider-controlled accepted outcome.

No duplicate run IDs were observed.

Five transactions exceeded 250 ms, including one transaction of 1,080 ms. Brief multi-endpoint latency clustering occurred, but the earlier sustained FLEET-006 degradation did not reproduce.

The result provides extended laboratory endurance and authorization-correctness evidence for the five-endpoint autonomous configuration while preserving the observed latency outliers and the unresolved status of the earlier degradation.
