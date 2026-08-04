# NUVL Edge Fleet

This directory contains the multi-endpoint NUVL Edge Lab tests.

The fleet consists of three physical ESP32-S3 endpoints using one Raspberry Pi coordinator and one shared NUVL verification boundary. The tests evaluate whether endpoint identity, requested mode, decision, denial reason, timing, and recovery behavior remain correctly bound when multiple constrained devices operate through the same path.

The fleet work demonstrates that endpoint capability and execution authority can remain separate:

> Each endpoint can create a request, receive a provider-bound result, and display that result without independently creating or retaining provider authority.

## What the Fleet Tests Cover

The current fleet test set includes:

- Three physical ESP32-S3 endpoints
- One shared Raspberry Pi verification boundary
- Coordinated near-concurrent request release
- Three accepted outcomes in one run
- Mixed accepted and denied outcomes in one run
- Per-device decision and reason binding
- Missing-endpoint isolation
- Endpoint restoration
- Shared-boundary outage
- Shared-boundary recovery
- Stage-level latency measurement
- Wireless-path comparison
- Fail-unavailable behavior without fallback acceptance

The tests do not claim that the Raspberry Pi boundary processes requests in parallel. The original boundary uses Python `HTTPServer` and is single-threaded.

The demonstrated property is coordinated fleet behavior through one shared boundary, not parallel execution inside the boundary.

## Fleet Architecture

```text
Windows control host
        |
        | starts the fleet launcher
        v
Raspberry Pi fleet coordinator
        |
        | assigns run_id, mode, and relative wait_ms
        v
Three ESP32-S3 endpoints
        |
        | create and submit provider-bound requests
        v
Raspberry Pi NUVL verification boundary
        |
        | returns decision and reason
        v
ESP32-S3 endpoints
        |
        | report result to coordinator
        v
Fleet launcher validates:
device identity
endpoint IP
decision
reason
latency
missing or late results
```

Primary services:

| Port | Service |
|---:|---|
| `8089` | NUVL verification boundary |
| `19052` | Fleet coordinator |

## Physical Endpoints

The fleet uses three ESP32-S3 devices:

```text
esp32-field-01
esp32-s3-02
esp32-s3-03
```

Each endpoint stores its durable identity in:

```text
device_id.txt
```

The firmware is deployed to each board as:

```text
main.py
```

The public identity examples are stored as:

```text
baseline/endpoint-config/
├── esp32-field-01/device_id.txt
├── esp32-s3-02/device_id.txt
└── esp32-s3-03/device_id.txt
```

COM port assignments are temporary bench mappings and are not durable identities.

A recorded Windows mapping was:

```text
COM5  -> esp32-field-01
COM9  -> esp32-s3-02
COM12 -> esp32-s3-03
```

Those COM numbers may change after reconnect, reboot, driver changes, or moving the devices to different USB ports.

## Directory Structure

```text
fleet/
├── README.md
│
├── baseline/
│   ├── README.md
│   ├── boundary/
│   ├── coordinator/
│   ├── firmware/
│   ├── launchers/
│   └── endpoint-config/
│
└── archer-validation/
    └── README.md
```

### [`baseline/`](baseline/)

Contains the original pre-latency-investigation fleet implementation.

This is the correct starting point for understanding or reproducing the fleet path.

### [`archer-validation/`](archer-validation/)

Contains later environment-specific validation for:

- Stage-level timing
- Single-endpoint isolation
- Single-endpoint restoration
- Shared-boundary outage
- Shared-boundary recovery
- House-Wi-Fi comparison
- Access-point fault-domain isolation

These files are validation extensions. They are not substitutes for the original fleet baseline.

## Original Fleet Baseline

The original supported fleet implementation consists of:

```text
nuvl_local_hardened.py
multi_endpoint_coordinator_v2.py
esp32_multi_poll_main_v2.py
esp32_multi_once.py
run_three_esp32_poll.py
run_three_esp32_mixed.py
```

Recommended placement:

```text
baseline/
├── README.md
├── boundary/
│   └── nuvl_local_hardened.py
├── coordinator/
│   └── multi_endpoint_coordinator_v2.py
├── firmware/
│   ├── esp32_multi_poll_main_v2.py
│   └── esp32_multi_once.py
├── launchers/
│   ├── run_three_esp32_poll.py
│   └── run_three_esp32_mixed.py
└── endpoint-config/
    ├── esp32-field-01/device_id.txt
    ├── esp32-s3-02/device_id.txt
    └── esp32-s3-03/device_id.txt
```

## File Roles

