# NUVL Edge Lab

NUVL Edge Lab is a physical test environment for provider-controlled validation and bounded authority on low-resource endpoints.

The laboratory uses:

- Three ESP32-S3 endpoints
- A Raspberry Pi fleet coordinator
- A Raspberry Pi verification boundary
- Local wireless infrastructure
- A Windows control host
- A provider that retains its Ed25519 private signing key

The tests examine whether constrained endpoints can request, receive, and display provider-bound decisions without independently acquiring reusable authorization authority.

The central architectural distinction is:

> The endpoint may request, observe, display, or act on a bounded result, but it does not independently create, enlarge, or reuse provider authority.

## What Has Been Tested

The current laboratory work includes:

- Three physical endpoints using one shared verification boundary
- Per-device identity, decision, and reason binding
- Mixed accepted and denied outcomes in the same fleet run
- Endpoint isolation and restoration
- Shared-boundary outage and recovery
- Fail-unavailable behavior without fallback acceptance
- Stage-level endpoint timing
- Wireless-path fault isolation
- Provider-issued authority bounded for disconnected use
- Replay rejection across process restart and Raspberry Pi power loss
- Exactly one successful exercise under overlapping attempts
- Crash after persistent commit but before response
- Crash before atomic state replacement

The results apply to the tested paths, configurations, and fault-injection points.

## Laboratory Architecture

The original fleet path is:

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
        | create requests
        | POST /nuvl
        v
Raspberry Pi verification boundary
        |
        | returns decision and reason
        v
ESP32-S3 endpoint reports
        |
        v
Fleet launcher validates:
identity
IP
decision
reason
timing
```

Primary services:

| Port | Service |
|---:|---|
| `8089` | NUVL verification boundary |
| `19052` | Fleet coordinator |

The original Raspberry Pi boundary uses Python `HTTPServer` and is single-threaded.

The fleet tests demonstrate coordinated fan-in through one shared boundary. They do not claim parallel processing inside that boundary.

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

Contains the three-endpoint fleet implementation and the later timing, isolation, outage, recovery, and wireless-comparison tests.

Begin with:

```text
fleet/baseline/
```

### [`disconnected-authority/`](disconnected-authority/)

Contains the bounded disconnected-use, replay-prevention, power-loss, overlapping-attempt, and crash-window tests.

### [`evidence/`](evidence/)

Contains selected logs and manifests supporting specific test results.

## Original Fleet Baseline

The original fleet implementation uses:

```text
nuvl_local_hardened.py
multi_endpoint_coordinator_v2.py
esp32_multi_poll_main_v2.py
esp32_multi_once.py
run_three_esp32_poll.py
run_three_esp32_mixed.py
```

Each ESP32-S3 contains:

```text
main.py
device_id.txt
```

The same fleet firmware is deployed to all three endpoints as `main.py`.

The durable endpoint identity is stored separately in `device_id.txt`.

Confirmed endpoint identities:

```text
esp32-field-01
esp32-s3-02
esp32-s3-03
```

COM port numbers are temporary Windows bench mappings and are not endpoint identities.

## Fleet Operation

The baseline firmware follows this sequence:

1. Read `device_id.txt`
2. Connect to Wi-Fi
3. Poll the Raspberry Pi coordinator
4. Receive a `run_id`, request mode, and relative `wait_ms`
5. Wait for the assigned release interval
6. Create a request
7. Submit the request to `/nuvl`
8. Receive a decision and reason
9. Report the result to the coordinator
10. Return to polling

The coordinator uses relative `wait_ms` timing.

This replaced an earlier absolute-timestamp design that failed because Raspberry Pi Python and MicroPython used incompatible epoch representations.

## Endpoint LED States

The ESP32-S3 onboard RGB LED displays the endpoint state.

| LED | Meaning |
|---|---|
| Blue | Ready or idle |
| Cyan | Wi-Fi connected |
| Yellow | Request created |
| Purple | Verification pending |
| Green | Accepted |
| Red | Denied |
| Orange | Stale, replay, or malformed denial |
| White | Network, provider, boundary, or execution path unavailable |

The LED displays the result returned through the tested path. It is not the source of authority.

## Three-Accept Fleet Baseline

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
- No endpoint result is missing
- No result is assigned to the wrong endpoint

## Mixed-Outcome Fleet Test

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

This is the stronger original fleet test.

A correct aggregate count is not sufficient. PASS requires the correct decision and reason to remain attached to the correct physical endpoint.

## Preserved Harness Failure

An earlier mixed-outcome run produced the correct endpoint results but was marked FAIL because the launcher still applied an all-accept PASS rule.

```text
run_id=18c5b0a38b1d51b0
system outcomes=correct
launcher result=FAIL
cause=all-accept PASS oracle
classification=harness/oracle failure
```

The failure was in the test oracle, not the endpoint or verification-boundary behavior.

The corrected launcher validates the expected result for each endpoint individually.

## Archer Fleet Validation

The Archer validation work extends the original baseline with:

- Stage-level endpoint timing
- Repeated three-endpoint runs
- Mixed per-device outcomes
- Single-endpoint isolation
- Single-endpoint restoration
- Shared-boundary outage
- Shared-boundary recovery
- House-Wi-Fi comparison
- Wireless fault-domain isolation

A twenty-run stage-timing campaign completed:

```text
20/20 fleet runs completed
60/60 endpoint transactions correct
13 PASS
7 PASS_DEGRADED
```

Across the campaign:

```text
0 identity failures
0 decision failures
0 reason failures
0 missing-result failures
```

The degraded classifications were caused by latency-budget behavior, not incorrect authorization outcomes.

## Wireless Latency Incident

One degraded run showed nearly identical connection-stage delays across all three endpoints:

```text
connect_ms approximately 866–868 ms
total elapsed approximately 891–893 ms
```

A Raspberry Pi Ethernet capture showed the endpoint TCP SYN traffic arriving together after the delay.

The fleet was then moved to house Wi-Fi for comparison.

Observed house-Wi-Fi results:

```text
13/13 runs PASS
39/39 endpoint transactions correct
33–147 ms endpoint latency
approximately 49.9 ms mean
41.5 ms median
0 results above the 250 ms budget
0 reproductions of the synchronized approximately 900 ms event
```

The incident was closed at the fault-domain level.

Supported conclusion:

> The access-point-specific wireless path was isolated as the fault domain.

The exact internal Mango mechanism remains unresolved.

No claim is made about a specific driver function, firmware defect, or hardware defect.

## Disconnected Authority

The disconnected-authority tests examine whether a provider-issued artifact remains bounded when the provider is temporarily unavailable.

The general path is:

```text
Provider
   |
   | issues signed, bounded artifact
   v
