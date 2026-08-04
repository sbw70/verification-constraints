# NUVL Edge Lab

NUVL Edge Lab is a physical test environment for evaluating provider-controlled validation and bounded authority on low-resource endpoints.

The laboratory uses three ESP32-S3 devices, a Raspberry Pi verification boundary, local wireless infrastructure, and a Windows control host. The tests examine whether constrained endpoints can request and display provider decisions without independently acquiring reusable authorization authority.

The repository contains curated source, test procedures, and evidence from the tested paths. It is not a dump of the original development directory.

## What This Lab Demonstrates

The current test set covers:

- Three physical endpoints using one shared verification boundary
- Per-device identity, decision, and reason binding
- Mixed accepted and denied outcomes in the same fleet run
- Fail-closed behavior when a verification path is unavailable
- Recovery after endpoint-specific and shared-boundary faults
- Provider-issued authority bounded for disconnected use
- Replay rejection across process restart and power loss
- Exactly one successful exercise under overlapping attempts
- Commit-before-accept behavior during an injected crash
- Recovery when a crash occurs before atomic state replacement

The central architectural distinction is:

> The endpoint may request, observe, display, or act on a bounded result, but it does not independently create, enlarge, or reuse provider authority.

## Laboratory Architecture

The original fleet path is:

```text
Three ESP32-S3 endpoints
        |
        | outbound HTTP polling
        v
Raspberry Pi fleet coordinator
        |
        | mode assignment and relative wait_ms
        v
ESP32-S3 request generation
        |
        | POST /nuvl
        v
Raspberry Pi verification boundary
        |
        | decision and reason
        v
ESP32-S3 result report
        |
        v
Fleet launcher validates:
identity + IP + decision + reason + timing
```

Primary services:

| Port | Service |
|---:|---|
| `8089` | NUVL verification boundary |
| `19052` | Fleet coordinator |

The original Raspberry Pi boundary uses Python `HTTPServer` and is single-threaded. The fleet tests demonstrate coordinated fan-in through a shared boundary. They do not claim parallel execution inside that boundary.

## Repository Structure

```text
labs/nuvl-edge/
├── README.md
├── .gitignore
│
├── fleet/
│   ├── README.md
│   ├── baseline/
│   └── archer-validation/
│
├── disconnected-authority/
│   ├── README.md
│   ├── poc003-single-use/
│   ├── poc004b-power-loss/
│   ├── poc005-double-spend/
│   ├── poc006a-commit-before-accept/
│   └── wp2-t1-pre-replace/
│
└── evidence/
    ├── README.md
    └── SHA256SUMS.txt
```

### [`fleet/`](fleet/)

Contains the three-endpoint fleet implementation and later fault-isolation variants.

Start with [`fleet/baseline/`](fleet/baseline/) for the original supported fleet path.

### [`disconnected-authority/`](disconnected-authority/)

Contains the client sequences, procedures, and evidence for bounded disconnected use, replay prevention, power-loss persistence, overlapping attempts, and crash-window testing.

Some verification-boundary implementations are intentionally withheld from the current public release. Each affected test folder identifies what is included, what is withheld, and what interface behavior is required.

### [`evidence/`](evidence/)

Contains selected logs, manifests, and hashes supporting specific test claims.

Raw development output, generated state, credentials, private keys, and unrelated terminal captures are not part of the public evidence set.

## Start Here: Original Fleet Baseline

The original pre-latency-investigation fleet implementation uses:

```text
nuvl_local_hardened.py
multi_endpoint_coordinator_v2.py
esp32_multi_poll_main_v2.py
esp32_multi_once.py
run_three_esp32_poll.py
run_three_esp32_mixed.py
```

Each ESP32 contains:

```text
main.py
device_id.txt
```

`main.py` is the deployed ESP32 firmware.

The confirmed endpoint identities are:

```text
esp32-field-01
esp32-s3-02
esp32-s3-03
```

Public examples are stored separately so the three files do not overwrite one another:

