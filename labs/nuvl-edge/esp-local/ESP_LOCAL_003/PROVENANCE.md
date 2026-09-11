# ESP-LOCAL-003 Provenance

## Test Identity

**Test:** ESP-LOCAL-003  
**Status:** PASS  
**Function:** Endpoint-local recognition of an externally established, integrity-bound authority object

ESP-LOCAL-003 extended endpoint-local authority recognition by binding the complete authority representation into SHA-256 verification material before physical command issuance.

The tested authority representation included:

- device identity;
- context;
- action;
- nonce; and
- maximum-use constraint.

---

## Tested Architecture

```text
External authority source
        |
        v
Seeed XIAO ESP32-S3
  local recognition
  bound verification
  spent-state check
        |
        v
Servo PWM command
        |
        +----> Independent ESP32-S3 PWM witness
```

Authority recognition and consumption occurred on the XIAO endpoint. No Raspberry Pi recognition boundary participated in the decision path.

---

## Endpoint Identity

| Property | Value |
|---|---|
| Platform | Seeed XIAO ESP32-S3 |
| Device ID | `esp32-xiao-servo-01` |
| Context | `esp_local_003` |
| Authorized action | `move_servo` |
| Maximum uses | `1` |
| Servo output | GPIO 5 |

---

## Frozen Authority Object

```json
{
  "device_id": "esp32-xiao-servo-01",
  "context": "esp_local_003",
  "action": "move_servo",
  "nonce": "eee8483225c14eb493654571128d57e2",
  "max_uses": 1
}
```

Canonical representation:

```text
{"action":"move_servo","context":"esp_local_003","device_id":"esp32-xiao-servo-01","max_uses":1,"nonce":"eee8483225c14eb493654571128d57e2"}
```

SHA-256 authority commitment:

```text
2452e70c9003739fd571a5e38752e54d526c1f7ee876ad3bed3041e09ca9c0cc
```

The device, context, action, nonce, and use constraint were therefore jointly represented in the verification material evaluated by the endpoint.

---

## Endpoint Implementation

Tested endpoint source:

```text
esp_local_003_main.py
```

The endpoint recognition path enforced:

```text
exact schema
    ->
device/context/action/use constraints
    ->
canonical authority representation
    ->
SHA-256 commitment recognition
    ->
spent-state recognition
    ->
consume authority
    ->
physical command issuance
```

Authority was consumed before PWM command issuance.

Spent state was maintained in volatile endpoint memory for this test.

---

## Independent Witness

ESP-LOCAL-003 reused the independent ESP32-S3 PWM witness implementation established for ESP-LOCAL-001.

Tested witness-source SHA-256:

```text
AF380567C2FA6E961C1A029073BDD15FB7C39CE0034A80C554DC6709DD0F8AC4
```

The witness independently monitored the servo PWM signal and reported command-burst activity without participating in the authority decision.

The `ESP_LOCAL_001` identifier present in witness output reflects the reused witness implementation and does not identify the authority-recognition test being executed.

---

## Witness Evidence

Contemporaneous COM8 witness output was retained in the test record.

The first valid authority execution produced:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=244932
ESP_LOCAL_001_WITNESS_HEARTBEAT ticks_ms=245092 state=ACTIVE
ESP_LOCAL_001_WITNESS_BURST_END pulses=50 duration_ms=978 pulse_min_us=426 pulse_max_us=2003
```

The witness subsequently remained `IDLE` through the retained replay and mutation-denial observations.

The final valid control produced:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=1047996
ESP_LOCAL_001_WITNESS_BURST_END pulses=51 duration_ms=999 pulse_min_us=426 pulse_max_us=2123
```

Repository artifact:

```text
ESP_LOCAL_003_WITNESS_LOG.txt
```

`ESP_LOCAL_003_WITNESS_LOG.txt` is a direct extraction of raw COM8 output preserved in the contemporaneous September 9 test record. It is not a test rerun or reconstructed witness record.

The source record contains discrete retained terminal excerpts; intervals absent from that record are not represented as observed data.

---

## Evidence Lineage

ESP-LOCAL-003 evidence consists of three distinct artifact classes:

| Artifact class | Provenance |
|---|---|
| Endpoint implementation | Source executed on the XIAO ESP32-S3 during ESP-LOCAL-003 |
| Witness implementation | Reused tested ESP-LOCAL-001 PWM witness |
| Witness log | Extracted from contemporaneously retained September 9 COM8 terminal output |

Repository SHA-256 manifests identify the exact bytes published in the repository.

Tested-source and published-copy digests are distinct provenance identities when their byte representations differ. No byte-identity claim is implied solely by functional equivalence.

---

## Evidence Boundary

The independent witness establishes electrical PWM command issuance.

ESP-LOCAL-003 does not use the witness evidence to establish:

- guaranteed mechanical movement;
- exactly-once mechanical execution; or
- actuator-state confirmation.

The authority commitment establishes integrity recognition against the frozen authority representation. It does not establish asymmetric provider identity.

Provider-attributable asymmetric authority is evaluated separately in ESP-LOCAL-004.
