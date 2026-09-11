# ESP-LOCAL-003 Provenance

## Purpose

This document records the provenance of the implementation and evidence artifacts associated with ESP-LOCAL-003.

ESP-LOCAL-003 evaluated endpoint-local recognition of an externally established bounded authority object whose device, context, action, nonce, and use constraint were jointly represented in verification material.

The test was performed on September 9, 2026.

---

## Test Environment

### Recognition and Actuation Endpoint

- Platform: Seeed XIAO ESP32-S3
- Runtime: MicroPython
- Device ID: `esp32-xiao-servo-01`
- Context: `esp_local_003`
- Authorized action: `move_servo`
- Servo output: GPIO 5
- Configured maximum uses: `1`

The XIAO performed authority recognition immediately before physical command issuance.

### Independent Witness

An ESP32-S3 DevKit was used as an independent electrical witness.

The witness monitored the servo PWM signal and reported:

- `IDLE` while no qualifying PWM burst was present;
- `BURST_START` when an actuation burst began;
- pulse count and duration at `BURST_END`.

The witness implementation reused the previously tested ESP-LOCAL-001 witness source. The retained tested-source SHA-256 digest is:

```text
AF380567C2FA6E961C1A029073BDD15FB7C39CE0034A80C554DC6709DD0F8AC4
```

The witness source was not developed specifically for ESP-LOCAL-003. Its reuse is intentional because ESP-LOCAL-003 required the same independent observation of servo PWM command issuance.

---

## Frozen Authority Material

The authority values were frozen before execution of the ESP-LOCAL-003 matrix.

Nonce:

```text
eee8483225c14eb493654571128d57e2
```

Authority commitment:

```text
2452e70c9003739fd571a5e38752e54d526c1f7ee876ad3bed3041e09ca9c0cc
```

Authority object:

```json
{
  "device_id": "esp32-xiao-servo-01",
  "context": "esp_local_003",
  "action": "move_servo",
  "nonce": "eee8483225c14eb493654571128d57e2",
  "max_uses": 1
}
```

Canonical authority representation:

```json
{"action":"move_servo","context":"esp_local_003","device_id":"esp32-xiao-servo-01","max_uses":1,"nonce":"eee8483225c14eb493654571128d57e2"}
```

The SHA-256 commitment above corresponds to the frozen canonical authority representation used by the tested endpoint implementation.

---

## Endpoint Firmware

The ESP-LOCAL-003 endpoint implementation was retained locally as:

```text
esp_local_003_main.py
```

The implementation enforced:

1. exact authority-object schema;
2. device binding;
3. context binding;
4. action binding;
5. `max_uses` constraint;
6. authority-object commitment recognition;
7. current-runtime spent-state recognition; and
8. consumption before physical command issuance.

No permissive fallback or unsigned alternative authority path was part of the tested ESP-LOCAL-003 recognition path.

The tested-source SHA-256 digest for `esp_local_003_main.py` should be recorded from the retained local tested source.

If the GitHub publication copy has a different byte-level digest because of publication processing, line-ending conversion, sanitization, or other non-functional transformation, the tested-source and published-copy digests must be recorded separately.

A differing digest must not be described as byte-identical provenance.

---

## Witness Evidence Provenance

The ESP-LOCAL-003 witness observations were preserved contemporaneously in the September 9, 2026 test record.

The retained record contains raw COM8 witness output from the ESP32-S3 DevKit, including the initial accepted execution:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=244932
ESP_LOCAL_001_WITNESS_HEARTBEAT ticks_ms=245092 state=ACTIVE
ESP_LOCAL_001_WITNESS_BURST_END pulses=50 duration_ms=978 pulse_min_us=426 pulse_max_us=2003
```

It also contains extended `IDLE` witness output following that event during the replay and mutation-denial sequence.

The final valid-control execution was independently observed as:

```text
ESP_LOCAL_001_WITNESS_BURST_START ticks_ms=1047996
ESP_LOCAL_001_WITNESS_BURST_END pulses=51 duration_ms=999 pulse_min_us=426 pulse_max_us=2123
```

For repository publication, the relevant raw witness excerpts were extracted into:

```text
ESP_LOCAL_003_WITNESS_LOG.txt
```

This file is an extraction of contemporaneously preserved terminal output. It is not a rerun of ESP-LOCAL-003 and is not a reconstruction of missing witness events.

The original test record contains separate witness excerpts rather than one uninterrupted terminal capture. Gaps between retained excerpts must not be represented as observed data.

---

## Evidence Interpretation

The witness evidence establishes electrical PWM command issuance associated with accepted authority.

The first valid authority produced one observed PWM burst:

```text
50 pulses
978 ms duration
```

The exact replay was subsequently denied as:

```text
authority_spent
```

No second PWM burst was observed during the retained replay interval.

The mutation-denial sequence produced no additional observed actuation burst in the retained witness evidence.

After the non-consuming mutation sequence, the original authority object remained admissible and produced a second independently observed PWM burst:

```text
51 pulses
999 ms duration
```

This final control demonstrated that the rejected mutation attempts had not consumed or corrupted the legitimate authority state.

The witness establishes electrical command issuance. It does not independently establish guaranteed mechanical movement or exactly-once mechanical execution.

---

## Fail-Closed Implementation History

During ESP-LOCAL-003 development, MicroPython compatibility differences were encountered in the authority canonicalization and hashing path.

An initial implementation using an unsupported `json.dumps(..., separators=...)` form failed during authority processing.

The observed endpoint result was:

```text
{"reason": "authority_invalid", "decision": "denied"}
```

The independent witness remained `IDLE`.

A subsequent implementation adjustment was required because the MicroPython hashing API did not expose the expected `hexdigest()` behavior used by the initial implementation.

These implementation defects did not produce an accepted authority decision or unintended physical command issuance.

The final tested implementation used MicroPython-compatible canonicalization and SHA-256 processing.

These failed-closed development observations are retained as part of the test provenance and are not represented as successful ESP-LOCAL-003 matrix cases.

---

## Publication Provenance Rules

Repository publication distinguishes between:

- tested-source artifacts;
- evidence captured or preserved during testing;
- evidence excerpts derived from contemporaneous test records; and
- published repository copies.

`SHA256SUMS.txt` records the byte identity of the files actually published in the repository.

Tested-source digests belong in this provenance record when available.

If a published artifact differs at the byte level from its tested source, both digests should be retained and explicitly distinguished.

A published-copy digest must not be substituted for a tested-source digest.

An extracted evidence file such as `ESP_LOCAL_003_WITNESS_LOG.txt` must be identified as an extraction when it was created from a larger contemporaneous record after execution of the test.

---

## Publication Boundary

ESP-LOCAL-003 demonstrates commitment-based integrity and endpoint-local bounded-authority recognition.

It does not establish provider identity or asymmetric provider attribution.

The test also does not establish:

- persistent spent-state across endpoint reboot;
- trusted time or expiration;
- secure boot;
- protected trust material;
- endpoint-compromise resistance;
- production cryptographic implementation hardening;
- guaranteed mechanical movement; or
- exactly-once physical execution.

Provider-attributable asymmetric authority is evaluated separately in ESP-LOCAL-004.
