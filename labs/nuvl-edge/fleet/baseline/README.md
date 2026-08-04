# NUVL Edge Fleet Baseline

This directory contains the original three-endpoint NUVL Edge fleet implementation.

It is the starting point for reproducing the physical fleet path before moving to the later Archer timing, isolation, outage, and wireless-comparison tests.

The baseline uses:

- Three physical ESP32-S3 endpoints
- One Raspberry Pi fleet coordinator
- One Raspberry Pi NUVL verification boundary
- Outbound HTTP polling from each endpoint
- A durable identity stored on each board
- Per-device validation of decision and reason
- RGB LED output at each endpoint

The baseline tests whether three constrained endpoints can share one verification boundary without losing the relationship between:

```text
endpoint identity
assigned request mode
decision
reason
reported result
```

## What the Baseline Demonstrates

Each ESP32-S3 can:

- Identify itself
- Poll the Raspberry Pi coordinator
- Receive a test assignment
- Create a request
- Submit the request to the NUVL boundary
- Receive a decision and reason
- Display the result through its onboard RGB LED
- Report the result back to the fleet coordinator

The endpoints do not independently create provider authority.

The tested baseline demonstrates:

- Coordinated three-endpoint operation
- Correct endpoint identity binding
- Correct decision and reason binding
- Three accepted outcomes in one run
- Mixed accepted and denied outcomes in one run
- No cross-assignment of one endpoint's result to another
- One shared verification boundary
- No fallback acceptance when the request path cannot complete

## Architecture

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
        | POST /nuvl
        v
Raspberry Pi verification boundary
        |
        | returns decision and reason
        v
ESP32-S3 endpoint report
        |
        v
Fleet coordinator
        |
        v
Windows launcher evaluates PASS or FAIL
```

Primary services:

| Port | Service |
|---:|---|
| `8089` | NUVL verification boundary |
| `19052` | Fleet coordinator |

The verification boundary uses Python `HTTPServer` and is single-threaded.

The baseline demonstrates coordinated fan-in through one shared boundary. It does not claim parallel request processing inside the Raspberry Pi boundary.

## Directory Contents

```text
baseline/
├── README.md
│
├── boundary/
│   └── nuvl_local_hardened.py
│
├── coordinator/
│   └── multi_endpoint_coordinator_v2.py
│
├── firmware/
│   ├── esp32_multi_poll_main_v2.py
│   └── esp32_multi_once.py
│
├── launchers/
│   ├── run_three_esp32_poll.py
│   └── run_three_esp32_mixed.py
│
└── endpoint-config/
    ├── esp32-field-01/
    │   └── device_id.txt
    ├── esp32-s3-02/
    │   └── device_id.txt
    └── esp32-s3-03/
        └── device_id.txt
