# Five-Endpoint Fleet Evidence

This directory contains retained evidence from the five-endpoint NUVL Edge Lab fleet test series.

The five-endpoint configuration consists of:

- three ESP32-S3 DevKitC-1 status/load endpoints; and
- two Seeed XIAO ESP32-S3 physical-effector endpoints.

Depending on the test condition, endpoints may operate independently, generate requests according to endpoint-local schedules, exercise different authorization outcomes, or experience deliberately introduced fault conditions.

All tests remain subject to the documented NUVL authority path for the applicable test configuration.

The directory contains preserved observation windows, test-boundary markers, analysis utilities, and related artifacts supporting results documented under:

```text
../tests/
```

---

## Evidence Scope

Evidence retained here may support tests involving:

- untethered five-endpoint operation;
- autonomous asynchronous request generation;
- sustained fleet operation;
- endpoint-local workload variation;
- mixed authorization outcomes;
- repeated unauthorized activity;
- participant fault isolation;
- authority-path unavailability;
- recovery following authority-path restoration;
- endpoint disconnect and reconnect behavior;
- endpoint restart or reboot behavior;
- malformed, stale, or replay-related request handling;
- shared-boundary load conditions;
- physical-effector authorization behavior; and
- other documented five-endpoint test conditions.

Evidence artifacts support only the findings established by their corresponding test documentation.

---

## Evidence Organization

A test evidence set may include:

- START and END markers defining an observation window;
- phase or transition markers where required;
- extracted coordinator or boundary logs;
- analysis utilities;
- transaction counts;
- endpoint participation records;
- authorization decisions and reasons;
- transaction-identifier uniqueness checks;
- latency observations;
- failure and error searches; and
- other test-specific artifacts identified by the corresponding test document.

Not every test requires every artifact type.

Extracted windows are retained where practical so reported results can be traced to the underlying transaction record without publishing unrelated laboratory logs.

---

## Test Documentation

The corresponding files under:

```text
../tests/
```

define the applicable:

- test classification;
- objective;
- configuration;
- procedure;
- PASS criteria;
- observed results;
- supported claim;
- limitations; and
- evidence references.

Where a test contains multiple operational phases, the retained evidence identifies the relevant boundaries where necessary.

Example:

```text
normal operation
->
introduced fault
->
faulted operation
->
restoration
->
recovered operation
```

---

## Evidence Interpretation

The evidence supports narrow laboratory findings from specifically documented test conditions.

Depending on the test, retained evidence may demonstrate that the five-endpoint configuration:

- operated without endpoint runtime USB tethering;
- generated requests autonomously;
- maintained endpoint identity and result binding;
- generated unique transaction identifiers;
- remained subject to provider-controlled authorization;
- produced expected endpoint-specific authorization outcomes;
- continued operating while another participant experienced a different authorization or workload condition;
- failed closed when the applicable authority path was unavailable;
- recovered following authority-path restoration;
- preserved authorization correctness during measured latency variation; or
- sustained operation over an extended observation period.

Results from one test condition do not establish behavior under untested fault modes, workloads, deployment environments, or fleet sizes.

---

## Physical Execution

Two endpoints in the five-endpoint fleet are connected to physical servo actuators.

Five-endpoint tests may therefore include physical-effector participants.

Coordinator and boundary evidence records software-observed endpoint participation, authorization decisions, reasons, and timing.

Unless a test includes an independent physical witness, those records are not independent proof of every actuator movement.

Dedicated actuator tests and test-specific observations provide the applicable physical-execution evidence.

An accepted software result alone does not establish exactly-once physical execution.

---

## Latency and Availability

Latency values retained in this directory are observations from specific laboratory configurations and measured windows.

They are not deterministic timing guarantees.

Material latency anomalies, timeouts, unavailable results, recovery events, or other abnormal conditions remain part of the technical record even when later tests do not reproduce them.

Where an internal cause has not been established, that limitation remains explicitly documented.

---

## Diagnostic Material

Additional diagnostic observations may be produced during fault isolation or investigation.

Intermediate diagnostic artifacts are not necessarily included when they are not required to support a published test result.

Material failures, anomalies, and unresolved conditions remain documented regardless of whether every intermediate diagnostic artifact is published.

---

## Publication Boundary

Public evidence excludes unnecessary local deployment information, including:

- Wi-Fi credentials;
- private local credentials;
- environment-specific secrets;
- unnecessary internal addressing;
- machine-specific filesystem paths; and
- unrelated laboratory configuration.

When an artifact is modified for publication, the publication copy receives its own SHA-256 digest.

A sanitized or otherwise modified artifact does not retain the digest of the original collected or tested artifact.

Where relevant, test documentation distinguishes between:

- the original collected or tested artifact; and
- the sanitized publication derivative.

---

## Integrity

Published evidence artifacts are tracked using SHA-256 digests in:

```text
SHA256SUMS.txt
```

Each digest applies to the exact published file identified by that entry.

Any modification to a published artifact requires recalculation of its SHA-256 digest.

Original tested-source hashes may also be retained in corresponding test documentation where necessary to preserve provenance.

---

## Evidence Boundary

These files represent laboratory evidence from documented NUVL Edge Lab five-endpoint tests.

They are provided to preserve traceability between reported findings and the underlying observation record.

They are not presented as:

- certification evidence;
- operational qualification;
- proof of arbitrary fleet scalability;
- proof of geographically distributed operation;
- proof of deterministic latency;
- proof of tactical-network performance;
- proof of arbitrary Byzantine or hostile-client tolerance;
- proof of resistance to every denial-of-service condition; or
- proof of performance outside the documented laboratory configuration.

Broader claims require separate evidence.