| File | Role |
|---|---|
| `nuvl_local_hardened.py` | Shared Raspberry Pi verification boundary |
| `multi_endpoint_coordinator_v2.py` | Assigns run state, endpoint mode, and relative release timing |
| `esp32_multi_poll_main_v2.py` | Main fleet firmware for each ESP32-S3 |
| `esp32_multi_once.py` | Single-endpoint diagnostic client |
| `run_three_esp32_poll.py` | Three-endpoint accepted-outcome launcher |
| `run_three_esp32_mixed.py` | Three-endpoint mixed-outcome launcher |
| `device_id.txt` | Durable identity for one physical endpoint |

## Coordinator Timing

The supported coordinator uses:

```text
wait_ms
```

This is a relative delay assigned to each endpoint.

An earlier coordinator used an absolute timestamp. That failed because Raspberry Pi Python and MicroPython did not use compatible epoch representations.

The corrected sequence is:

```text
coordinator assigns relative wait_ms
endpoint receives wait_ms
endpoint waits locally
endpoint submits request
```

The original absolute-time coordinator and endpoint firmware are superseded.

## Endpoint Firmware Behavior

The baseline ESP32 fleet firmware:

1. Reads `device_id.txt`
2. Connects to Wi-Fi
3. Polls the coordinator over outbound HTTP
4. Receives a `run_id`, requested mode, and `wait_ms`
5. Waits for the relative release interval
6. Creates the request
7. Posts the request to `/nuvl`
8. Receives a decision and reason
9. Reports the result to the coordinator
10. Returns to polling for the next run

The endpoint report includes the fields needed by the launcher to validate the run, including:

```text
run_id
device_id
endpoint IP
decision
reason
latency
nonce
memory delta
```

The exact field set may vary slightly between baseline and later stage-timing firmware.

## LED States

The onboard RGB LED provides a physical indication of endpoint state.

| LED | Meaning |
|---|---|
| Blue | Ready or idle |
| Cyan | Wi-Fi connected |
| Yellow | Request created |
| Purple | Provider or boundary decision pending |
| Green | Accepted |
| Red | Denied |
| Orange | Stale, replay, or malformed denial |
| White | Provider, network, boundary, or execution path unavailable |

LED output is an endpoint rendering mechanism. It is not the source of authority.

## Baseline Test 1: Three Accepted Outcomes

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

- All three expected endpoints respond
- Each endpoint reports its expected identity
- Each endpoint result is associated with the expected IP
- All three decisions are `accepted`
- All three reasons are `provider_admissible`
- No result is missing
- No result is assigned to the wrong endpoint

This test establishes the basic three-endpoint path.

## Baseline Test 2: Mixed Outcomes

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

This is the stronger baseline fleet test.

A correct aggregate count is not sufficient. PASS requires the correct decision and reason to remain bound to the correct physical endpoint.

The required relationship is:

```text
device identity
    +
assigned mode
    +
decision
    +
reason
    =
expected per-device result
```

A decision associated with the wrong endpoint is a failure even when the aggregate accepted and denied counts are correct.

## Harness-Oracle Failure

An earlier mixed-outcome run produced the correct endpoint results but was marked FAIL because the launcher still used an all-accept PASS rule.

Recorded run:

```text
run_id=18c5b0a38b1d51b0
system outcomes=correct
launcher result=FAIL
cause=all-accept PASS oracle
classification=harness/oracle failure
```

The failure was in the test oracle, not the endpoint or boundary behavior.

The corrected mixed launcher validates the expected outcome for each device individually.

This record is retained because test-harness failures are part of the engineering history and should not be silently removed.

## Single-Endpoint Diagnostic

Firmware:

```text
esp32_multi_once.py
```

The single-endpoint client is used to isolate one board from the fleet and verify:

- Device identity
- Wi-Fi connection
- Raspberry Pi reachability
- `/nuvl` reachability
- Decision parsing
- LED output
- Basic latency
- Endpoint recovery

This diagnostic should be used before modifying fleet logic when only one endpoint is missing or late.

## Fleet Validation Matrix

| Test | Result | Property exercised |
|---|---|---|
| Three-endpoint accepted baseline | PASS | All endpoints complete with correct identity and result binding |
| Three-endpoint mixed outcomes | PASS | Different decisions remain bound to the correct endpoints |
| Single-endpoint diagnostic | PASS | One board can be validated independently |
| Single-endpoint isolation | PASS | One unavailable endpoint does not corrupt the other results |
| Single-endpoint restoration | PASS | The isolated endpoint can resume participation |
| Shared-boundary outage | PASS | All endpoints fail unavailable without accepted action |
| Shared-boundary recovery | PASS with anomaly | Shared services recover; one endpoint required reset for timely participation |
| House-Wi-Fi comparison | PASS | Access-point-specific latency fault domain isolated |

