# NUVL Edge Fleet Baseline

This directory contains the original three-endpoint NUVL fleet implementation used before the later latency investigation and Archer validation work.

It is the primary starting point for reproducing the NUVL Edge Lab fleet path.

The baseline uses:

- Three physical ESP32-S3 endpoints
- One Raspberry Pi fleet coordinator
- One Raspberry Pi NUVL verification boundary
- Outbound HTTP polling from each endpoint
- Per-device identity stored in `device_id.txt`
- Per-device decision and reason validation at the launcher

The baseline demonstrates that multiple constrained endpoints can share one verification boundary while preserving the relationship between:

```text
endpoint identity
assigned request mode
decision
reason
reported result
```

## Demonstrated Property

The fleet baseline separates endpoint capability from provider-controlled authority.

Each ESP32-S3 can:

- Identify itself
- Receive a coordinated test assignment
- Create a request
- Submit the request to the NUVL boundary
- Receive a decision and reason
- Render the result through its RGB LED
- Report the result to the fleet coordinator

The endpoint does not independently create provider authority.

The baseline demonstrates:

- Three-endpoint coordinated operation
- Correct endpoint identity binding
- Correct decision and reason binding
- Mixed accepted and denied outcomes
- No cross-assignment of one endpoint's result to another endpoint
- One shared verification boundary
- Fail-unavailable behavior when the request path cannot complete

## Architecture

```text
Windows control host
        |
        | starts fleet launcher
        v
Raspberry Pi fleet coordinator
        |
        | run_id
        | mode
        | relative wait_ms
        v
Three ESP32-S3 endpoints
        |
        | POST /nuvl
        v
Raspberry Pi verification boundary
        |
        | decision
        | reason
        v
ESP32-S3 endpoint report
        |
        v
Fleet coordinator
        |
        v
Windows launcher evaluates PASS or FAIL
```

Primary ports:

| Port | Service |
|---:|---|
| `8089` | NUVL verification boundary |
| `19052` | Fleet coordinator |

The original verification boundary uses Python `HTTPServer` and is single-threaded.

The fleet tests demonstrate coordinated fan-in through one shared boundary. They do not claim parallel request processing inside the Raspberry Pi boundary.

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

## File Roles

### `boundary/nuvl_local_hardened.py`

Runs the Raspberry Pi NUVL verification boundary.

The baseline boundary accepts requests at:

```text
POST /nuvl
```

The tested modes produce the following decision and reason pairs:

```text
accepted / provider_admissible
denied / unauthorized_request
denied / stale_replay_malformed
```

The boundary is the shared downstream decision point for all three endpoints.

### `coordinator/multi_endpoint_coordinator_v2.py`

Runs the fleet coordinator.

The coordinator:

- Creates or tracks a fleet run
- Assigns a request mode to each endpoint
- Assigns a relative `wait_ms`
- Receives endpoint results
- Preserves the relationship between run ID and endpoint identity
- Makes the collected results available to the launcher

The `v2` coordinator uses relative timing.

An earlier coordinator used an absolute timestamp. That design was superseded because Raspberry Pi Python and MicroPython represented epochs differently.

### `firmware/esp32_multi_poll_main_v2.py`

Main fleet firmware for each ESP32-S3.

The firmware:

1. Reads the endpoint identity from `device_id.txt`
2. Connects to Wi-Fi
3. Polls the fleet coordinator
4. Receives a `run_id`, mode, and relative `wait_ms`
5. Waits locally for the assigned release interval
6. Creates the request
7. Posts the request to `/nuvl`
8. Receives a decision and reason
9. Reports the result to the coordinator
10. Returns to polling

The same firmware is used on all three endpoints.

The board-specific identity comes from `device_id.txt`.

### `firmware/esp32_multi_once.py`

Single-endpoint diagnostic client.

Use this before changing fleet logic when one board is missing, late, or unable to complete the normal path.

It is intended to help isolate:

- Board identity
- Wi-Fi connectivity
- Raspberry Pi reachability
- Boundary reachability
- Decision parsing
- LED behavior
- Basic request latency

