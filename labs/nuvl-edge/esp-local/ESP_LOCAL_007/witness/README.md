# ESP-LOCAL-007 Independent Witness

This directory contains the ESP-IDF firmware for the independent hardware witness used by ESP-LOCAL-007.

The witness has no authority or authorization role. It observes the endpoint's physical servo-control signal electrically and records pulse-level evidence independently of the endpoint and coordinator.

## Directory contents

~~~text
witness/
├── CMakeLists.txt
├── partitions.csv
├── sdkconfig
└── main/
    ├── cJSON.c
    ├── cJSON.h
    ├── witness_rmt_v1.c
    └── witness_wifi_config.example.h
~~~

## `witness_rmt_v1.c`

`witness_rmt_v1.c` implements the ESP-LOCAL-007 RMT hardware witness.

The tested witness identifies itself as:

~~~text
esp32-witness-007
~~~

Its primary interfaces are:

~~~text
Observed signal: GPIO4
Self-test output: GPIO6
Control: UDP port 19072
Capture engine: ESP-IDF RMT RX
RMT resolution: 1 MHz
~~~

GPIO4 is electrically connected to the endpoint servo-control output during the scored test.

The witness does not receive the provider authority, verify its signature, inspect endpoint persistent state, or participate in the decision to execute the servo command.

Its function is measurement.

## Why RMT capture is used

The original ESP-LOCAL-007 witness implementation used a MicroPython interrupt/Python-queue capture path.

That implementation was adequate to detect activity but did not capture the R001 servo burst completely enough to satisfy the independent physical-witness criterion.

The witness was therefore replaced with this ESP-IDF RMT RX implementation.

RMT performs pulse capture independently of Python scheduling and provides hardware-timed pulse durations to the witness processing tasks.

The scored R003 run used this RMT witness.

## Pulse classification

The witness classifies a captured high pulse as servo-valid when its width is within:

~~~text
1500 µs <= pulse width <= 2500 µs
~~~

Other captured high pulses are classified as transients.

Expected servo periods are bounded by:

~~~text
15000 µs <= period <= 25000 µs
~~~

A burst is closed after:

~~~text
100000 µs
~~~

without another valid servo pulse.

A closed burst is classified as servo-like when:

~~~text
pulse count >= 3
period_out_of_range == 0
~~~

The classification therefore depends on observed electrical pulse shape and repetition, not on endpoint log messages or requester responses.

## Capture path

The RMT receiver is configured with:

~~~text
GPIO:                 4
resolution:           1,000,000 Hz
RX idle stop:         30,000 µs
RX buffer:            256 symbols
capture queue depth:  4
~~~

Capture is split between acquisition and processing tasks.

The RMT completion callback places received data into the acquisition path. Captured symbols are copied into a processing queue and decoded into high-pulse observations.

The witness tracks capture-health counters for:

- capture overflows;
- capture truncations; and
- capture errors.

These counters are included in status and run evidence.

A scored observation requires the capture-health counters relevant to the run to remain zero.

## Timing basis

Pulse widths and periods are derived from RMT symbol durations.

The witness also records estimated absolute edge times. These are reconstructed from the RMT receive-completion time, configured idle-stop interval, and captured symbol durations.

The evidence explicitly records this property as:

~~~text
absolute_edge_time_estimated = true
edge_time_basis = rx_done_minus_idle_stop_minus_captured_durations
~~~

Absolute edge timestamps should therefore be interpreted according to that reconstruction method. Pulse widths and periods are the primary physical-signal measurements.

## Burst evidence

For each detected burst, the witness records a `burst_end` event containing fields including:

- burst identifier;
- associated run identifier;
- closure reason;
- first and last rise times;
- final pulse end;
- burst duration;
- pulse count;
- minimum pulse width;
- maximum pulse width;
- mean pulse width;
- minimum period;
- maximum period;
- out-of-range period count; and
- `servo_like` classification.

This raw burst record is the witness's direct classification of the observed physical event.

## Run control

The witness exposes a UDP control interface on port `19072`.

Commands use the control prefix:

~~~text
W007
~~~

Supported commands are:

~~~text
W007 DISCOVER
W007 STATUS
W007 START <run-id> <UTC-anchor>
W007 MARK <text>
W007 SELFTEST
W007 STOP <UTC-anchor>
~~~

### `DISCOVER`

Returns witness identity and status information for discovery.

### `STATUS`

Returns current witness state, including:

- IP address;
- connection state;
- control port;
- witness GPIO;
- capture engine;
- capture readiness;
- queue depth;
- capture overflow count;
- capture truncation count;
- capture error count;
- RMT buffer size;
- capture filter;
- pulse sequence;
- burst sequence; and
- current session file.

### `START`

Begins a named evidence run.

Run identifiers are restricted to 20 characters and may contain:

~~~text
A-Z
a-z
0-9
-
_
~~~

The witness records the coordinator-provided UTC anchor alongside its own monotonic timing.

### `MARK`

Adds a coordinator-supplied marker to the active evidence stream.

ESP-LOCAL-007 uses this to correlate coordinator events with independently recorded witness activity.

### `STOP`

Closes the active run after the capture path becomes quiet.

The witness waits for:

- the required quiet interval;
- an empty capture queue; and
- closure of any active burst.

If the capture path does not become quiet, STOP fails rather than silently finalizing an incomplete active burst.

After successful closure, the run file is hashed with SHA-256 and a `.sha` sidecar is written.

## Self-test

GPIO6 provides a local witness self-test output.

`SELFTEST` requires an active run and generates:

~~~text
50 pulses
2000 µs high
approximately 20 ms period
~~~

GPIO6 can be temporarily connected to GPIO4 to validate the complete RMT capture and classification path.

The self-test loopback is a validation configuration, not the scored witness configuration.

Before a scored endpoint run, the GPIO6-to-GPIO4 loopback must be removed so GPIO4 observes the endpoint rather than the witness's own test output.

The host-side `coordinator/witness_loopback_check.py` utility is provided to verify that this temporary loopback has been removed.

## Evidence storage

The witness uses a dedicated SPIFFS partition labeled:

~~~text
evidence
~~~

The published partition table is:

| Name | Type | Subtype | Offset | Size |
|---|---|---|---:|---:|
| `nvs` | data | nvs | `0x9000` | `0x6000` |
| `phy_init` | data | phy | `0xf000` | `0x1000` |
| `factory` | app | factory | `0x10000` | `0x1F0000` |
| `evidence` | data | spiffs | `0x200000` | `0x400000` |

The evidence partition therefore reserves 4 MiB for witness evidence.

SPIFFS is mounted at:

~~~text
/evidence
~~~

The witness creates a session evidence file for each boot and a separate evidence file for each named run.

Events are emitted as compact JSON lines to:

- the serial console;
- the active session file; and
- the active run file, when a run is active.

Writes are flushed during operation, and run closure synchronizes the evidence before hashing it.

## Evidence integrity

When a run closes successfully, the witness computes SHA-256 over the completed run file.

It then creates a sidecar containing:

~~~text
<sha256>  <run-filename>
~~~

A `run_file_closed` event records:

- completed run ID;
- evidence filename;
- SHA-256 digest; and
- sidecar filename.

This allows the exported witness run artifact to be checked independently after collection.

## Session identity

Each witness boot receives a session identifier derived from:

- device ID;
- part of the Wi-Fi station MAC address; and
- a persistent boot counter.

The boot counter is stored in NVS.

Session and run records also include the witness's monotonic `esp_timer` time so events within the same boot can be ordered independently of coordinator wall-clock timestamps.

## Wi-Fi configuration

`main/witness_wifi_config.example.h` contains the publication template:

~~~c
#pragma once
// Copy to witness_wifi_config.h and set your own Wi-Fi password.
#define W007_WIFI_SSID     "Xer0trust 2.4"
#define W007_WIFI_PASSWORD "REDACTED_SET_YOUR_OWN"
~~~

A reproduction build requires:

~~~text
main/witness_wifi_config.h
~~~

with the local Wi-Fi credentials.

The real lab Wi-Fi password is not included in the published source.

## Build

The ESP-IDF project is defined as:

~~~text
ESP_LOCAL_007_WITNESS_RMT_V1
~~~

The checked-in `sdkconfig` preserves the configuration associated with the published witness build.

The project uses the ESP-IDF RMT RX driver for signal capture and includes local `cJSON.c` and `cJSON.h` sources for JSON evidence generation.

## Independence boundary

The witness is intentionally outside the authority path.

Its firmware identifies its roles as:

~~~text
authority_role = NONE
authorization_role = NONE
~~~

It does not know whether a requester should be accepted.

It does not know whether an authority is `UNSPENT` or `SPENT`.

It does not receive the provider private key.

It does not tell the endpoint to execute.

It records whether the electrical signal associated with physical servo execution occurred.

This separation allows endpoint enforcement evidence and physical execution evidence to be compared without relying on the endpoint to attest to its own physical output.