## Archer Validation

The Archer validation set was created after the original fleet baseline.

Known files include:

```text
nuvl_local_hardened_latency.py
esp32_multi_poll_main_v2_pm_none_stage_v2_archer.py
esp32_multi_poll_main_v2_pm_none_stage_v2_archer_isolate_com9.py
run_three_esp32_poll_archer.py
run_three_esp32_mixed_archer.py
run_three_esp32_poll_isolate_com9_archer.py
run_three_esp32_poll_shared_boundary_outage_archer.py
```

These variants add or support:

- Stage-level timing
- House-network configuration
- Endpoint isolation
- Shared-boundary outage testing
- Recovery validation
- Later latency diagnosis

The `COM9` designation records the temporary Windows mapping used during the isolation test. It does not identify the endpoint independently of `device_id.txt`.

## Endpoint Isolation

The isolation test removes one endpoint from normal participation while the remaining endpoints continue through the shared coordinator and boundary.

The test checks that:

- Missing participation is detected
- Results from available endpoints remain correctly bound
- The absent endpoint does not cause identity reassignment
- The absent endpoint does not cause another endpoint’s result to be duplicated
- Available endpoints are not converted into false accepted results
- The launcher distinguishes an unavailable endpoint from an incorrect endpoint result

A correct isolation result is not the same as a full three-endpoint PASS. It is evaluated against the expected degraded-state oracle.

## Endpoint Restoration

After isolation, the removed endpoint is restored to normal participation.

PASS requires:

- The endpoint reconnects
- The endpoint reports its correct durable identity
- The endpoint receives the intended mode
- The endpoint result is correctly bound
- The other endpoints remain correct
- No service restart is required unless the test explicitly includes one

The recorded restoration test passed.

## Shared-Boundary Outage

The shared-boundary outage test removes the verification path used by all endpoints.

Expected behavior:

```text
boundary unavailable
        |
        v
endpoint cannot obtain a valid decision
        |
        v
endpoint reports unavailable
        |
        v
no fallback acceptance
```

PASS requires:

- No endpoint reports an accepted action
- No cached or previous acceptance is reused
- The unavailable condition is visible
- Endpoint identities remain distinguishable
- The fleet launcher does not reinterpret missing decisions as success

The shared-boundary outage test passed in the tested path.

## Shared-Boundary Recovery

After restoring the verification boundary and coordinator, the fleet was returned to service without rebuilding the entire environment.

Observed result:

- Shared services recovered
- The fleet eventually returned to three-endpoint operation
- One endpoint required reset before timely participation resumed

Classification:

```text
PASS with anomaly
```

The endpoint reset does not invalidate the shared-boundary fail-closed result.

It is retained as an operational recovery limitation.

## Latency Measurements

Original warmed fleet behavior was generally observed in the following range:

```text
approximately 32–48 ms
```

The original three-accept run completed in:

```text
33–34 ms
```

The original mixed-outcome run completed in:

```text
29–38 ms
```

Later stage-timing tests separated portions of the endpoint request path, including connection time and total elapsed time.

A 20-run stage-timing series completed:

```text
20/20 runs completed
60/60 endpoint transactions correct
13 PASS
7 PASS_DEGRADED
0 identity failures
0 decision failures
0 reason failures
0 missing results
0 late-result classification failures
```

The degraded classifications were based on latency budget, not incorrect authorization outcomes.

## Synchronized Latency Incident

One degraded run showed nearly identical connection-stage delays across all three endpoints:

```text
connect_ms approximately 866–868 ms
total elapsed approximately 891–893 ms
```

The Raspberry Pi Ethernet capture showed the endpoint TCP SYN traffic arriving together after the delay.

This indicated that the synchronized completion event was not caused by three independent endpoint execution stalls.

The leading fault domain was the access-point-specific wireless path.

The exact internal Mango mechanism remains unresolved.

No claim is made about:

- A specific Mango driver function
- A specific firmware defect
- A hardware defect
- A universal ESP32 compatibility problem

## House-Wi-Fi A/B Comparison

The same three endpoints, firmware logic, Raspberry Pi services, coordinator path, and provider path were tested through house Wi-Fi.

Observed comparison:

```text
13/13 runs PASS
39/39 endpoint transactions correct
33–147 ms endpoint latency
approximately 49.9 ms mean
41.5 ms median
0 results above the 250 ms budget
0 reproductions of the synchronized approximately 900 ms event
```

