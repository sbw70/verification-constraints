# ESP-LOCAL-006 — Hostile Relay / Compromised Forwarder

ESP-LOCAL-006 evaluates whether an intermediary positioned between provider-issued authority and an endpoint-local enforcement boundary can convert control of transport or request content into greater executable authority.

The test introduced a hostile application-layer relay capable of observing, modifying, substituting, forwarding, delaying, and replaying authority-bearing requests while retaining endpoint-local recognition and enforcement.

The requirement under test was:

> Intermediary control over the request path must not become the ability to originate, enlarge, substitute, regenerate, or reuse provider authority.

ESP-LOCAL-006 is a NUVL core test and does not introduce an architecture change.

## Tested Architecture

```text
requester / provider
        ↓
Raspberry Pi 3 hostile relay
        ↓
ESP32-S3 endpoint-local recognition
        ↓
persistent single-use authority enforcement
        ↓
servo PWM command path
        ↓
independent ESP32-S3 witness
```

The relay was hostile with respect to transport and request content.

It did not possess the trusted provider private key and did not have trusted-provider signing capability.

The endpoint retained the provider public trust anchor and remained responsible for deciding whether a presented request represented executable provider-established authority.

## Supported Result

Within the tested configuration, the hostile intermediary could transport, observe, mutate, substitute, and replay requests but could not turn those capabilities into greater executable provider authority.

The completed matrix demonstrated that:

- signed-field mutation was rejected,
- attempted enlargement of `max_uses` was rejected,
- a correctly structured request signed by an untrusted provider key was rejected,
- an untouched trusted request remained usable after preceding invalid submissions,
- valid authority was consumed once,
- replay after consumption was rejected,
- rejected hostile submissions did not consume or poison the legitimate unused authority,
- accepted authority was recorded as `SPENT` before PWM command issuance,
- independent GPIO observation recorded one servo-valid PWM burst for each accepted fresh authority and no second burst for the scored replay controls.

The strongest provider-key control used identical canonical Authority #2 bytes with different signatures:

```text
authority_bytes_equal: True
signatures_equal: False
```

The wrong-provider signature was rejected.

The trusted-provider signature over the same canonical authority bytes was accepted.

Detailed observed results are recorded in:

```text
RESULTS.md
```

## Scope

ESP-LOCAL-006 exercises:

- provider-issued Ed25519-signed bounded authority,
- endpoint-local signature verification,
- endpoint-local semantic admissibility,
- SHA-256 binding of received canonical authority to persistent authority state,
- persistent single-use authority consumption,
- hostile intermediary request-content control,
- `action` mutation,
- `context` mutation,
- `device_id` mutation,
- `max_uses` enlargement,
- byte-preserving pass-through controls,
- wrong-provider signature substitution,
- replay after legitimate consumption,
- direct persistent-state capture,
- independent electrical observation of the PWM command path.

ESP-LOCAL-006 tests compromised-forwarder behavior.

It does not test compromise of the trusted provider signing key.

## Test Endpoint

Primary actuator endpoint:

```text
Hardware:   Seeed XIAO ESP32-S3
Identity:   esp32-xiao-servo-02
Framework:  ESP-IDF v6.1
Actuator:   servo PWM
Port:       19061
```

The endpoint used endpoint-local Ed25519 recognition and persistent single-use authority state.

A separate ESP32-S3 DevKit independently monitored the electrical PWM command path:

```text
endpoint GPIO5
      ↓
witness GPIO4
```

The witness was observational only and did not participate in authorization.

## Hostile Relay

The hostile relay ran on a Raspberry Pi 3.

```text
requester
   ↓ TCP 19060
hostile relay
   ↓ TCP 19061
endpoint
```

The tested relay implementation supports:

- pass-through,
- `action` mutation,
- `context` mutation,
- `device_id` mutation,
- `max_uses` mutation,
- replay,
- per-transaction JSONL logging.

For mutation cases, the relay modifies authority-bearing content while retaining the original provider signature.

It does not create a replacement trusted-provider signature.

The tested relay reports:

```text
provider_private_key=ABSENT
signing_capability=ABSENT
```

## Provider Authority

The runtime recognizes authority in the canonical form:

```json
{
  "action": "move_servo",
  "context": "esp_local_006",
  "device_id": "esp32-xiao-servo-02",
  "max_uses": 1,
  "nonce": "<32 lowercase hexadecimal characters>"
}
```

The nonce may vary for a fresh provider-issued authority.

The remaining authority-bearing fields are constrained by the endpoint-local admissibility rule used in this test.

Trusted provider raw Ed25519 public key:

```text
48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1
```

