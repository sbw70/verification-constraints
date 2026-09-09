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

SHA-256:

```text
175F571A938991B70A8C4ADF9D58864D179FA91CB70F4477F0717CB2C173C723
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

SHA-256:

```text
15938CBB3842BD6BFFF21F54CFD6FEEBE8BFC0E98BE1A24A236ECBBAE87D4874
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

The independent witness firmware was:

```text
esp_local_002_witness.py
```

SHA-256:

```text
AF380567C2FA6E961C1A029073BDD15FB7C39CE0034A80C554DC6709DD0F8AC4
```

This source is identical to the witness implementation used for ESP-LOCAL-001.

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

The curated evidence record is:

```text
ESP_LOCAL_002_EVIDENCE.log
```

SHA-256:

```text
8B66231145627977D47127992B9380287A31CFF8DC5378CB7DEB33474842187A
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

The published artifacts represent the final tested ESP-LOCAL-002 implementation and its corresponding external capability utility, independent witness, and curated evidence record.

The provider utility hash identifies the external capability-generation implementation used for the test.

The endpoint firmware hash identifies the implementation that performed endpoint-local recognition and RAM-based single-use consumption.

The witness firmware hash identifies the independent electrical observation implementation used to record PWM command issuance.

The evidence-record hash identifies the curated record of the observed test results.

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

The manifest verified all four covered artifacts successfully.
