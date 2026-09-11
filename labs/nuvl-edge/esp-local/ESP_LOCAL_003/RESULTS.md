# ESP-LOCAL-003 Results

## Status

**PASS**

ESP-LOCAL-003 demonstrated endpoint-local recognition of an externally established bounded authority object whose device, context, action, nonce, and use constraint were jointly represented in verification material.

The endpoint rejected modification or enlargement of those bounds before physical command issuance, consumed valid authority before execution, and denied subsequent reuse during the current runtime.

---

## Test Configuration

Endpoint:

- Seeed XIAO ESP32-S3
- Device ID: `esp32-xiao-servo-01`
- Context: `esp_local_003`
- Authorized action: `move_servo`
- `max_uses`: `1`

Frozen nonce:

```text
eee8483225c14eb493654571128d57e2