```

## Components

### Verification Boundary

File:

```text
boundary/nuvl_local_hardened.py
```

The Raspberry Pi verification boundary accepts requests at:

```text
POST /nuvl
```

The baseline request modes produce these decision and reason pairs:

```text
accepted / provider_admissible
denied / unauthorized_request
denied / stale_replay_malformed
```

All three endpoints use the same shared boundary.

### Fleet Coordinator

File:

```text
coordinator/multi_endpoint_coordinator_v2.py
```

The coordinator:

- Creates and tracks fleet runs
- Assigns a mode to each endpoint
- Assigns a relative `wait_ms`
- Receives endpoint reports
- Preserves the relationship between run ID and endpoint identity
- Makes the completed results available to the launcher

The coordinator uses relative release timing.

An earlier design used an absolute timestamp. That approach was replaced because Raspberry Pi Python and MicroPython represented epochs differently.

The supported sequence is:

```text
coordinator assigns wait_ms
endpoint receives wait_ms
endpoint waits locally
endpoint submits request
```

### Fleet Firmware

File:

```text
firmware/esp32_multi_poll_main_v2.py
```

This is the primary firmware used on all three ESP32-S3 endpoints.

The firmware:

1. Reads the endpoint identity from `device_id.txt`
2. Connects to Wi-Fi
3. Polls the fleet coordinator
4. Receives a `run_id`, mode, and relative `wait_ms`
5. Waits for the assigned release interval
6. Creates the request
7. Posts the request to `/nuvl`
8. Receives a decision and reason
9. Reports the result to the coordinator
10. Returns to polling for the next run

The same firmware is used on all three boards.

The board-specific identity comes from `device_id.txt`.

### Single-Endpoint Diagnostic

File:

```text
firmware/esp32_multi_once.py
```

The single-endpoint client is used to validate one endpoint independently before running the full fleet.

It can help isolate:

- Board identity
- Wi-Fi connectivity
- Raspberry Pi reachability
- Boundary reachability
- Decision parsing
- LED behavior
- Basic request latency

### Three-Accept Launcher

File:

```text
launchers/run_three_esp32_poll.py
```

This launcher assigns the accepted path to all three endpoints.

Expected result:

```text
esp32-field-01 -> accepted / provider_admissible
esp32-s3-02    -> accepted / provider_admissible
esp32-s3-03    -> accepted / provider_admissible
```

### Mixed-Outcome Launcher

File:

```text
launchers/run_three_esp32_mixed.py
```

This launcher assigns a different expected outcome to each endpoint.

Expected result:

```text
esp32-field-01 -> accepted / provider_admissible
esp32-s3-02    -> denied / unauthorized_request
esp32-s3-03    -> denied / stale_replay_malformed
```

The launcher validates each endpoint individually.

Correct aggregate counts are not enough to earn PASS.

## Endpoint Identities

The fleet uses these durable endpoint identities:

```text
esp32-field-01
esp32-s3-02
esp32-s3-03
```

Each physical board stores its own identity in:

```text
device_id.txt
```

The repository keeps the three identity files in separate directories:

```text
endpoint-config/
├── esp32-field-01/device_id.txt
├── esp32-s3-02/device_id.txt
└── esp32-s3-03/device_id.txt
```

Each file contains only the corresponding endpoint name.

Example:

```text
esp32-field-01
```

## ESP32-S3 Setup

Each endpoint requires:

```text
main.py
device_id.txt
```

Copy:

```text
firmware/esp32_multi_poll_main_v2.py
```

to each board as:

```text
main.py
```

Then copy the matching identity file to the same board.

Example board contents:

```text
main.py
device_id.txt
```

The firmware is shared across the fleet. The identity file distinguishes the three physical endpoints.

## Endpoint Identity and COM Ports

The durable endpoint identity comes from:

```text
device_id.txt
```

COM port numbers are temporary Windows mappings.

One recorded bench mapping was:

```text
COM5  -> esp32-field-01
COM9  -> esp32-s3-02
COM12 -> esp32-s3-03
```

Those COM numbers may change after:

- Reconnecting a board
- Moving it to another USB port
- Rebooting Windows
- Reinstalling a driver

The COM number should not be used as the endpoint identity.

## Configuration

The ESP32 firmware requires the local Wi-Fi and Raspberry Pi settings.

Example:

```python
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"
PI_IP = "YOUR_PI_IP"
```

The Raspberry Pi address must point to the system running both the coordinator and verification-boundary services.

The original Mango bench used:

```text
SSID: GL-MT300N-V2-94f
Raspberry Pi: 192.168.8.234
```

A different network may use a different address, SSID, and password.

## Starting the Services

Start the Raspberry Pi verification boundary:

```bash
python3 boundary/nuvl_local_hardened.py
```

Start the fleet coordinator in a second terminal:

```bash
python3 coordinator/multi_endpoint_coordinator_v2.py
```

Before running the fleet launcher, confirm:

- The boundary is listening on port `8089`
- The coordinator is listening on port `19052`
- The endpoints can reach the Raspberry Pi
- Each endpoint reports its expected identity
- Each board has the correct `device_id.txt`

## LED States

The onboard RGB LED provides a physical indication of endpoint state.

| LED | Meaning |
|---|---|
| Blue | Ready or idle |
| Cyan | Wi-Fi connected |
| Yellow | Request created |
| Purple | Boundary or provider decision pending |
| Green | Accepted |
| Red | Denied |
| Orange | Stale, replay, or malformed denial |
| White | Network, provider, boundary, or execution path unavailable |

The LED displays the result returned through the tested path. It is not the source of authority.

## Test 1: Three Accepted Outcomes

Run:

```bash
python launchers/run_three_esp32_poll.py
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

### PASS Criteria

PASS requires:

- Three expected endpoint reports
- Correct durable identity for each endpoint
- Correct endpoint IP association
- Three `accepted` decisions
- Three `provider_admissible` reasons
- No missing endpoint
- No duplicate endpoint
- No result assigned to the wrong device

A run with only two endpoint reports is not PASS.

A run with three accepted counts but incorrect device binding is not PASS.

## Test 2: Mixed Outcomes

Run:

```bash
python launchers/run_three_esp32_mixed.py
```

Expected binding:

| Endpoint | Expected decision | Expected reason |
|---|---|---|
| `esp32-field-01` | `accepted` | `provider_admissible` |
| `esp32-s3-02` | `denied` | `unauthorized_request` |
| `esp32-s3-03` | `denied` | `stale_replay_malformed` |

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