### `launchers/run_three_esp32_poll.py`

Runs the original three-endpoint accepted baseline.

Expected result:

```text
esp32-field-01 -> accepted / provider_admissible
esp32-s3-02    -> accepted / provider_admissible
esp32-s3-03    -> accepted / provider_admissible
```

### `launchers/run_three_esp32_mixed.py`

Runs the mixed-outcome fleet test.

Expected result:

```text
esp32-field-01 -> accepted / provider_admissible
esp32-s3-02    -> denied / unauthorized_request
esp32-s3-03    -> denied / stale_replay_malformed
```

This launcher evaluates the expected result for each endpoint individually.

Aggregate counts alone cannot earn PASS.

### `endpoint-config/*/device_id.txt`

Stores the durable endpoint identity.

Confirmed identities:

```text
esp32-field-01
esp32-s3-02
esp32-s3-03
```

Each physical endpoint receives only its own `device_id.txt`.

## Physical Endpoint Setup

Each ESP32-S3 should contain:

```text
main.py
device_id.txt
```

Deploy:

```text
firmware/esp32_multi_poll_main_v2.py
```

to the board as:

```text
main.py
```

Then copy the matching identity file.

Example:

```text
esp32-field-01/
├── main.py
└── device_id.txt
```

The contents of that board's identity file are:

```text
esp32-field-01
```

Repeat with the other two identities.

## Durable Identity Versus COM Port

The endpoint identity is the value stored in:

```text
device_id.txt
```

COM port numbers are temporary Windows bench mappings.

One recorded mapping was:

```text
COM5  -> esp32-field-01
COM9  -> esp32-s3-02
COM12 -> esp32-s3-03
```

Those COM numbers may change after reconnecting the boards, rebooting Windows, changing USB ports, or reinstalling a driver.

Do not use the COM number as the endpoint identity.

## Network Configuration

Public source copies should use explicit placeholders:

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

A reproducer must replace the network values with settings appropriate to the local environment.

A sanitized public source file is not byte-identical to the original tested file.

Do not reuse the original tested-source hash for a modified public copy.

## Service Startup

Start the Raspberry Pi services before running the Windows launcher.

From the applicable Raspberry Pi working directory:

```bash
python3 nuvl_local_hardened.py
```

In a second terminal:

```bash
python3 multi_endpoint_coordinator_v2.py
```

Confirm that:

- The boundary is listening on port `8089`
- The coordinator is listening on port `19052`
- The ESP32-S3 devices can reach the Raspberry Pi
- Each endpoint reports its expected durable identity

The exact Raspberry Pi address must match the value configured in the public firmware copy.

## LED States

The ESP32-S3 onboard RGB LED provides a physical representation of endpoint state.

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

The LED displays the result. It is not an authority source.

## Test 1: Three-Endpoint Accepted Baseline

Run:

```bash
python run_three_esp32_poll.py
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

- Three expected endpoint responses
- Correct endpoint identity for each response
- Correct endpoint IP association
- Three `accepted` decisions
- Three `provider_admissible` reasons
- No missing endpoint
- No duplicate endpoint
- No result assigned to the wrong endpoint

A run with only two responses is not PASS.

A run with three accepted counts but incorrect endpoint binding is not PASS.

## Test 2: Three-Endpoint Mixed Outcomes

Run:

```bash
python run_three_esp32_mixed.py
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

### PASS Criteria

PASS requires the exact expected relationship for every endpoint:

| Endpoint | Expected decision | Expected reason |
|---|---|---|
| `esp32-field-01` | `accepted` | `provider_admissible` |
| `esp32-s3-02` | `denied` | `unauthorized_request` |
| `esp32-s3-03` | `denied` | `stale_replay_malformed` |

The test fails when:

- A result is assigned to the wrong endpoint
- A decision is correct but its reason is incorrect
- Aggregate accepted and denied counts are correct but per-device binding is wrong
- An endpoint is missing
- An unexpected endpoint appears
- A required denial is converted into acceptance

This is the stronger original fleet test because it proves more than coordinated completion.

It verifies that different decisions remain attached to the correct physical devices.

