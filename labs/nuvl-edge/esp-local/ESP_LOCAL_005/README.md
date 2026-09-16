# ESP-LOCAL-005 — Persistent Endpoint-Local Authority Consumption

ESP-LOCAL-005 evaluates persistent endpoint-local enforcement of provider-issued, single-use bounded authority on an ESP32-S3 actuator endpoint.

The test extends endpoint-local provider-signature verification with durable local consumption of authority before physical command issuance.

The central requirement is that a bounded authority must not become executable more than permitted simply because the endpoint reboots, loses power, encounters invalid persistent state, or crashes during the consumption sequence.

## Scope

ESP-LOCAL-005 exercises:

- provider-signed authority,
- endpoint-local Ed25519 verification,
- semantic authority checks,
- explicit provisioning of persistent authority state,
- durable transition from `UNSPENT` to `SPENT`,
- replay denial,
- reboot persistence,
- full power-loss persistence,
- missing-state handling,
- corrupt-state handling,
- truncated-state handling,
- independent observation of the actuator command path,
- injected crashes around the persistence/execution boundary.

The test is concerned with bounded authority consumption at the endpoint.

It does not transfer authority-generation capability to the endpoint.

## Architectural Model

The tested authority path is:

```text
provider-issued authority
        ↓
endpoint signature verification
        ↓
semantic admissibility
        ↓
persistent-state validation
        ↓
authority consumption
        ↓
persistent-state verification
        ↓
physical command path
```

The endpoint may recognize and consume authority established by the provider.

It may not independently originate, enlarge, substitute, or regenerate that authority.

## Test Endpoint

Primary actuator endpoint:

```text
Hardware:   Seeed XIAO ESP32-S3
Identity:   esp32-xiao-servo-02
Framework:  ESP-IDF v6.1
Language:   C
Actuator:   servo PWM
```

A separate ESP32-S3 DevKit was used as an independent witness of the PWM execution path.

The witness observed Servo #2 through GPIO4.

## Provider Authority

Authority objects are provider-signed with Ed25519.

The canonical authority representation contains:

```json
{
  "action": "move_servo",
  "context": "esp_local_005",
  "device_id": "esp32-xiao-servo-02",
  "max_uses": 1,
  "nonce": "<provider-generated nonce>"
}
```

The endpoint holds provider verification material.

Provider signing material is included in the reproduction package so that equivalent test authorities can be generated and inspected.

Multiple fresh authorities were used during the test series so that previously consumed authority was not reset and reused as though it were new.

## Persistent Authority State

ESP-LOCAL-005 uses a dedicated ESP-IDF NVS partition:

```text
label:   nuvl_state
offset:  0x110000
size:    0x6000
length:  24576 bytes
```

The tested authority-state record contains:

- record magic,
- record version,
- authority state,
- authority identifier,
- CRC32.

Recognized authority states are:

```text
UNSPENT
SPENT
```

Persistent-state absence is not interpreted as fresh authority.

A usable `UNSPENT` state is created through explicit provisioning.

Invalid persistent state is handled as non-executable state rather than as an implicit reset.

## Normal Execution Ordering

The normal runtime evaluates authority in the following order:

```text
verify provider signature
        ↓
validate authority semantics
        ↓
validate persistent record
        ↓
require matching UNSPENT authority
        ↓
write SPENT state
        ↓
verify persistent SPENT state
        ↓
issue PWM command
```

Physical command issuance is downstream of authority consumption.

## Fault-Injection Coverage

ESP-LOCAL-005 includes dedicated artifacts for exercising persistent-state and crash behavior.

The published material includes:

- corrupt-state injection,
- truncated-state injection,
- post-consumption / pre-PWM crash injection,
- crash after the persistent-state write but before the explicit `nvs_commit()` call.

These variants exist to exercise the authority boundary under failure rather than only under nominal execution.

Observed outcomes are documented in `RESULTS.md`.

## Independent Witness

The witness implementation is separate from the enforcing endpoint.

Its purpose is to observe whether PWM is actually emitted on the tested actuator signal path.

This allows endpoint decision logs to be compared against an independent electrical observation.

The witness is not used to make the authorization decision.

It does not provide authority to the endpoint.

It also does not independently establish mechanical servo movement; it observes the electrical PWM command path.

## Directory Contents

```text
ESP_LOCAL_005/
├── README.md
├── RESULTS.md
├── PROVENANCE.md
├── SHA256SUMS.txt
├── firmware/
├── provider/
├── witness/
└── evidence/
```

### `firmware/`

Contains the endpoint implementations used for the test series, including:

- normal runtime,
- explicit provisioner,
- corrupt-state injector,
- truncated-state injector,
- post-consumption crash runtime,
- pre-explicit-commit crash runtime,
- authority-specific provisioning variants required by those cases.

### `provider/`

Contains the Ed25519 test key material used to generate and reproduce provider-signed authority objects.

### `witness/`

Contains the independent GPIO witness implementation used to observe the Servo #2 PWM path.

### `evidence/`

Contains preserved test artifacts, including:

- compiled ESP32 application binaries,
- authority metadata,
- authority-specific runtime variants,
- raw persistent-state partition captures,
- native Ed25519 gate artifacts,
- fault-injection binaries.

### `RESULTS.md`

Records the observed behavior of the completed test matrix.

### `PROVENANCE.md`

Records artifact origin, lineage, authority-specific relationships, and source/binary/state relationships.

### `SHA256SUMS.txt`

Provides SHA-256 verification for the published artifact set.

## Reproduction Model

Reproduction should preserve the separation between:

1. provider authority generation,
2. explicit endpoint provisioning,
3. endpoint runtime evaluation,
4. independent witness observation,
5. fault injection,
6. persistent-state capture.

A fresh authority should be used when a test requires fresh `UNSPENT` state.

Previously consumed authority should remain consumed rather than being erased and reused as a new authority.

The independent witness should be active before execution-path tests begin.

Persistent-state fault cases should alter the state under test without silently changing the normal runtime's validation behavior.

## Artifact Verification

Published files can be verified against:

```text
SHA256SUMS.txt
```

The manifest covers the artifacts included in this reproduction package.

Raw persistent-state `.bin` files are binary partition captures and should be handled as binary files rather than opened or copied as text.

## Results and Evidence

Detailed observed outcomes are intentionally separated from this README.

See:

```text
RESULTS.md
```

for test outcomes and:

```text
PROVENANCE.md
```

for artifact lineage.

The `evidence/` directory contains the preserved artifacts supporting those records.

## Boundaries

ESP-LOCAL-005 evaluates endpoint-local bounded-authority consumption and persistence.

It is not intended to establish:

- secure boot,
- tamper-resistant storage,
- resistance to complete endpoint compromise,
- resistance to provider-key compromise,
- confidentiality,
- trusted time,
- exactly-once mechanical execution,
- universal ESP-IDF NVS persistence semantics,
- equivalent behavior across unrelated MCU or storage platforms.

Those properties require separate tests and evidence.
