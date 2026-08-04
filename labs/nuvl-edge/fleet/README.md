# NUVL Edge Fleet

This directory contains the multi-endpoint tests for the NUVL Edge Lab.

The fleet consists of three physical ESP32-S3 endpoints using one Raspberry Pi coordinator and one shared NUVL verification boundary.

The tests examine whether endpoint identity, assigned request mode, decision, denial reason, timing, and recovery behavior remain correctly bound when multiple constrained devices operate through the same path.

The fleet demonstrates a separation between endpoint capability and provider-controlled authority:

> Each endpoint can create a request, receive a provider-bound result, and display that result without independently creating or retaining provider authority.

## What the Fleet Tests Demonstrate

The current fleet work covers:

- Three physical ESP32-S3 endpoints
- One shared Raspberry Pi verification boundary
- Coordinated near-concurrent request release
- Three accepted outcomes in one run
- Mixed accepted and denied outcomes in one run
- Per-device decision and reason binding
- Single-endpoint diagnostics
- Endpoint isolation and restoration
- Shared-boundary outage and recovery
- Stage-level latency measurement
- Wireless-path comparison
- Fail-unavailable behavior without fallback acceptance

The original Raspberry Pi boundary uses Python `HTTPServer` and is single-threaded.

The demonstrated property is coordinated fleet behavior through one shared boundary. The tests do not claim parallel request processing inside that boundary.

## Fleet Architecture

