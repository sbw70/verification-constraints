# Five-Endpoint Fleet Evidence

This directory contains the primary evidence retained for the five-endpoint autonomous NUVL Edge Lab fleet tests.

The evidence supports the FLEET-006 autonomous asynchronous test series and its subsequent restoration and overnight endurance observations.

The five-endpoint configuration consisted of:

- three ESP32-S3 DevKitC-1 status/load endpoints; and
- two Seeed XIAO ESP32-S3 physical-effector endpoints.

The endpoints independently generated requests according to endpoint-local schedules while remaining subject to the same provider-controlled authority path.

This directory contains preserved observation windows, observation-boundary markers, and the analysis utilities used to derive the reported results.

---

## Evidence Scope

The public evidence set focuses on three primary observation windows:

### FLEET-006 Autonomous Observation

The initial sustained autonomous five-endpoint observation.

This window established endpoint-local asynchronous request generation across the heterogeneous fleet.

The observation also captured a sustained latency-degradation condition.

Authorization outcomes remained correct during the observed degradation.

The exact internal cause of the latency condition was not established.

### FLEET-006-D8 Restoration Observation

A subsequent observation after diagnostic isolation and restoration of the full five-endpoint autonomous workload.

The earlier sustained latency-degradation condition did not reproduce during this window.

D8 is retained as restoration evidence rather than as proof that the earlier condition was permanently resolved.

### FLEET-006-D9 Overnight Endurance Observation

An extended overnight observation of the restored five-endpoint autonomous fleet.

The analyzed window covered approximately 7 hours 18 minutes and contained 27,080 unique transactions.

All 27,080 transactions produced the expected provider-controlled authorization outcome.

The earlier sustained latency-degradation condition did not reproduce.

Brief latency outliers remained present and are preserved in the evidence.

---

## Evidence Organization

Each primary observation may include:

- a START marker defining the beginning of the analyzed window;
- an END marker defining the end of the analyzed window;
- the extracted log corresponding to that window; and
- an analysis utility used to derive transaction counts, endpoint participation, decision outcomes, uniqueness, and timing observations.

The extracted windows are retained so reported results can be traced to the underlying transaction record without requiring publication of unrelated laboratory logs.

---

## Evidence Interpretation

The evidence is intended to support narrow laboratory findings.

It demonstrates that the tested five-endpoint configuration:

- operated autonomously using endpoint-local request generation;
- maintained endpoint identity and result binding;
- generated unique transaction identifiers across the analyzed windows;
- remained subject to provider-controlled authorization;
- preserved expected authorization outcomes during the observed autonomous runs; and
- sustained an extended overnight workload after restoration of the full fleet.

The evidence does not establish:

- geographically distributed operation;
- independently hosted provider infrastructure;
- tactical-network performance;
- deterministic latency;
- guaranteed availability;
- production fleet scalability;
- operational UAS or C-UAS performance; or
- the internal cause of the observed FLEET-006 latency-degradation condition.

---

## Physical Execution

Two endpoints in the five-endpoint fleet were connected to physical servo actuators.

Physical execution behavior is documented by the dedicated actuator test series and the five-endpoint test documentation.

The autonomous evidence logs establish participation and authorization outcomes for those endpoints.

They should not be interpreted as independent physical witnesses of every actuator movement.

---

## Diagnostic Material

Additional diagnostic observations were performed while investigating the FLEET-006 latency-degradation condition.

Those intermediate diagnostic windows are not required to reproduce the primary five-endpoint capability findings and are not included in this evidence directory.

Their exclusion does not change the disposition of the observed anomaly.

The sustained latency-degradation event remains part of the technical record, and its exact internal mechanism remains unresolved.

---

## Evidence Boundary

These files represent laboratory evidence from the tested NUVL Edge Lab configuration.

They are provided to make the reported five-endpoint results inspectable and reproducible at the evidence-analysis level.

They are not presented as certification evidence, operational qualification, or proof of performance outside the documented laboratory environment.