The comparison isolated the degraded event to the access-point-specific wireless path at the fault-domain level.

Incident status:

```text
closed at fault-domain level
exact internal mechanism unresolved
```

The Mango latency incident is engineering evidence. It is not the normal NUVL fleet baseline.

## Network Configuration

Public source should use explicit placeholders:

```python
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"
PI_IP = "YOUR_PI_IP"
```

The original Mango bench used:

```text
SSID: GL-MT300N-V2-94f
Raspberry Pi: 192.168.8.234
```

The original test files may contain bench-specific values.

A sanitized public copy is not byte-identical to the original tested source.

Do not reuse the tested-source hash for a modified copy.

Each published derivative should receive its own SHA-256 in:

```text
../evidence/SHA256SUMS.txt
```

## Source Classes

Fleet source should be labeled as one of the following.

### Original tested source

The exact file used during the recorded test.

### Sanitized public derivative

A copy modified to remove credentials, private values, or environment-specific configuration.

### Rerun-confirmed public source

A sanitized or reorganized copy executed again and confirmed against the documented PASS criteria.

Changing any of the following creates a new source version:

- SSID
- Password
- Raspberry Pi address
- Coordinator address
- Port
- Timeout
- Release timing
- Endpoint identity handling
- PASS oracle
- Decision mapping
- Reason mapping
- Source structure

Configuration-only changes may not alter the intended architecture, but they still change the file bytes and therefore require a new hash.

## Known Failed or Superseded Approaches

The fleet implementation includes several corrected development failures.

### Concurrent Windows `mpremote`

Attempting to control all three serial ports concurrently through Windows `mpremote` produced timeouts.

This approach was replaced with endpoint-originated outbound polling.

### Inbound UDP Triggering

Inbound UDP triggering was unreliable through the tested access-point path.

The fleet retained outbound HTTP polling.

### Absolute Release Timestamp

The first coordinator exchanged an absolute timestamp between Raspberry Pi Python and MicroPython.

The epoch mismatch made the release time unreliable.

The supported coordinator uses relative `wait_ms`.

### All-Accept Mixed-Test Oracle

The first mixed launcher evaluated success using an all-accept rule.

It reported FAIL even though the endpoint outcomes were correct for the assigned mixed modes.

The corrected launcher uses per-device expected decisions and reasons.

## Evidence

Fleet run IDs and summarized results are documented here, but run IDs are not substitutes for evidence files.

Current recorded runs:

```text
Three-accept baseline:
run_id=18c565fc0e9dfd5c

Mixed outcomes:
run_id=18c5b11e874cd4cc

Harness-oracle failure:
run_id=18c5b0a38b1d51b0
```

Fleet logs should be added to [`../evidence/`](../evidence/) only after:

- The exact file is identified
- The associated run is confirmed
- The file is classified as original or sanitized
- The SHA-256 is calculated
- Any anomaly is documented
- The applicable fleet README links to it

See [`../evidence/README.md`](../evidence/README.md) for the evidence policy.

## Limitations

The fleet results apply to the tested topology and paths.

They do not establish:

- Parallel processing inside the original single-threaded boundary
- Behavior with arbitrary endpoint counts
- Behavior across arbitrary Wi-Fi access points
- Behavior under sustained RF interference
- Behavior under deliberate wireless jamming
- Long-duration repeated endpoint dropout and restoration
- Multi-boundary coordination
- Independent reproduction by an external laboratory
- Production readiness
- Safety certification
- Authorization correctness outside the implemented request modes

The endpoint trusts the downstream Raspberry Pi decision in the original fleet architecture.

The ESP32 does not independently verify the provider signature.

A compromised Raspberry Pi boundary could therefore fabricate a result to the trusting endpoint in this implementation.

That limitation is architectural and must not be omitted.

## Recommended Reproduction Order

1. Validate one endpoint with `esp32_multi_once.py`
2. Start `nuvl_local_hardened.py`
3. Start `multi_endpoint_coordinator_v2.py`
4. Deploy `esp32_multi_poll_main_v2.py` as `main.py`
5. Confirm all three `device_id.txt` files
6. Run `run_three_esp32_poll.py`
7. Confirm the three-accept baseline
8. Run `run_three_esp32_mixed.py`
9. Confirm per-device mixed-outcome binding
10. Attempt endpoint isolation
11. Restore the isolated endpoint
12. Test shared-boundary outage
13. Restore the shared boundary
14. Attempt stage-timing and wireless-path comparisons only after the baseline is stable

Begin with [`baseline/`](baseline/) before using the Archer validation variants.
