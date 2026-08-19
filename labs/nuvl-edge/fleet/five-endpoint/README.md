# NUVL Edge Fleet — Five-Endpoint Heterogeneous Configuration

This directory contains the five-endpoint heterogeneous fleet tests for the NUVL Edge Lab.

The configuration extends the earlier three-endpoint fleet into a larger physical testbed containing three ESP32-S3 status/load endpoints and two XIAO ESP32-S3 physical-effector endpoints.

The purpose of this series is to evaluate whether provider-controlled authorization, endpoint identity, outcome binding, physical execution, recovery behavior, and autonomous request generation remain correct as the fleet becomes larger and more heterogeneous.

This is a laboratory implementation.

It is not a geographically distributed deployment, tactical network qualification, or production fleet implementation.

---

## Test Classification

The five-endpoint fleet tests are:

**NUVL core — no architecture change.**

The authority path remains:

    endpoint
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
    physical execution when applicable

The fleet tests change the number, type, power arrangement, and request-generation behavior of the endpoints.

They do not transfer provider authority into the endpoints.

---

## Physical Fleet

The tested fleet consists of:

    esp32-field-01
    esp32-s3-02
    esp32-s3-03
    esp32-xiao-servo-01
    esp32-xiao-servo-02

Hardware:

- 3 × ESP32-S3 DevKitC-1 endpoints
- 2 × Seeed XIAO ESP32-S3 endpoints
- 2 × physical servo effectors
- Raspberry Pi 5 boundary/coordinator
- Archer Wi-Fi infrastructure
- separate laptop used as launcher/observer where required

During qualified untethered runtime, the endpoint boards were not connected by USB to the laptop, Chromebook, or Raspberry Pi.

The five endpoints were powered independently from external USB power sources.

---

# FLEET-005 — Untethered Heterogeneous Baseline

FLEET-005 established the initial qualified five-endpoint physical baseline.

The test used coordinated release timing while all five physical endpoints were untethered from controlling hosts.

Launcher:

    run_five_endpoint_accept_archer.py

### Results

    20 / 20 coordinated runs PASS
    100 / 100 endpoint transactions correct
    0 missing results
    0 unavailable results
    0 identity/IP mismatches
    0 outcome mismatches
    0 actuator-report mismatches
    0 late results
    0 stragglers

Observed authorization latency across the campaign:

    minimum: 30 ms
    maximum: 49 ms

Both XIAO servo endpoints physically moved during every qualified run.

### Physical Anomaly

Intermittent shortened servo travel was observed.

The affected servo did not consistently complete the same apparent mechanical stroke, although physical movement was observed and the endpoint reported successful actuator invocation and completion.

The exact mechanical or electrical cause was not isolated.

No independent position, PWM, or actuator-command witness was used.

Accordingly, FLEET-005 supports physical movement following accepted authorization but does not support a calibrated-position, full-stroke, or exactly-once physical-execution claim.

---

## FLEET-005 Supported Result

The tested configuration demonstrated:

> Five untethered heterogeneous ESP32-S3 endpoints participated in a coordinated provider-controlled authorization workload with correct endpoint identity and outcome binding across 100 endpoint transactions, while both physical-effector endpoints produced authorized movement in every qualified run.

FLEET-005 does not establish autonomous endpoint request generation.

That is addressed by FLEET-006.

---

# FLEET-006 — Autonomous Asynchronous Operation

FLEET-006 removed coordinator-controlled release timing from the endpoint request path.

Each endpoint generated its own transaction identifiers and originated authorization requests according to its own local schedule.

The laptop was no longer responsible for triggering individual endpoint requests.

This changes the fleet workload model but does not change the NUVL authority architecture.

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

Endpoint transaction identifiers were generated locally using the endpoint identity, local timing value, and endpoint-local counter.

The XIAO firmware preserved the physical authority boundary:

    physical execution occurs only after an accepted decision

---

# FLEET-006 Primary Sustained Window

The primary sustained autonomous observation captured:

    2,125 transactions
    2,125 unique run IDs
    0 duplicate run IDs
    2,125 accepted
    2,125 provider_admissible

All five endpoint identities were represented.

Both physical-effector endpoints were observed repeatedly actuating during autonomous operation.

Physical observation was intermittent rather than continuous.

Occasional shortened servo swings remained visible, so complete mechanical stroke for every accepted transaction was not established.

---

## Latency-Degradation Observation