```text
fleet/baseline/endpoint-config/
├── esp32-field-01/device_id.txt
├── esp32-s3-02/device_id.txt
└── esp32-s3-03/device_id.txt
```

COM port numbers are bench-specific and are not durable endpoint identities.

## Baseline Reproduction Path

A reproducer should begin with the baseline before attempting outage, isolation, persistence, or crash-injection tests.

### 1. Prepare the Raspberry Pi

Run the verification boundary:

```text
nuvl_local_hardened.py
```

Run the fleet coordinator:

```text
multi_endpoint_coordinator_v2.py
```

The coordinator uses relative `wait_ms` values. This replaced an earlier absolute-timestamp design that failed because Raspberry Pi Python and MicroPython represented epochs differently.

### 2. Prepare Each ESP32-S3

Copy the fleet firmware to each board as:

```text
main.py
```

Copy the board-specific identity as:

```text
device_id.txt
```

The firmware:

- Reads the endpoint identity from `device_id.txt`
- Polls the Raspberry Pi coordinator over outbound HTTP
- Receives a test mode and relative release delay
- Posts its request to `/nuvl`
- Reports the result to the coordinator
- Displays the outcome through the onboard RGB LED

LED states:

| LED | Meaning |
|---|---|
| Blue | Ready or idle |
| Yellow | Request created |
| Purple | Verification pending |
| Green | Accepted |
| Red | Denied |
| Orange | Stale, replay, or malformed denial |
| White | Network, provider, boundary, or execution unavailable |

### 3. Run the Three-Accept Baseline

Launcher:

```text
run_three_esp32_poll.py
```

Expected binding:

```text
esp32-field-01 -> accepted / provider_admissible
esp32-s3-02    -> accepted / provider_admissible
esp32-s3-03    -> accepted / provider_admissible
```

Recorded successful run:

```text
run_id=18c565fc0e9dfd5c
responses=3/3
accepted=3
identity_or_ip_mismatch=0
elapsed=33–34 ms
result=PASS
```

PASS requires:

- Three expected endpoint responses
- Correct endpoint identities
- Correct endpoint IP bindings
- Three accepted outcomes
- No missing result
- No cross-assigned result

### 4. Run the Mixed-Outcome Test

Launcher:

```text
run_three_esp32_mixed.py
```

Expected binding:

```text
esp32-field-01 -> accepted / provider_admissible
esp32-s3-02    -> denied / unauthorized_request
esp32-s3-03    -> denied / stale_replay_malformed
```

Recorded successful run:

```text
run_id=18c5b11e874cd4cc
responses=3/3
accepted=1
denied=2
identity_or_ip_mismatch=0
elapsed=29–38 ms
result=PASS
```

This is the stronger fleet test because aggregate counts cannot earn PASS. Each decision and reason must remain bound to the correct physical endpoint.

## Test Catalog

| Test | Location | Result | Property exercised |
|---|---|---|---|
| Three-endpoint baseline | [`fleet/baseline/`](fleet/baseline/) | PASS | Correct identity and result binding |
| Mixed fleet outcomes | [`fleet/baseline/`](fleet/baseline/) | PASS | Different outcomes remain bound to the correct devices |
| Single-endpoint diagnostic | [`fleet/baseline/`](fleet/baseline/) | PASS | Individual board, Wi-Fi, and boundary-path validation |
| Single-endpoint isolation | [`fleet/archer-validation/`](fleet/archer-validation/) | PASS | One unavailable endpoint does not corrupt the other results |
| Single-endpoint restoration | [`fleet/archer-validation/`](fleet/archer-validation/) | PASS | The isolated endpoint resumes participation |
| Shared-boundary outage | [`fleet/archer-validation/`](fleet/archer-validation/) | PASS | All endpoints fail unavailable with zero accepted action |
| Shared-boundary recovery | [`fleet/archer-validation/`](fleet/archer-validation/) | PASS with anomaly | Services recover; one endpoint required reset for timely participation |
| POC003 | [`disconnected-authority/poc003-single-use/`](disconnected-authority/poc003-single-use/) | PASS | Bounded disconnected single use |
| POC004B | [`disconnected-authority/poc004b-power-loss/`](disconnected-authority/poc004b-power-loss/) | PASS | Completed commit survives abrupt Raspberry Pi power loss |
| POC005 | [`disconnected-authority/poc005-double-spend/`](disconnected-authority/poc005-double-spend/) | PASS | Competing attempts produce exactly one acceptance |
| POC006A | [`disconnected-authority/poc006a-commit-before-accept/`](disconnected-authority/poc006a-commit-before-accept/) | PASS | Crash after commit and before response remains replay-denied |
| WP2-T1 | [`disconnected-authority/wp2-t1-pre-replace/`](disconnected-authority/wp2-t1-pre-replace/) | PASS | Crash before atomic replacement does not falsely consume the artifact |

