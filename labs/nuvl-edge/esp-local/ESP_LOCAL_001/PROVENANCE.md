# ESP-LOCAL-001 Provenance

## Test Identity

**Test:** ESP-LOCAL-001  
**Result:** PASS  
**Purpose:** Endpoint-local bounded-authority admissibility recognition with independently witnessed physical command issuance.

## Test Environment

The test was executed using:

- Seeed XIAO ESP32-S3 endpoint
- ESP32-S3 DevKit independent PWM witness
- Local Wi-Fi network
- HTTP request path directly to the endpoint
- Servo control output on GPIO5

The endpoint under test was identified as:

```text
esp32-xiao-servo-01
```

The configured test context was:

```text
esp_local_demo
```

The authorized action was:

```text
move_servo
```

## Endpoint Firmware

The endpoint firmware used for the final test state was:

```text
esp_local_001_main.py
```

SHA-256:

```text
0F84521FA85A6EA439DFA6B464C69D9DA53E788365C737318ECA5F7140822FDD
```

The final implementation required the exact request key set:

```text
device_id
context
action
```

Requests containing unexpected fields were denied.

## Witness Firmware

The independent witness firmware was:

```text
esp_local_001_witness.py
```

SHA-256:

```text
AF380567C2FA6E961C1A029073BDD15FB7C39CE0034A80C554DC6709DD0F8AC4
```

The witness monitored the endpoint servo PWM signal and independently recorded command bursts.

## Pre-Test Endpoint Firmware

Before ESP-LOCAL-001 firmware was installed, the existing endpoint firmware was preserved as:

```text
esp32_xiao_servo_01_pre_esp_local_main.py
```

SHA-256:

```text
8D6F6B6CA1BEB093FC5559381F30700AF9A338685DEEDBAB7D65BF72D6D96C7E
```

The preserved firmware represented the earlier actuator configuration in which the endpoint relied on an external recognition path.

## Evidence Record

The curated evidence record is:

```text
ESP_LOCAL_001_EVIDENCE.log
```

SHA-256:

```text
9ED7508F0B980496FC96B08E924B288D7ED517BE455065AAACB5A2C52769676F
```

The evidence record contains the final semantic results, the representation-ambiguity defect and correction, accepted-path witness output, and denied-path witness observations.

## Artifact Relationship

The publication artifacts represent the final tested ESP-LOCAL-001 implementation and its corresponding witness and evidence record.

The endpoint firmware hash identifies the corrected implementation used for the final result.

The witness firmware hash identifies the independent observation implementation used to record PWM command issuance.

The evidence record is a curated test record derived from observed terminal and witness output. It is not represented as a raw continuous terminal capture.

## Integrity

The published ESP-LOCAL-001 artifacts are covered by the accompanying:

```text
SHA256SUMS.txt
```