The sustained autonomous run developed a pronounced latency-degradation condition late in the observation window.

Authorization correctness remained intact.

The degradation affected multiple endpoint identities and persisted into a subsequent diagnostic observation.

The exact internal mechanism was not identified.

Diagnostic work found no evidence of:

- Raspberry Pi CPU exhaustion
- Raspberry Pi memory exhaustion
- swap exhaustion
- TCP resource exhaustion
- persistent provider/boundary processing degradation
- general laptop-to-Pi LAN degradation
- persistent corrupted runtime state in the continuously operating `esp32-field-01`

Removing other fleet endpoints coincided with recovery of normal latency on `esp32-field-01` without restarting that endpoint.

However, restoring the full five-endpoint workload did not immediately reproduce the degraded state.

The anomaly therefore remains unresolved.

It is preserved as a test finding rather than attributed to a specific component.

---

# FLEET-006-D8 — Five-Endpoint Restoration Run

After the degradation investigation, the full five-endpoint autonomous workload was restored.

Results:

    599 transactions
    599 unique run IDs
    0 duplicate run IDs
    599 / 599 accepted
    599 / 599 provider_admissible

Fleet median:

    35 ms

Only two transactions exceeded 250 ms, both early in the observation window.

The sustained degradation observed earlier did not reproduce during this run.

---

# FLEET-006-D9 — Overnight Endurance

The full autonomous five-endpoint fleet was then left running overnight.

Observation duration:

    7 hours 17 minutes 53 seconds

Results:

    27,080 transactions
    27,080 unique run IDs
    0 duplicate run IDs
    27,080 / 27,080 accepted
    27,080 / 27,080 provider_admissible

Fleet median:

    35 ms

Five transactions exceeded 250 ms.

One exceeded one second.

Neither physical XIAO endpoint exceeded 250 ms during the overnight observation.

The earlier sustained degraded state did not reproduce.

Two brief multi-endpoint latency clusters were observed, but they did not develop into a persistent degraded condition.

---

## FLEET-006 Endurance Finding

The overnight run materially weakened several simple explanations for the earlier degradation.

The previously observed persistent latency state was not reproduced despite substantially greater elapsed runtime and transaction count.

The evidence therefore does not support the conclusion that any one of the following alone was sufficient to cause the earlier degradation:

- five-endpoint autonomous load
- elapsed runtime
- transaction accumulation

The underlying mechanism remains unresolved.

No claim is made that the network was free of latency disturbances.

---

# What the Five-Endpoint Series Demonstrates

The combined five-endpoint testing supports the following laboratory-scale findings:

- five heterogeneous physical endpoints can operate through the same provider-controlled authority path;
- endpoints can operate untethered from controlling hosts;
- endpoint identity and provider outcomes remain correctly bound across the tested fleet;
- physical-effect endpoints execute only after accepted decisions in the tested path;
- mixed endpoint types can coexist in the same fleet;
- autonomous endpoint-local request generation can replace coordinated launcher release timing;
- endpoint-generated transaction identifiers remain unique across sustained operation;
- authorization correctness remained intact during the observed latency-degradation event;
- the fleet recovered from the observed degraded condition without requiring restart of the continuously operating isolated endpoint;
- the restored five-endpoint fleet completed a later overnight endurance run without reproducing the sustained degradation.

---

# What the Five-Endpoint Series Does Not Establish

The current evidence does not establish:

- geographically distributed deployment
- independently hosted provider infrastructure
- tactical RF performance
- contested-spectrum performance
- deterministic authorization latency
- true parallel processing by the current boundary implementation
- calibrated servo position
- full mechanical stroke for every accepted transaction
- exactly-once physical execution
- independently witnessed actuator command
- operational UAS or C-UAS integration
- production reliability or availability
- TACOS operational performance
- the internal cause of the observed latency-degradation event

All results are bounded to the tested NUVL Edge Lab hardware, software, network, and test conditions.

---

# Relationship to the Three-Endpoint Fleet

The original three-endpoint fleet remains separately documented.

The five-endpoint series does not replace that baseline.

It extends the test environment from a three-endpoint fleet into a heterogeneous five-endpoint configuration with physical effectors and autonomous request generation.

Repository organization:

    fleet/
    ├── three-endpoint/
    └── five-endpoint/

Each configuration should retain its own firmware, launcher, procedures, evidence, hashes, results, and limitations so that observed behavior remains traceable to the exact tested configuration.
