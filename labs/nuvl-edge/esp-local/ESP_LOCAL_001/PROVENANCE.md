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

Tested-source SHA-256:

```text
0F84521FA85A6EA439DFA6B464C69D9DA53E788365C737318ECA5F7140822FDD
```

Published-copy SHA-256:

```text
6c21bad9b4ba789dee4e6734ca5298e160c218735cb43eaf23a1c20a85e3be5d
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

Tested-source SHA-256:

```text
AF380567C2FA6E961C1A029073BDD15FB7C39CE0034A80C554DC6709DD0F8AC4
```

Published-copy SHA-256:

```text
4cd13da81a5b7313fb0647c0ec9ba87709effbcb4ce7a8eecc30cfc4d88e13af
```

The witness monitored the endpoint servo PWM signal and independently recorded command bursts.

## Pre-Test Endpoint Firmware

Before ESP-LOCAL-001 firmware was installed, the existing endpoint firmware was preserved as:

```text
esp32_xiao_servo_01_pre_esp_local_main.py
```

Preserved-source SHA-256:

```text
8D6F6B6CA1BEB093FC5559381F30700AF9A338685DEEDBAB7D65BF72D6D96C7E
```

The preserved firmware represented the earlier actuator configuration in which the endpoint relied on an external recognition path.

This preserved pre-test artifact is recorded for test lineage and is not part of the ESP-LOCAL-001 publication manifest.

## Evidence Record

The curated bench evidence record is:

```text
ESP_LOCAL_001_EVIDENCE.log
```

Tested-source SHA-256:

```text
9ED7508F0B980496FC96B08E924B288D7ED517BE455065AAACB5A2C52769676F
```

Published-copy SHA-256:

```text
9edf493364563e256bd3ae5d12705d2b1a332a93e989569729ee4d041b0e7d7e
```

The evidence record contains the final semantic results, the representation-ambiguity defect and correction, accepted-path witness output, and denied-path witness observations.

The evidence record is a curated test record derived from observed terminal and witness output. It is not represented as a raw continuous terminal capture.

## Artifact Relationship

The tested-source digests identify the bench-side artifacts associated with the completed ESP-LOCAL-001 test.

The published-copy digests identify the corresponding files as stored in the public repository.

Where tested-source and published-copy digests differ, the publication copy is not represented as byte-identical to the bench-side artifact. The separate digests preserve the distinction between test provenance and publication integrity.

The endpoint tested-source digest identifies the corrected implementation used for the final test result.

The witness tested-source digest identifies the independent observation implementation used during the test.

The evidence tested-source digest identifies the curated bench evidence record associated with the result.

The corresponding published-copy digests identify the repository artifacts covered by the publication manifest.

## Integrity

The published ESP-LOCAL-001 artifacts are covered by the accompanying:

```text
SHA256SUMS.txt
```

`SHA256SUMS.txt` records the published-copy digests and paths used for repository integrity verification.