The earlier POC004 process-restart test remains documented but is not yet presented as a complete reproduction package because the exact boundary version has not been tied conclusively to the recorded run.

## Disconnected-Authority Test Sequence

### POC003 — Bounded Single Use

POC003 exercises provider-issued authority during provider disconnection.

The tested matrix includes:

- Valid bounded offline exercise
- Replay rejection
- Context mismatch
- Action mismatch
- Nonce mismatch
- Device mismatch
- Tampering
- Unsigned material
- Expired material
- Missing artifact

Best last-known end-to-end client:

```text
poc003_esp32_spend_v2_housewifi.py
```

Two provider variants exist in the original working set. The test-folder documentation identifies the version selected for public reproduction.

### POC004B — Power-Loss Persistence

POC004B tests whether completed spent-state remains effective after abrupt Raspberry Pi power loss.

Observed property:

> A completed persistent-state commit remained effective after power loss, and the spent artifact remained unavailable for reuse after restart.

The restoration sequence eventually returned the three-endpoint fleet to normal operation. One endpoint required reset before timely participation resumed. That anomaly is retained in the evidence record.

### POC005 — Overlapping Attempts

POC005 submits overlapping attempts against one single-use artifact.

Observed property:

> Exactly one attempt succeeded and no duplicate acceptance occurred.

This test does not claim mathematically simultaneous execution. It demonstrates single-use enforcement under near-concurrent competing attempts.

### POC006A — Crash After Commit

POC006A injects a crash after persistent commit but before the response is returned.

Observed property:

> The missing response did not permit the committed artifact to be accepted again.

### WP2-T1 — Crash Before Replacement

WP2-T1 injects a crash before atomic replacement of persistent state.

Observed property:

> The interrupted replacement did not falsely consume the artifact. The commit could be retried after restart, after which replay remained denied.

The tested boundary was identified by:

```text
wp2_t1_pre_replace_boundary_archer.py
SHA-256:
87351DBDF539E0E44480B28B205AE04FAD796D9C60DA9C4084FDEFDA49A9BFC8
```

Do not substitute:

```text
wp2_t1_temp_fsync_boundary_archer.py
```

That similarly named file has different contents and was not the tested boundary.

## Publication Boundary

Some verification-boundary source files are intentionally withheld because they may expose mechanism-level implementation details involving persistence order, crash handling, or atomic replacement.

A withheld boundary does not prevent evaluation of the documented test.

The corresponding public test packages may include:

- Client sequence
- Boundary interface
- Request and response structure
- Failure-injection procedure
- Expected result
- PASS criteria
- Observed result
- Evidence
- Source and evidence hashes
- Known limitations

Where a boundary is withheld, the test-folder README states that directly.

This is an intentional publication decision, not a missing-file error.

## Source and Evidence Integrity

The repository distinguishes three source classes:

1. **Original tested source**  
   The exact file used in the recorded test.

2. **Sanitized public derivative**  
   A copy modified to remove credentials, private values, or environment-specific configuration.

3. **Rerun-confirmed public source**  
   A sanitized or reorganized public copy that was executed again and confirmed against its documented PASS criteria.

A sanitized derivative is not byte-identical to the original tested source.