Two fresh authority instances were used.

### Authority #1

Authority identifier:

```text
f72ade66cea3c93c2cb57944e03d69e185a061a59f83c3705a8e6977dfddc7d6
```

Authority #1 was used for:

- `action` mutation,
- `context` mutation,
- `device_id` mutation,
- `max_uses` enlargement,
- untouched trusted positive control,
- replay after legitimate consumption.

### Authority #2

Authority identifier:

```text
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc
```

Authority #2 was used to isolate provider-key trust.

The trusted-provider and wrong-provider requests preserve identical canonical authority bytes while carrying different Ed25519 signatures.

The endpoint had no trust relationship with the wrong-provider key.

## Endpoint Evaluation Order

The published endpoint runtime implements the following decision path:

```text
receive relay envelope
        ↓
strict envelope decoding
        ↓
provider Ed25519 verification
        ↓
semantic admissibility
        ↓
SHA-256 received authority
        ↓
persistent-state validation
        ↓
exact authority-id match
        ↓
require UNSPENT
        ↓
record SPENT
        ↓
commit
        ↓
close NVS handle
        ↓
deinitialize authority partition
        ↓
reinitialize authority partition
        ↓
fresh state reread
        ↓
require same authority-id + SPENT
        ↓
PWM command
```

No later failure path restores consumed authority.

Missing, malformed, corrupt, mismatched, or already-spent authority state is not treated as fresh authority.

## Persistent Authority State

ESP-LOCAL-006 uses a dedicated ESP-IDF NVS partition:

```text
label:   nuvl_state
offset:  0x110000
size:    0x6000
length:  24576 bytes
```

The persisted authority record contains:

```text
magic
version
state
reserved
authority_id[32]
crc32
```

Total record size:

```text
44 bytes
```

Recognized state values:

```text
UNSPENT = 1
SPENT   = 2
```

The endpoint requires a structurally valid persistent record whose stored authority identifier exactly matches the SHA-256 identifier of the received canonical authority.

Accepted authority is transitioned to `SPENT` before physical command issuance.

The runtime then closes the NVS handle, deinitializes and reinitializes the authority partition, and performs a fresh reread requiring the same authority identifier and `SPENT` state before PWM.

This post-commit reread is stronger than a same-handle cached read.

It does not independently establish persistence across an immediate power-loss boundary or resolve the exact physical ESP-IDF/NVS persistence point characterized separately in ESP-LOCAL-005.

## Test Matrix

The scored matrix was:

```text
1. Auth1 action mutation
2. Auth1 context mutation
3. Auth1 device_id mutation
4. Auth1 max_uses enlargement
5. Auth1 untouched trusted positive control
6. Auth1 replay
7. Auth2 wrong-provider signature control
8. Auth2 trusted-provider positive control
9. Auth2 trusted replay
```

A transport failure was not counted as an authorization denial.

The initial `max_uses` mutation attempts that failed to reach the endpoint because of relay-to-endpoint transport delay were not scored.

The case was rerun with a longer transport timeout and was scored only after the mutated request reached the endpoint and exercised the endpoint validation path.

## Independent Witness

The independent witness:

- does not hold provider signing material,
- does not verify provider authority,
- does not consume authority,
- does not modify persistent state,
- does not participate in the endpoint decision.

It records positive pulse widths observed on the endpoint PWM line as:

```text
PWM_HIGH_US <width>
```

The witness supports a claim of observed electrical PWM command issuance.

It does not independently establish guaranteed mechanical servo motion or exactly-once mechanical actuation.

## Evidence Model

The publication preserves separate evidence layers:

```text
provider authority artifact
        ↓
relay transaction record
        ↓
endpoint decision observation
        ↓
persistent-state capture
        ↓
independent PWM observation
```

No single artifact is treated as sufficient by itself to establish the complete result.

Persistent-state partition hashes establish binary-image identity and change.

The specific `UNSPENT` or `SPENT` interpretation depends on parsing the authority record, preserving the authority identifier, validating the NVS record structure and CRC, and correlating the result with endpoint and replay observations.

The COM15 endpoint and COM8 witness transcripts are curated derivatives reconstructed from preserved interactive terminal output.

They are explicitly not represented as original redirected raw serial logs.

## Published Firmware

Unlike the initial publication boundary used during test development, the completed ESP-LOCAL-006 package includes the endpoint implementation and preserved tested application binaries.

Published firmware material includes:

```text
firmware/
├── README.md
├── CMakeLists.txt
├── partitions.csv
├── sdkconfig
├── main/
│   ├── CMakeLists.AUTH2_TESTED.txt
│   ├── ESP_LOCAL_006.c
│   ├── ESP_LOCAL_006_PROVISIONER.c
│   ├── ESP_LOCAL_006_AUTH2_PROVISIONER.c
│   └── local_wifi_config.example.h
└── components/
    └── monocypher/
        ├── CMakeLists.txt
        ├── monocypher.c
        ├── monocypher.h
        ├── monocypher-ed25519.c
        └── monocypher-ed25519.h
```

The original credential-bearing `local_wifi_config.h` is not published.

A sanitized publication derivative is provided as:

```text
firmware/main/local_wifi_config.example.h
```

The final retained `main/CMakeLists.txt` corresponded to the Authority #2 provisioner build and is preserved as:

```text
firmware/main/CMakeLists.AUTH2_TESTED.txt
```

It is not represented as a universal build selector for all three applications.

The exact preserved tested application binaries are published under `evidence/`.

## Directory Contents

```text
ESP_LOCAL_006/
├── README.md
├── RESULTS.md
├── PROVENANCE.md
├── SHA256SUMS.txt
├── evidence/
├── firmware/
├── provider/
├── relay/
└── witness/
```

### `evidence/`

Contains test evidence including:

- Raspberry Pi 3 relay-host baseline,
- Auth1 relay JSONL records,
- Auth2 relay JSONL records,
- curated COM15 endpoint transcript,
- curated COM8 witness transcript,
- raw authority-state partition captures,
- preserved tested runtime binary,
- preserved Authority #1 provisioner binary,
- preserved Authority #2 provisioner binary.

### `firmware/`

Contains the published endpoint runtime, provisioner sources, build configuration, partition definition, cryptographic component source, sanitized Wi-Fi configuration template, and firmware-specific documentation.

### `provider/`

Contains:

- Authority #1 metadata,
- Authority #1 trusted request,
- Authority #2 metadata,
- Authority #2 trusted-provider request,
- Authority #2 wrong-provider request,
- wrong-provider public key.

The trusted provider private key and wrong-provider private key are not published.

### `relay/`

Contains the tested hostile relay implementation and relay-specific documentation.

### `witness/`

Contains the independent GPIO witness implementation and witness-specific documentation.

### `RESULTS.md`

Records the observed behavior of the completed scored matrix and test limitations.

### `PROVENANCE.md`

Records tested artifact identities, authority relationships, build lineage, relay lineage, persistent-state capture lineage, curated-evidence lineage, and publication relationships.

### `SHA256SUMS.txt`

Records SHA-256 values for the files actually published in the completed ESP-LOCAL-006 tree.

The manifest is regenerated after publication contents are finalized.

## Reproduction Requirements

A meaningful reproduction must preserve separation between:

1. trusted provider authority generation,
2. hostile relay operation,
3. endpoint-local signature verification,
4. endpoint-local semantic admissibility,
5. exact authority-to-state binding,
6. persistent single-use consumption,
7. physical command issuance,
8. independent witness observation.

A mutation case is not an authorization result unless the modified request reaches the endpoint and exercises the endpoint validation path.

A timeout, dropped request, or transport failure is not equivalent to endpoint denial.

For a different-provider-key control, trusted and untrusted requests should preserve identical canonical authority bytes so that provider trust is isolated from authority-content differences.

A test requiring unused authority should begin with a fresh `UNSPENT` authority instance.

Previously consumed authority should remain consumed rather than being reset and reused as though it were fresh.

A rebuilt binary is a reproduction build unless its SHA-256 exactly matches the corresponding preserved tested binary.

## Boundaries

ESP-LOCAL-006 does not establish:

- resistance to trusted provider private-key theft,
- resistance to complete endpoint compromise,
- secure routing,
- denial-of-service resistance,
- guaranteed availability under hostile intermediary behavior,
- trusted time or expiration enforcement,
- tamper-resistant persistent storage,
- anti-rollback protection,
- persistence across every possible immediate power-loss point,
- the exact physical ESP-IDF/NVS persistence boundary,
- exactly-once mechanical actuation,
- guaranteed mechanical servo movement.

The hostile relay can still interfere with availability by delaying, dropping, or preventing delivery.

The demonstrated property is narrower:

> Control of the intermediary request path did not become greater executable provider authority in the tested architecture.

The additional negative-path result is also material:

> Rejected invalid submissions did not consume the legitimate unused authority later accepted under the original provider-established bounds.

Observed outcomes are documented in:

```text
RESULTS.md
```

Artifact lineage is documented in:

```text
PROVENANCE.md
```

Firmware and build material are documented in:

```text
firmware/README.md
```

Published file integrity is documented in:

```text
SHA256SUMS.txt
```