### PASS Criteria

PASS requires the exact expected relationship for every endpoint.

The test fails when:

- A result is assigned to the wrong endpoint
- A decision is correct but its reason is incorrect
- Aggregate counts are correct but per-device binding is wrong
- An endpoint is missing
- An unexpected endpoint appears
- A required denial is converted into acceptance

This is the stronger original fleet test because it verifies more than coordinated completion.

It demonstrates that three different outcomes can remain attached to the correct three physical endpoints through one shared boundary.

## Preserved Harness Failure

An earlier mixed-outcome run produced the correct endpoint outcomes but was marked FAIL because the launcher still used an all-accept PASS rule.

Recorded run:

```text
run_id=18c5b0a38b1d51b0
system outcomes=correct
launcher result=FAIL
cause=all-accept PASS oracle
classification=harness/oracle failure
```

The endpoints and boundary produced the expected mixed results.

The failure was in the launcher oracle.

The corrected launcher evaluates the expected decision and reason for each endpoint individually.

The earlier run remains documented because the test harness itself can produce an incorrect classification.

## Timing

Recorded baseline timing:

```text
Three-accept run: 33–34 ms
Mixed-outcome run: 29–38 ms
```

Normal warmed fleet behavior was generally observed around:

```text
approximately 32–48 ms
```

These values describe the tested environment.

They are not guaranteed performance values for other access points, Raspberry Pi configurations, firmware versions, or radio conditions.

Later stage-timing and wireless-path testing is documented under:

```text
../archer-validation/
```

## Fail-Unavailable Behavior

When the endpoint cannot complete the request path, it must not reinterpret the failure as acceptance.

Expected behavior:

```text
network unavailable
provider unavailable
boundary unavailable
request timeout
malformed response
        |
        v
no accepted result
```

The endpoint may display an unavailable condition, including the white LED state, but it must not produce fallback acceptance.

Fail-unavailable claims apply to the tested paths.

## Known Failed or Superseded Approaches

Several earlier approaches were tested and replaced.

### Concurrent Windows `mpremote`

Earlier launchers attempted to control all three serial ports concurrently through Windows `mpremote`.

That approach produced timeouts.

It was replaced by endpoint-originated outbound polling.

Superseded files include:

```text
run_three_esp32.py
run_three_esp32_v2.py
```

### Inbound UDP Triggering

Inbound UDP triggering was unreliable through the tested access-point path.

The supported fleet retained outbound HTTP polling.

Superseded files include:

```text
esp32_multi_udp_main.py
run_three_esp32_udp.py
```

### Absolute Release Timestamps

The first polling coordinator exchanged an absolute release timestamp between Raspberry Pi Python and MicroPython.

The incompatible epoch representations caused incorrect release timing.

Superseded files include:

```text
multi_endpoint_coordinator.py
esp32_multi_poll_main.py
```

The supported relative-timing versions are:

```text
multi_endpoint_coordinator_v2.py
esp32_multi_poll_main_v2.py
```

## Limitations

The baseline does not establish:

- Parallel processing inside the single-threaded Raspberry Pi boundary
- Correct operation with arbitrary endpoint counts
- Correct operation across arbitrary wireless networks
- Resistance to deliberate radio jamming
- Production readiness
- Safety certification
- Independent reproduction by an external laboratory
- Endpoint-side independent verification of the provider signature

In the baseline architecture, the ESP32-S3 endpoints trust the downstream result returned by the Raspberry Pi.

The Raspberry Pi holds the provider public trust anchor.

The provider retains the private signing key.

The endpoints do not hold the provider private key and do not independently mint provider authority.

However, because the endpoint trusts the Raspberry Pi result, a compromised Raspberry Pi could fabricate the downstream result presented to the endpoint.

That limitation is part of the tested architecture.

## Recommended Test Order

1. Configure the ESP32 firmware for the local network.
2. Prepare the three `device_id.txt` files.
3. Deploy the firmware to one ESP32-S3.
4. Validate the single endpoint with `esp32_multi_once.py`.
5. Deploy the fleet firmware to all three endpoints.
6. Start `nuvl_local_hardened.py`.
7. Start `multi_endpoint_coordinator_v2.py`.
8. Run `run_three_esp32_poll.py`.
9. Confirm the three-accept baseline.
10. Run `run_three_esp32_mixed.py`.
11. Confirm the exact per-device mixed-outcome binding.
12. Move to the Archer validation tests only after the baseline is stable.

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

Additional logs and manifests are indexed in:

```text
../../evidence/
```

See [`../../evidence/README.md`](../../evidence/README.md) for the current evidence set.