ESP32-S3 endpoint or test client
   |
   | presents artifact and request
   v
Raspberry Pi verification boundary
   |
   | verifies provider signature
   | verifies explicit bounds
   | checks single-use state
   v
Accepted once or denied
```

The provider retains the Ed25519 private signing key.

The Raspberry Pi boundary uses provider public verification material.

The endpoint does not receive the provider private key and does not independently mint provider authority.

## POC003 — Bounded Disconnected Single Use

POC003 establishes the base disconnected-authority behavior.

The provider file is:

```text
poc003_ed25519_provider_1h.py
```

The provider issues an Ed25519-signed, single-use artifact before disconnection.

The Raspberry Pi boundary verifies and enforces that artifact while the provider is unavailable.

The tested matrix includes:

- Valid bounded use
- Replay
- Context mismatch
- Action mismatch
- Nonce mismatch
- Device mismatch
- Tampered artifact
- Unsigned artifact
- Expired artifact
- Missing artifact

Expected behavior:

```text
valid bounded use        -> accepted once
replay                   -> denied
context mismatch         -> denied
action mismatch          -> denied
nonce mismatch           -> denied
device mismatch          -> denied
tampering                -> denied
unsigned material        -> denied
expired artifact         -> denied
missing artifact         -> denied
```

## POC004 — Replay State Across Process Restart

POC004 tested whether spent-state enforcement survived restart of the Raspberry Pi verification-boundary process.

Observed result:

> Replay remained denied after process restart.

POC004 remains part of the recorded test history.

## POC004B — Replay State Across Power Loss

POC004B extends the persistence test from process restart to abrupt Raspberry Pi power loss.

Observed result:

> A completed persistent-state commit remained effective after abrupt Raspberry Pi power loss.

After power restoration:

- The verification boundary recovered
- The fleet coordinator recovered
- The fleet eventually returned to three-endpoint operation
- One endpoint required reset before timely participation resumed

The recovery result is recorded as:

```text
PASS with anomaly
```

The endpoint reset does not invalidate the persistent replay result.

## POC005 — Overlapping Attempts

POC005 submits two overlapping attempts against one single-use artifact.

Expected result:

```text
attempts started:  2
accepted:          1
denied:            1
duplicate accept:  0
```

Observed result:

> Exactly one attempt succeeded and no duplicate acceptance occurred.

The test demonstrates single-use enforcement under near-concurrent competing attempts.

It does not claim mathematically simultaneous execution.

## POC006A — Crash After Commit

POC006A injects a crash after persistent spent-state has been committed but before the successful response is returned.

Observed result:

> The missing response did not permit the committed artifact to be accepted again.

After restart, replay of the same artifact remained denied.

## WP2-T1 — Crash Before Atomic Replacement

WP2-T1 injects a crash after temporary state has been written and synchronized but before atomic replacement of the committed state file.

Observed result:

> The interrupted replacement did not falsely consume the artifact. The commit could be retried after restart, after which replay remained denied.

The verification boundary used in the recorded test was:

```text
wp2_t1_pre_replace_boundary_archer.py
```

Confirmed source SHA-256:

```text
87351DBDF539E0E44480B28B205AE04FAD796D9C60DA9C4084FDEFDA49A9BFC8
```

The similarly named file:

```text
wp2_t1_temp_fsync_boundary_archer.py
```

was not the boundary used in the recorded test.

## Test Summary

| Test | Location | Result | Property exercised |
|---|---|---|---|
| Three-endpoint baseline | [`fleet/baseline/`](fleet/baseline/) | PASS | Correct identity and result binding |
| Mixed fleet outcomes | [`fleet/baseline/`](fleet/baseline/) | PASS | Different outcomes remain bound to the correct devices |
| Single-endpoint isolation | [`fleet/archer-validation/`](fleet/archer-validation/) | PASS | One unavailable endpoint does not corrupt the other results |
| Single-endpoint restoration | [`fleet/archer-validation/`](fleet/archer-validation/) | PASS | The isolated endpoint resumes participation |
| Shared-boundary outage | [`fleet/archer-validation/`](fleet/archer-validation/) | PASS | All endpoints fail unavailable without accepted action |
| Shared-boundary recovery | [`fleet/archer-validation/`](fleet/archer-validation/) | PASS with anomaly | Services recover; one endpoint required reset |
| POC003 | [`disconnected-authority/poc003-single-use/`](disconnected-authority/poc003-single-use/) | PASS | Bounded disconnected single use |
| POC004B | [`disconnected-authority/poc004b-power-loss/`](disconnected-authority/poc004b-power-loss/) | PASS | Completed commit survives abrupt power loss |
| POC005 | [`disconnected-authority/poc005-double-spend/`](disconnected-authority/poc005-double-spend/) | PASS | Competing attempts produce exactly one acceptance |
| POC006A | [`disconnected-authority/poc006a-commit-before-accept/`](disconnected-authority/poc006a-commit-before-accept/) | PASS | Crash after commit remains replay-denied |
| WP2-T1 | [`disconnected-authority/wp2-t1-pre-replace/`](disconnected-authority/wp2-t1-pre-replace/) | PASS | Crash before replacement does not falsely consume the artifact |

## Configuration

The ESP32 firmware requires local Wi-Fi and Raspberry Pi settings.

Example:

```python
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"
PI_IP = "YOUR_PI_IP"
```

The Raspberry Pi address must point to the system running the coordinator and verification-boundary services.

The recorded Mango environment used:

```text
SSID: GL-MT300N-V2-94f
Raspberry Pi: 192.168.8.234
```

Other networks will require different values.

## Evidence

Selected evidence is stored under:

```text
evidence/
```

The current evidence set includes:

```text
poc004b_archer_evidence_20260730_225507.log
post_powercycle_fleet_restoration_20260730_231251.log
poc004b_local_manifest_20260731_232149.txt
wp2_t1_final_evidence_20260801_010225.log
```

See [`evidence/README.md`](evidence/README.md) for descriptions, recorded hashes, and verification commands.

## Public Boundary Coverage

Some disconnected-authority test folders do not include the complete mechanism-level verification-boundary implementation.

Those folders still document:

- The client sequence
- The boundary interface
- The request and response behavior
- The failure-injection point
- The expected result
- The observed result
- The PASS criteria
- The supporting evidence
- The known limitations

Where a boundary implementation is not included, the applicable test README states that directly.

## Limitations

The current results do not establish:

- Parallel processing inside the original single-threaded boundary
- Correct operation with arbitrary endpoint counts
- Correct operation across arbitrary wireless networks
- Behavior under deliberate radio jamming
- Behavior under sustained RF interference
- Every possible persistence crash point
- Startup with corrupt or truncated persistent state
- Cross-process contention
- Multi-boundary contention
- Long-duration repeated power-cycle endurance
- Independent reproduction by an external laboratory
- Production readiness
- Safety certification

The ESP32-S3 endpoints trust the downstream result returned by the Raspberry Pi verification boundary.

The endpoints do not independently verify the provider signature.

A compromised Raspberry Pi could therefore fabricate a downstream result to a trusting endpoint in this implementation.

That limitation is part of the tested architecture.

## Where to Begin

Start with the original fleet baseline:

```text
fleet/baseline/
```

After confirming the three-accept and mixed-outcome fleet tests, continue with:

1. Archer endpoint isolation and restoration
2. Shared-boundary outage and recovery
3. POC003 bounded disconnected single use
4. POC004B power-loss persistence
5. POC005 overlapping attempts
6. POC006A crash after commit
7. WP2-T1 crash before atomic replacement