Do not attach an original tested hash to a modified public copy.

Each published derivative receives its own SHA-256 in [`evidence/SHA256SUMS.txt`](evidence/SHA256SUMS.txt), labeled according to its source class.

Example:

```text
# Sanitized public derivative — not byte-identical to tested source
<sha256>  fleet/baseline/firmware/esp32_multi_poll_main_v2.py
```

## Network Configuration

Public source should use explicit configuration placeholders:

```python
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"
PI_IP = "YOUR_PI_IP"
```

The original bench used:

```text
SSID: GL-MT300N-V2-94f
Raspberry Pi: 192.168.8.234
```

Those values describe the tested environment and are not expected to work unchanged in another laboratory.

Changing credentials, addresses, persistence paths, timing parameters, or source structure creates a different source version. A modified public copy should be rerun before being represented as equivalent to the historical tested source.

## Evidence

The evidence directory contains selected material supporting specific claims.

Curated evidence may include:

- Terminal logs
- Test manifests
- Source hashes
- Evidence hashes
- Run identifiers
- Expected and observed results
- Documented anomalies
- Recovery confirmation

Generated authority artifacts, private keys, runtime spent-state, crash markers, PID files, caches, and unrelated development logs are excluded from the public source tree by default.

See [`evidence/README.md`](evidence/README.md) for the evidence index and verification procedure.

## Known Development Failures

The supported implementation resulted from several failed or superseded approaches:

- Concurrent Windows `mpremote` control was unreliable across three serial ports.
- Improved subprocess capture did not correct the concurrent serial-control problem.
- Inbound UDP triggering was unreliable through the tested access-point path.
- The original coordinator used an incompatible absolute timestamp across Raspberry Pi Python and MicroPython.
- Relative `wait_ms` coordination corrected the cross-epoch timing defect.
- An early mixed-outcome launcher used an all-accept PASS oracle and incorrectly reported FAIL despite correct endpoint outcomes.

The corrected mixed launcher requires per-device identity, decision, and reason matching.

The earlier oracle failure is preserved as a harness failure rather than being misclassified as an architectural failure:

```text
run_id=18c5b0a38b1d51b0
system outcomes=correct
launcher result=FAIL
cause=all-accept PASS oracle
classification=harness/oracle failure
```

## Wireless Latency Incident

A later synchronized latency event was isolated through a controlled comparison between the Mango access-point path and house Wi-Fi.

House-Wi-Fi comparison:

```text
13/13 runs PASS
39/39 endpoint transactions correct
33–147 ms observed endpoint latency
approximately 49.9 ms mean
41.5 ms median
zero reproduction of the synchronized approximately 900 ms event
```

Disposition:

- The incident is closed at the fault-domain level.
- The access-point-specific wireless path was isolated.
- The exact internal Mango mechanism remains unresolved.
- No specific driver function or hardware defect is claimed.
- The degraded Mango event is engineering incident evidence, not the normal product baseline.

## Limitations and Open Work

The current results should not be interpreted as proving behavior outside the tested paths.

Items not yet demonstrated include:

- Additional persistence crash points outside the POC006A and WP2-T1 windows
- Startup with corrupt, truncated, or structurally invalid persistent state
- Recovery after persistent-state corruption is detected
- Cross-process or multi-boundary contention beyond the tested in-process serialization path
- Long-duration repeated power-cycle campaigns
- Independent reproduction by an external laboratory
- Generalization of latency results to other access points, firmware versions, or radio environments

These limitations are part of the engineering record and will be updated as additional testing is completed.

## Reproduction Notes

Each test-folder README provides the test-specific information needed to reproduce or evaluate that case:

- Purpose
- Invariant or property tested
- Included files
- Withheld components, when applicable
- Topology and ports
- Preconditions
- Required configuration
- Execution sequence
- Expected outcome
- Observed outcome
- PASS criteria
- Limitations
- Known setup incidents
- Evidence names and hashes

Begin with the original fleet baseline before attempting the disconnected-authority or crash-injection tests.