```text
Windows control host
        |
        | starts fleet launcher
        v
Raspberry Pi fleet coordinator
        |
        | assigns run_id
        | assigns request mode
        | assigns relative wait_ms
        v
Three ESP32-S3 endpoints
        |
        | create and submit requests
        | POST /nuvl
        v
Raspberry Pi NUVL verification boundary
        |
        | returns decision and reason
        v
ESP32-S3 endpoint reports
        |
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

The deployed firmware is stored on each endpoint as:

```text
main.py
```

The same fleet firmware can be used on all three devices. The `device_id.txt` file distinguishes the physical endpoints.

A recorded Windows USB mapping was:

```text
COM5  -> esp32-field-01
COM9  -> esp32-s3-02
COM12 -> esp32-s3-03
```

COM port numbers are temporary bench mappings. They may change after reconnecting the boards, moving USB ports, rebooting Windows, or reinstalling drivers.

The durable identity is the value in `device_id.txt`, not the COM port number.

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

## Baseline Fleet

The [`baseline/`](baseline/) directory contains the original three-endpoint fleet implementation.

This is the starting point for understanding and reproducing the fleet path.

The baseline includes:

```text
nuvl_local_hardened.py
multi_endpoint_coordinator_v2.py
esp32_multi_poll_main_v2.py
esp32_multi_once.py
run_three_esp32_poll.py
run_three_esp32_mixed.py
```

The baseline established:

- Three physical endpoint responses
- Correct durable endpoint identities
- Correct endpoint IP associations
- Three accepted outcomes in one run
- Mixed accepted and denied outcomes in one run
- Correct per-device decision and reason binding
- No cross-assigned results
- Relative `wait_ms` coordination
- Endpoint-originated outbound HTTP polling

See [`baseline/README.md`](baseline/README.md) for component roles, setup, test commands, PASS criteria, and recorded runs.

## Archer Validation

The [`archer-validation/`](archer-validation/) directory contains the later validation work performed after the baseline was established.

The Archer validation set extends the baseline with:

- Stage-level endpoint timing
- Repeated three-endpoint timing runs
- Single-endpoint isolation
- Single-endpoint restoration
- Shared-boundary outage
- Shared-boundary recovery
- House-Wi-Fi comparison
- Access-point fault-domain isolation

It also documents the synchronized latency incident observed through the Mango access-point path.

See [`archer-validation/README.md`](archer-validation/README.md) for the timing campaign, outage tests, recovery results, and wireless-path comparison.

## Endpoint Firmware Behavior

The fleet firmware follows this sequence:

1. Read `device_id.txt`
2. Connect to Wi-Fi
3. Poll the Raspberry Pi coordinator
4. Receive a `run_id`, request mode, and relative `wait_ms`
5. Wait for the assigned release interval
6. Create the request
7. Submit the request to `/nuvl`
8. Receive a decision and reason
9. Report the result to the coordinator
10. Return to polling for the next run

Endpoint reports include the information needed to evaluate the fleet run, including:

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

Later stage-timing firmware includes additional timing fields.

## Coordinator Timing

The supported fleet coordinator uses:

```text
wait_ms
```

This is a relative delay assigned to each endpoint.

An earlier coordinator used an absolute timestamp. That approach failed because Raspberry Pi Python and MicroPython did not use compatible epoch representations.

The supported sequence is:

```text
coordinator assigns relative wait_ms
endpoint receives wait_ms
endpoint waits locally
endpoint submits request
```

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

The LED displays the result returned through the tested path. It is not the source of authority.

## Baseline Test: Three Accepted Outcomes

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
- Each endpoint reports its correct identity
- Each result is associated with the expected endpoint IP
- All three decisions are `accepted`
- All three reasons are `provider_admissible`
- No result is missing
- No result is assigned to the wrong endpoint

## Baseline Test: Mixed Outcomes

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

A correct aggregate count is not enough. PASS requires the correct decision and reason to remain bound to the correct physical endpoint.

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

## Preserved Harness Failure

An earlier mixed-outcome run produced the correct endpoint results but was marked FAIL because the launcher still used an all-accept PASS rule.

Recorded run:

```text
run_id=18c5b0a38b1d51b0
system outcomes=correct
launcher result=FAIL
cause=all-accept PASS oracle
classification=harness/oracle failure
```

The failure was in the test oracle, not the endpoint or verification-boundary behavior.

The corrected mixed launcher validates the expected decision and reason for each endpoint individually.

This record remains part of the engineering history because a test harness can misclassify a correct system result.

## Single-Endpoint Diagnostic

The baseline includes:

```text
esp32_multi_once.py
```

This client validates one endpoint independently before the full fleet is run.

It can be used to check:

- Device identity
- Wi-Fi connection
- Raspberry Pi reachability
- `/nuvl` reachability
- Decision parsing
- LED output
- Basic latency
- Endpoint recovery

A single-endpoint diagnostic is useful when only one endpoint is missing, late, or unable to complete the normal fleet path.

## Fleet Validation Results

| Test | Result | Property exercised |
|---|---|---|
| Three-endpoint accepted baseline | PASS | All endpoints complete with correct identity and result binding |
| Three-endpoint mixed outcomes | PASS | Different decisions remain bound to the correct endpoints |
| Single-endpoint diagnostic | PASS | One board can be validated independently |
| Single-endpoint isolation | PASS | One unavailable endpoint does not corrupt the other results |
| Single-endpoint restoration | PASS | The isolated endpoint resumes participation |
| Shared-boundary outage | PASS | All endpoints fail unavailable without accepted action |
| Shared-boundary recovery | PASS with anomaly | Shared services recover; one endpoint required reset |
| Twenty-run stage-timing series | 13 PASS / 7 PASS_DEGRADED | Correct results remain preserved during latency variation |
| House-Wi-Fi comparison | 13/13 PASS | Access-point-specific latency fault domain isolated |

## Endpoint Isolation

The isolation test removes one endpoint from normal participation while the remaining endpoints continue through the shared coordinator and verification boundary.

The test checks that:

- Missing participation is detected
- Results from available endpoints remain correctly bound
- The absent endpoint does not cause identity reassignment
- The absent endpoint does not duplicate another endpoint's result
- Available endpoints are not converted into false accepted results
- The launcher distinguishes unavailability from an incorrect result

The recorded isolation target was:

```text
esp32-s3-02
temporary Windows mapping: COM9
```

A correct isolation result is evaluated against the expected degraded state. It is not represented as a normal three-endpoint PASS.

## Endpoint Restoration

After isolation, the removed endpoint was returned to normal participation.

The restoration test checks that:

- The endpoint reconnects
- The endpoint reports its correct durable identity
- The endpoint receives the intended mode
- The endpoint result is correctly bound
- The other endpoints remain correct
- No identity or result cross-assignment occurs

The recorded restoration test passed.

## Shared-Boundary Outage

The shared-boundary outage test removes the verification path used by all three endpoints.

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
- No previous acceptance is reused
- No local fallback acceptance occurs
- The unavailable condition remains visible
- Endpoint identities remain distinguishable
- Missing or timed-out decisions are not interpreted as success

The shared-boundary outage test passed in the tested path.

## Shared-Boundary Recovery

After restoring the verification boundary and coordinator, the fleet was returned to service.

Observed result:

- Shared services recovered
- The fleet eventually returned to three-endpoint operation
- One endpoint required reset before timely participation resumed

Classification:

```text
PASS with anomaly
```

The endpoint reset does not invalidate the fail-unavailable result.

It remains a documented operational recovery limitation.

## Timing Results

Original warmed fleet behavior was generally observed around:

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

The later Stage-Timing V2 campaign completed:

```text
20/20 fleet runs completed
60/60 endpoint transactions correct
13 PASS
7 PASS_DEGRADED
```

Across that campaign:

```text
0 identity failures
0 decision failures
0 reason failures
0 missing-result failures
```

The degraded classifications were based on latency budget, not incorrect authorization outcomes.

## Synchronized Latency Incident

One degraded run showed nearly identical connection-stage delays across all three endpoints.

Recorded behavior:

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
- A confirmed firmware defect
- A confirmed hardware defect
- A universal ESP32 compatibility problem

## House-Wi-Fi Comparison

The same three endpoints, firmware logic, Raspberry Pi services, coordinator path, and verification-boundary path were tested through house Wi-Fi.

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

## Configuration

The ESP32 firmware requires the local Wi-Fi and Raspberry Pi settings.

Example:

```python
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"
PI_IP = "YOUR_PI_IP"
```

The Raspberry Pi address must point to the system running the coordinator and verification-boundary services.

The original Mango bench used:

```text
SSID: GL-MT300N-V2-94f
Raspberry Pi: 192.168.8.234
```

The house-Wi-Fi comparison used a different local network.

## Known Failed or Superseded Approaches

Several earlier approaches were tested and replaced.

### Concurrent Windows `mpremote`

Attempting to control all three serial ports concurrently through Windows `mpremote` produced timeouts.

This approach was replaced by endpoint-originated outbound polling.

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

## Limitations

The fleet results apply to the tested topology and paths.

They do not establish:

- Parallel processing inside the original single-threaded boundary
- Correct operation with arbitrary endpoint counts
- Correct operation across arbitrary wireless networks
- Behavior under deliberate wireless jamming
- Behavior under sustained RF interference
- Long-duration repeated endpoint dropout and restoration
- Multi-boundary coordination
- Independent reproduction by an external laboratory
- Production readiness
- Safety certification
- Authorization correctness outside the implemented request modes

The ESP32-S3 endpoints trust the downstream result returned by the Raspberry Pi verification boundary.

The endpoints do not independently verify the provider signature.

The Raspberry Pi holds the provider public trust anchor, while the provider retains the private signing key.

The endpoints do not hold the provider private key and do not independently mint provider authority.

However, a compromised Raspberry Pi could fabricate a downstream result to a trusting endpoint in this implementation.

That limitation is part of the tested architecture.

## Recommended Test Order

1. Validate one endpoint with `esp32_multi_once.py`.
2. Start `nuvl_local_hardened.py`.
3. Start `multi_endpoint_coordinator_v2.py`.
4. Deploy `esp32_multi_poll_main_v2.py` as `main.py`.
5. Confirm all three `device_id.txt` values.
6. Run `run_three_esp32_poll.py`.
7. Confirm the three-accept baseline.
8. Run `run_three_esp32_mixed.py`.
9. Confirm per-device mixed-outcome binding.
10. Move to endpoint isolation and restoration.
11. Test shared-boundary outage and recovery.
12. Attempt stage-timing and wireless-path comparisons only after the baseline is stable.

Begin with [`baseline/`](baseline/) before using the Archer validation variants.

## Recorded Runs

Three-accept baseline:

```text
run_id=18c565fc0e9dfd5c
```

Mixed-outcome PASS:

```text
run_id=18c5b11e874cd4cc
```

Mixed-outcome harness failure:

```text
run_id=18c5b0a38b1d51b0
```

Additional logs and manifests are indexed under:

```text
../evidence/
```

See [`../evidence/README.md`](../evidence/README.md) for the current evidence set.