## Preserved Harness Failure

An earlier mixed-outcome run produced the correct endpoint outcomes but was marked FAIL because the launcher still applied an all-accept PASS rule.

Recorded run:

```text
run_id=18c5b0a38b1d51b0
system outcomes=correct
launcher result=FAIL
cause=all-accept PASS oracle
classification=harness/oracle failure
```

The architecture produced the expected mixed results.

The failure was in the launcher oracle.

The corrected launcher evaluates the expected decision and reason for each device individually.

This failure remains documented because a test harness can misclassify a correct system result.

## Timing

Recorded original baseline timing:

```text
Three-accept run: 33–34 ms
Mixed-outcome run: 29–38 ms
```

Normal warmed fleet behavior was generally observed in approximately:

```text
32–48 ms
```

These values describe the tested environment.

They are not guaranteed performance values for other access points, Raspberry Pi configurations, radio conditions, or firmware versions.

Later stage-timing and wireless-path investigation files belong under:

```text
../archer-validation/
```

They should not be substituted for the original fleet baseline.

## Fail-Unavailable Behavior

When the endpoint cannot complete the request path, it must not reinterpret the failure as acceptance.

Expected failure behavior:

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

The endpoint may display an unavailable state, including the white LED condition, but it must not produce fallback acceptance.

Claims about fail-closed or fail-unavailable behavior apply to the tested paths.

## Source Classification

Each published source file should be classified as one of the following.

### Original tested source

The exact file used during the recorded test.

### Sanitized public derivative

A copy modified to remove credentials, personal values, or environment-specific configuration.

### Rerun-confirmed public source

A sanitized or reorganized public copy that was executed again and confirmed against the documented PASS criteria.

Do not attach an original tested hash to a modified public file.

Each finalized public copy receives its own SHA-256 in:

```text
../../evidence/SHA256SUMS.txt
```

The public-copy hashes can be generated after the files are finalized.

## Known Failed or Superseded Approaches

The following files or approaches are not part of the supported baseline.

### Concurrent Windows `mpremote`

Earlier launchers attempted concurrent Windows serial control across all three endpoints.

That approach produced timeouts and was replaced by endpoint-originated outbound polling.

Superseded examples include:

```text
run_three_esp32.py
run_three_esp32_v2.py
```

### Inbound UDP Triggering

Inbound UDP triggering was unreliable through the tested access-point path.

The supported fleet retained outbound HTTP polling.

Superseded examples include:

```text
esp32_multi_udp_main.py
run_three_esp32_udp.py
```

### Absolute Timestamp Coordination

The first polling coordinator exchanged an absolute release timestamp between Raspberry Pi Python and MicroPython.

The incompatible epoch representations caused incorrect release timing.

Superseded examples include:

```text
multi_endpoint_coordinator.py
esp32_multi_poll_main.py
```

The supported versions are:

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
- Protection against a compromised Raspberry Pi fabricating a result to the endpoint

In the original fleet design, the ESP32 trusts the downstream Raspberry Pi decision.

The Raspberry Pi holds the provider public trust anchor, while the provider retains the private signing key.

The ESP32 does not hold the provider private key and does not independently mint provider authority.

However, because the endpoint trusts the Raspberry Pi result, a compromised Raspberry Pi could fabricate the local result presented to the endpoint.

That limitation is part of the architecture and should remain visible.

## Recommended Reproduction Order

1. Review the network placeholders in the firmware.
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
12. Preserve the launcher output and run ID.
13. Move to Archer isolation, outage, or latency tests only after the baseline is stable.

## Evidence

Current baseline run identifiers:

```text
Three-accept baseline:
18c565fc0e9dfd5c

Mixed-outcome PASS:
18c5b11e874cd4cc

Mixed-outcome harness failure:
18c5b0a38b1d51b0
```

These run IDs identify recorded results but are not substitutes for the underlying evidence files.

Fleet evidence should be added under:

```text
../../evidence/
```

only after the exact logs are located, reviewed, and hashed.

See:

```text
../../evidence/README.md
```

for the evidence policy and verification procedure.
