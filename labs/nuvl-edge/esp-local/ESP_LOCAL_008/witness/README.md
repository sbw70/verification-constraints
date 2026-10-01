
# ESP-LOCAL-008 Witness

## Purpose

The ESP-LOCAL-008 witness independently observes the physical servo-control signal during directionality testing.

The witness has no provider-authority role and no authorization role.

Its function is limited to physical observation:

> Determine whether a servo-like PWM/control signal crossed the monitored physical line during a scored run.

The witness does not decide whether an authority is valid.

It does not verify the provider signature.

It does not inspect endpoint persistent authority state.

It does not cause endpoint acceptance or denial.

The ESP-LOCAL-008 result therefore combines endpoint enforcement evidence with an independently instrumented physical signal boundary.

## Repository Layout

The published witness tree is:

    witness/
    |-- README.md
    |
    `-- ESP_LOCAL_008_WITNESS_RMT_V1/
        |-- CMakeLists.txt
        |-- partitions.csv
        |-- sdkconfig
        |-- sdkconfig.defaults
        |
        `-- main/
            |-- CMakeLists.txt
            |-- cJSON.c
            |-- cJSON.h
            `-- witness_rmt_v1.c

Primary witness source:

    ESP_LOCAL_008_WITNESS_RMT_V1/main/witness_rmt_v1.c

The implementation includes:

- ESP32-S3 RMT RX capture;
- servo-pulse classification;
- burst classification;
- capture-health counters;
- persistent SPIFFS evidence;
- per-session and per-run evidence files;
- SHA-256 run-file hashing;
- UDP control;
- status reporting;
- self-test support.

## Witness Identity

The witness identifies itself as:

    device_id: esp32-witness-007

Network configuration during ESP-LOCAL-008:

    IP:           192.168.0.216
    control port: 19072
    protocol:     UDP

Observed hardware identity:

    MAC:
    44:1b:f6:ff:36:a8

The `007` device identifier is retained because the ESP-LOCAL-008 witness implementation is derived from the independent RMT witness established during ESP-LOCAL-007.

The witness has:

    authority_role:     NONE
    authorization_role: NONE

## Physical Wiring

ESP-LOCAL-008 used two witness-input configurations.

Final physical mapping:

    witness GPIO4 -> Servo #2 signal
    witness GPIO5 -> Servo #1 signal

This GPIO number identifies the witness input pin.

It is separate from the endpoint's local PWM output GPIO numbering.

The endpoint firmware used GPIO5 for the actuator signal on both XIAO ESP32-S3 endpoints.

## Published GPIO Configuration

The currently published source contains:

    #define WITNESS_GPIO GPIO_NUM_5

This corresponds to the final Servo1 witness configuration.

The final Servo2 cases were captured with the same witness implementation built with:

    #define WITNESS_GPIO GPIO_NUM_4

The two builds differ in the selected witness input GPIO.

The scored matrix therefore used:

    Servo1 cases -> witness GPIO5
    Servo2 cases -> witness GPIO4

The single checked-in source snapshot must not be interpreted as evidence that all scored runs used GPIO5.

## Recorded Witness Build Identities

The scored GPIO4 witness application was recorded as:

    SHA-256:
    DE68A458A8B80FA6A27904F8DEFBAEC755C74981E2B3706AF441ED98E98183B2

The recorded GPIO5 witness source configuration was:

    SHA-256:
    FE1BBA2C8B15D437FF7BFAF255A77CC3EFDE085B47F79689473C3A953832EE42

The recorded GPIO5 witness application binary was:

    SHA-256:
    8F90F1695650602C844404E0A5417F39F5C2B5E469EB91333EC490A7BC386BFD

These values identify scored bench artifacts and configurations.

They do not imply that the corresponding application binaries are currently present in the published witness directory.

## Capture Engine

The witness uses the ESP32-S3 RMT receive peripheral:

    capture_engine: rmt_rx

Capture resolution:

    1,000,000 Hz

Equivalent timing resolution:

    1 microsecond

RMT receive configuration:

    RX_IDLE_STOP_US:     30000
    RX_SIGNAL_MIN_NS:    1250
    RX_BUFFER_SYMBOLS:   256
    CAPTURE_QUEUE_DEPTH: 4

The witness records capture-health conditions separately from classified signal events.

## Servo Pulse Classification

A captured high pulse is classified as servo-valid when its width is within:

    minimum: 1500 us
    maximum: 2500 us

Pulses outside that interval are classified as transients.

Servo-like period bounds are:

    minimum: 15000 us
    maximum: 25000 us

Burst separation threshold:

    100000 us

A burst is classified as servo-like when:

- it contains at least three valid servo-width pulses; and
- no measured inter-pulse period is outside the accepted period range.

The classifier therefore distinguishes isolated transitions or malformed timing from a sustained servo-like control sequence.

## Burst Evidence

For each detected burst the witness records fields including:

    burst identifier
    associated run
    first rise time
    last rise time
    last edge time
    duration
    pulse count
    minimum pulse width
    maximum pulse width
    mean pulse width
    minimum period
    maximum period
    period-out-of-range count
    servo_like classification

The physical witness claim is limited to the observed electrical control signal.

A servo-like burst is not an independent measurement of mechanical shaft displacement.

## Capture Health

The witness maintains three capture-health counters:

    capture_overflows
    capture_truncations
    capture_errors

A scored run requires these counters not to increase during the relevant capture interval.

The witness also reports:

    capture_ready
    capture_queue_depth
    rx_buffer_symbols
    capture_filter_min_ns
    pulse_seq
    burst_seq

Capture-health evidence is retained so a zero-signal result is not interpreted as meaningful if the capture path itself failed.

## Evidence Storage

The witness stores evidence in a dedicated SPIFFS partition.

Partition definition:

    evidence,data,spiffs,0x200000,0x400000,

Offset:

    0x00200000

Size:

    0x00400000

Equivalent size:

    4 MiB

Mount path:

    /evidence

Partition label:

    evidence

The storage configuration uses:

    format_if_mount_failed = true

Session and run evidence are written as line-oriented JSON.

## Session Files

Each witness boot creates a session identity containing:

    device identity
    device-specific short UID
    boot counter

Session identifier form:

    esp32-witness-007-<uid>-B####

Session evidence filename form:

    S_<uid>_B####.jl

Example scored-session forms observed during ESP-LOCAL-008 include:

    esp32-witness-007-f6ff36a8-B0064
    esp32-witness-007-f6ff36a8-B0070
    esp32-witness-007-f6ff36a8-B0073

The session file receives general witness events throughout that boot.

## Run Files

A controlled witness run creates a separate run evidence file.

Run filename form:

    R_<RUN_ID>.jl

The witness validates run identifiers before creating the file.

Accepted run-name characters are:

    A-Z
    a-z
    0-9
    -
    _

Maximum run identifier length:

    20 characters

The witness refuses a second START while another run is active.

That condition is reported as:

    run_already_active

## UDP Control Protocol

Control messages use:

    magic: W007
    port:  19072

Supported commands include:

    DISCOVER
    STATUS
    START
    MARK
    SELFTEST
    STOP

The ESP-LOCAL-008 presenter uses the witness primarily through:

    STATUS
    START
    MARK
    STOP

A scored run is bracketed so the physical capture can be associated with one presenter operation.

## START Behavior

START establishes a named run and resets run-local counters.

Run-local evidence includes:

    servo-valid pulse count
    transient count
    burst count
    servo-like burst count
    capture overflow delta
    capture truncation delta
    capture error delta

The witness also records the coordinator-supplied UTC anchor when present.

The implementation requires a quiet interval around run start so signal activity is not ambiguously assigned across run boundaries.

Configured start quiet interval:

    250000 us

## STOP Behavior

STOP waits for the capture path to become quiet before finalizing the run.

Configured quiet-stop timeout:

    1500 ms

The completed run record contains fields including:

    run start time
    run end time
    duration
    coordinator start anchor
    coordinator stop anchor
    servo_valid_pulses
    transients
    bursts
    servo_like_bursts
    quiet-before-stop interval
    capture_overflows_during_run
    capture_truncations_during_run
    capture_errors_during_run

After closing the run file, the witness computes its SHA-256 digest.

The digest is returned to the presenter in the STOP reply.

A `.sha` sidecar is also written to witness storage.

## Final Scored Runs

### X2_S2_DENY_001

Authority scope:

    Servo #1

Presented to:

    Servo #2

Witness input:

    GPIO4

Pre-run:

    pulse_seq: 0
    burst_seq: 0
    capture_overflows: 0
    capture_truncations: 0
    capture_errors: 0

Post-run:

    pulse_seq: 0
    burst_seq: 0
    capture_overflows: 0
    capture_truncations: 0
    capture_errors: 0

Run-file SHA-256 returned by witness:

    ffa3a7b598e55d871b1114dc77123e5e2674cafeec2ef858f89a2a595ce0b4a6

Physical result:

    no observed target-line control signal

### Y2_S2_ACCEPT_001

Authority scope:

    Servo #2

Presented to:

    Servo #2

Witness input:

    GPIO4

Pre-run:

    pulse_seq: 0
    burst_seq: 0
    capture_overflows: 0
    capture_truncations: 0
    capture_errors: 0

Post-run:

    pulse_seq: 49
    burst_seq: 1
    capture_overflows: 0
    capture_truncations: 0
    capture_errors: 0

Run-file SHA-256 returned by witness:

    1756bacf8d53c0336137f78876e91a0f42a3d204441850c6c7263bf47447930b

Physical result:

    one observed servo-like control-signal burst

### X3_S1_ACCEPT_001

Authority scope:

    Servo #1

Presented to:

    Servo #1

Witness input:

    GPIO5

Pre-run:

    pulse_seq: 0
    burst_seq: 0
    capture_overflows: 0
    capture_truncations: 0
    capture_errors: 0

Post-run:

    pulse_seq: 49
    burst_seq: 1
    capture_overflows: 0
    capture_truncations: 0
    capture_errors: 0

Run-file SHA-256 returned by witness:

    1b7247e7f4639556b66a3db3f14c4054229cd724dfb180107f1b7b645124021d

Physical result:

    one observed servo-like control-signal burst

### Y3_S1_DENY_001

Authority scope:

    Servo #2

Presented to:

    Servo #1

Witness input:

    GPIO5

Pre-run:

    pulse_seq: 0
    burst_seq: 0
    capture_overflows: 0
    capture_truncations: 0
    capture_errors: 0

Post-run:

    pulse_seq: 0
    burst_seq: 0
    capture_overflows: 0
    capture_truncations: 0
    capture_errors: 0

Run-file SHA-256 returned by witness:

    8c1f95aa2acaec4c97cace8461892cab3c737e4651c134946a3ec9452694adeb

Physical result:

    no observed target-line control signal

## Final Witness Matrix

| Run | Target | Witness GPIO | Pulses | Bursts | Capture Faults | Physical Result |
|---|---|---:|---:|---:|---:|---|
| `X2_S2_DENY_001` | Servo2 | 4 | 0 | 0 | 0 | no signal |
| `Y3_S1_DENY_001` | Servo1 | 5 | 0 | 0 | 0 | no signal |
| `X3_S1_ACCEPT_001` | Servo1 | 5 | 49 | 1 | 0 | one servo-like burst |
| `Y2_S2_ACCEPT_001` | Servo2 | 4 | 49 | 1 | 0 | one servo-like burst |

The final matrix therefore produced the expected physical directionality pattern:

    wrong target -> no target-line control burst
    correct target -> one target-line control burst

## Superseded Physical-Witness Cases

### Y2_S1_DENY_001

The endpoint correctly denied the wrong-target authority.

The witness was configured on GPIO4 while the Servo1 signal was physically connected to witness GPIO5.

The endpoint and state evidence remain useful, but that run does not support the final Servo1 physical zero-signal claim.

It was replaced by:

    Y3_S1_DENY_001

### X2_S1_ACCEPT_001

The endpoint correctly accepted and executed the Servo1-targeted authority.

The witness was configured on GPIO4 instead of the Servo1 signal connected to GPIO5.

The endpoint-side result remains useful, but that run does not support the final independently witnessed Servo1 positive physical result.

It was replaced by:

    X3_S1_ACCEPT_001

## Control Artifact

### Y3_S1_DENY_002

The endpoint response reported:

    denied
    target_id_mismatch

The witness START reply reported:

    run_already_active

The run therefore did not establish a fresh independent witness bracket.

It is retained under:

    evidence/controls/

and is excluded from the final scored witness matrix.

## Witness Partition Images

Full witness evidence-partition images are retained under:

    evidence/witness-images/

Recorded scored evidence images include:

    ESP_LOCAL_008_WITNESS_AFTER_Y2_PASS.bin

SHA-256:

    BC1DC3B46758BAA7AE470F10557F638AB43584DBA191D410D978ADDC4D0935D1

Recorded after the Servo1 X3 positive case:

    ESP_LOCAL_008_WITNESS_AFTER_X3_PASS.bin

SHA-256:

    393FC673A41E9E99F0B7FE7994B818D04FBB551D151361B448415EF3745CECF1

Recorded after the Servo1 Y3 wrong-target case:

    ESP_LOCAL_008_WITNESS_AFTER_Y3_DENY.bin

SHA-256:

    28AF6266B49C6C56605C91DC437D7886474AB663875A5143195FA82F7A500458

These are complete raw images of the dedicated witness evidence partition.

## Self-Test

The witness implementation contains a local self-test output on:

    GPIO6

The self-test emits approximately:

    50 pulses
    2000 us high
    approximately 20 ms period

The self-test requires an active run.

The self-test path is independent of provider authority and is used only to validate witness capture behavior.

It is not part of the ESP-LOCAL-008 scored directionality result.

## Wi-Fi Configuration

The witness source includes:

    #include "witness_wifi_config.h"

The local Wi-Fi credential header is not checked into the ESP-LOCAL-008 witness directory.

The implementation expects macros compatible with:

    W007_WIFI_SSID
    W007_WIFI_PASSWORD

A local configuration header has the form:

    #pragma once

    #define W007_WIFI_SSID     "<TEST_WIFI_SSID>"
    #define W007_WIFI_PASSWORD "<TEST_WIFI_PASSWORD>"

The Wi-Fi password is bench configuration and is not part of the authority or witness property under test.

## Build Configuration

The witness targets:

    ESP32-S3

The published `sdkconfig.defaults` specifies:

    CONFIG_IDF_TARGET="esp32s3"
    CONFIG_PARTITION_TABLE_CUSTOM=y
    CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="partitions.csv"
    CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y
    CONFIG_ESPTOOLPY_FLASHMODE_DIO=y
    CONFIG_ESPTOOLPY_FLASHFREQ_80M=y
    CONFIG_FREERTOS_HZ=1000
    CONFIG_RMT_RX_ISR_CACHE_SAFE=y
    CONFIG_RMT_RECV_FUNC_IN_IRAM=y

Observed scored witness boot environment included:

    ESP-IDF v6.1
    flash size: 16 MB

## Evidence Boundary

The witness does not prove authorization correctness by itself.

A zero-pulse witness result does not identify why an endpoint refused execution.

A positive pulse burst does not prove that the provider authority was valid or correctly consumed.

Those properties are established by the endpoint and provider evidence.

The witness contributes an independent answer to one narrower question:

> Did an electrical servo-control signal cross the monitored physical boundary during this run?

ESP-LOCAL-008 requires this observation to agree with the endpoint enforcement result.

## Scope

The final witness evidence supports the following physical-boundary observations in the tested configuration:

    wrong-target Servo2 presentation -> zero signal on Servo2 line
    correct-target Servo2 presentation -> one servo-like burst on Servo2 line

    wrong-target Servo1 presentation -> zero signal on Servo1 line
    correct-target Servo1 presentation -> one servo-like burst on Servo1 line

The evidence supports a control-signal claim.

It does not independently establish mechanical servo movement, actuator load, torque, position, or downstream physical effect.
