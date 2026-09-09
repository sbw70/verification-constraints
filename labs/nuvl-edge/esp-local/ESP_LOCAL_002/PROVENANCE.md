# ESP-LOCAL-002 Provenance

## Test Identity

**Test:** ESP-LOCAL-002  
**Result:** PASS  
**Purpose:** Endpoint-local recognition and single-use consumption of an externally generated bearer capability with independently witnessed physical command issuance.

## Test Environment

The test was executed using:

- Seeed XIAO ESP32-S3 endpoint
- ESP32-S3 DevKit independent PWM witness
- Local Wi-Fi network
- HTTP request path directly to the endpoint
- External capability-generation utility
- Servo control output on GPIO5

The endpoint under test was identified as:

```text
esp32-xiao-servo-01
```

The configured test context was:

```text
esp_local_002
```

The authorized action was:

```text
move_servo
```

## Capability Source

The external capability-generation utility was:

```text
esp_local_002_provider.py
```

Tested-source SHA-256:

```text
175F571A938991B70A8C4ADF9D58864D179FA91CB70F4477F0717CB2C173C723
```

Published-copy SHA-256:

```text
d4ed191d8be8d9ba0bfaf23bae7359d5df4327f42aabad48323857643cc5ab1b
```

The utility generated a random 256-bit bearer capability:

```text
8b20574c6ba2330e4a4b94e91e1a1669c585b7d86c95e5592bd018ff42337e3e
```

The corresponding SHA-256 commitment was:

```text
700775b2bd9fd36b8f0c5f6e5072297a6e6df30bbfb24b49fbf9e88960ad18ae
```

The endpoint stored the commitment rather than the bearer capability value.

## Endpoint Firmware

The endpoint firmware used for the final test state was:

```text
esp_local_002_main.py
```

Tested-source SHA-256:

```text
15938CBB3842BD6BFFF21F54CFD6FEEBE8BFC0E98BE1A24A236ECBBAE87D4874
```

Published-copy SHA-256:

```text
35ae53417de32cac375b414d7582c9cb9c379d9203cb6e4c23cd2316904b40d1
```

The endpoint required the exact request key set:

```text
device_id
context
action
capability
```

The endpoint independently checked:

```text
device_id = esp32-xiao-servo-01
context   = esp_local_002
action    = move_servo
SHA-256(capability) = stored commitment
capability_spent = false
```

The capability-spent state was maintained in endpoint RAM.

For an accepted request, the implementation marked the capability spent before physical command issuance.

## Witness Firmware

The independent witness firmware used during the test was:

```text
esp_local_002_witness.py
```

Tested-source SHA-256:

```text
AF380567C2FA6E961C1A029073BDD15FB7C39CE0034A80C554DC6709DD0F8AC4
```

Published-copy SHA-256:

```text
4cd13da81a5b7313fb0647c0ec9ba87709effbcb4ce7a8eecc30cfc4d88e13af
```

The tested witness implementation was the same witness implementation used for ESP-LOCAL-001.

The published witness copy is not represented as byte-identical to the tested-source artifact because its published-copy digest differs from the tested-source digest.

The witness monitored the endpoint servo PWM signal and independently recorded command bursts.

## Observed Accepted Path

Following endpoint reset to establish an unspent runtime state, the valid capability was presented with the expected device, context, and action.

The endpoint returned:

```text
accepted
authority_admissible
```

The witness recorded:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=236837
ESP_LOCAL_001_WITNESS_BURST_END pulses=50 duration_ms=980 pulse_min_us=1792 pulse_max_us=2001
```

This established one independently observed PWM command burst associated with the accepted first presentation.

## Observed Replay Path

The exact same request and bearer capability were presented again without resetting the endpoint.

The endpoint returned:

```text
decision=denied
reason=capability_spent
```

No additional PWM burst was observed.

The witness remained `IDLE` through at least:

```text
ESP_LOCAL_001_WITNESS_HEARTBEAT ticks_ms=355095 state=IDLE
```

## Additional Semantic Results

The final endpoint implementation also produced the expected denials for:

```text
invalid capability
wrong device
wrong context
unauthorized action
```

The observed reasons were:

```text
capability_invalid
wrong_device
wrong_context
action_not_authorized
```

## Evidence Record

The curated bench evidence record is:

```text
ESP_LOCAL_002_EVIDENCE.log
```

Tested-source SHA-256:

```text
8B66231145627977D47127992B9380287A31CFF8DC5378CB7DEB33474842187A
```

Published-copy SHA-256:

```text
08dbdd0e43223306168d2cfa7b62b644d29e6eed04f1e77fb8622a23054357b1
```

The evidence record contains:

- test objective and topology;
- capability and commitment values;
- semantic decision results;
- accepted-path witness output;
- replay-denial output;
- denied-path witness observations;
- supported claim; and
- explicit claim boundaries.

The evidence record is a curated record assembled from observed terminal and witness output. It is not represented as a raw continuous terminal capture.

## Artifact Relationship

The tested-source digests identify the bench-side artifacts associated with the completed ESP-LOCAL-002 test.

The published-copy digests identify the corresponding files as stored in the public repository.

Where tested-source and published-copy digests differ, the publication copy is not represented as byte-identical to the bench-side artifact. The separate digests preserve the distinction between test provenance and publication integrity.

The provider tested-source digest identifies the external capability-generation implementation associated with the test.

The endpoint tested-source digest identifies the implementation that performed endpoint-local recognition and RAM-based single-use consumption during the test.

The witness tested-source digest identifies the independent electrical observation implementation used during the test.

The evidence tested-source digest identifies the curated bench evidence record associated with the result.

The corresponding published-copy digests identify the repository artifacts covered by the publication manifest.

## Claim Boundary

The externally generated value used in ESP-LOCAL-002 is a bearer capability.

The test does not establish cryptographic identity of the request sender.

The endpoint-local `device_id`, `context`, and `action` predicates are not cryptographically bound into the capability commitment.

The spent state is RAM-only and is cleared by endpoint reset.

Accordingly, the published artifacts do not establish:

- cryptographic provider attribution;
- cryptographic binding of the complete authority object;
- persistent replay resistance across endpoint restart or power loss;
- secure boot;
- endpoint-compromise resistance;
- protected trust-anchor or key storage;
- hardware tamper resistance;
- production key custody; or
- exactly-once mechanical execution.

The witness establishes electrical PWM command issuance, not mechanical servo movement.

## Integrity

The published ESP-LOCAL-002 artifacts are covered by the accompanying:

```text
SHA256SUMS.txt
```

`SHA256SUMS.txt` records the published-copy digests and paths used for repository integrity verification.

The publication manifest verified all four covered artifacts successfully.
