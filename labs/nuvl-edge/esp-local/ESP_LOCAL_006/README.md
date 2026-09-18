# ESP-LOCAL-006 — Hostile Relay / Compromised Forwarder

ESP-LOCAL-006 evaluates whether an intermediary positioned between the requester/provider side and an endpoint-local enforcement boundary can convert transport or content-control capability into greater executable authority.

The test retains provider-controlled authority while introducing a hostile application-layer relay capable of observing, modifying, substituting, forwarding, and replaying authority-bearing requests.

The central requirement is that compromise of the path must not become compromise of provider authority.

## Scope

ESP-LOCAL-006 exercises:

- provider-issued Ed25519-signed bounded authority,
- endpoint-local signature verification,
- endpoint-local semantic admissibility,
- persistent single-use authority state,
- a hostile intermediary with request-content control,
- signed-field mutation,
- attempted enlargement of `max_uses`,
- byte-preserving pass-through controls,
- wrong-provider signature substitution,
- replay after legitimate execution,
- independent electrical observation of the PWM command path,
- direct pre-test and post-test persistent-state capture.

The relay was hostile with respect to transport and request content.

It did not possess the trusted provider private key and did not have trusted-provider signing capability.

ESP-LOCAL-006 therefore tests compromised-forwarder behavior, not trusted-provider key compromise.

## Architectural Model

The tested path was:

```text
requester / provider
        ↓
Raspberry Pi 3 hostile relay
        ↓
ESP32-S3 endpoint-local enforcement
        ↓
persistent single-use authority state
        ↓
servo PWM command path
        ↓
independent ESP32-S3 witness
```

The relay could observe and manipulate requests.

The endpoint remained responsible for determining whether a presented request represented executable provider authority.

The endpoint could recognize and consume provider-established authority.

The relay could not independently originate trusted provider authority.

## Test Endpoint

Primary actuator endpoint:

```text
Hardware:   Seeed XIAO ESP32-S3
Identity:   esp32-xiao-servo-02
Framework:  ESP-IDF v6.1
Actuator:   servo PWM
Port:       19061
```

The endpoint used endpoint-local Ed25519 verification and persistent single-use authority state.

A separate ESP32-S3 DevKit was used as an independent witness of the electrical PWM command path.

The witness monitored endpoint GPIO5 through witness GPIO4.

## Hostile Relay

The hostile relay ran on a Raspberry Pi 3.

Default relay path:

```text
requester
   ↓ TCP 19060
hostile relay
   ↓ TCP 19061
endpoint
```

The relay implementation supports:

- pass-through,
- `action` mutation,
- `context` mutation,
- `device_id` mutation,
- `max_uses` mutation,
- replay,
- per-transaction JSONL logging.

For mutation cases, the relay modifies the canonical authority content while retaining the original provider signature.

It does not generate a replacement trusted-provider signature.

At startup the relay reports:

```text
provider_private_key=ABSENT
signing_capability=ABSENT
```

## Provider Authority

The tested authority representation was:

```json
{
  "action": "move_servo",
  "context": "esp_local_006",
  "device_id": "esp32-xiao-servo-02",
  "max_uses": 1,
  "nonce": "<authority-specific nonce>"
}
```

The trusted provider raw Ed25519 public key was:

```text
48852270ce16654edeef2a1c3d0930af4b990e1bf5060fb3221996434f63e5b1
```

Two fresh authority instances were used.

### Authority #1

Authority #1 was used for:

- `action` mutation,
- `context` mutation,
- `device_id` mutation,
- `max_uses` enlargement,
- untouched positive control,
- replay after legitimate consumption.

Authority #1 identifier:

```text
f72ade66cea3c93c2cb57944e03d69e185a061a59f83c3705a8e6977dfddc7d6
```

### Authority #2

Authority #2 was used for the different-provider-key control.

Authority #2 identifier:

```text
196a973cfe65d81c415618f2874874e65d88e006223783bc0726a4c84acf87fc
```

The trusted-provider and wrong-provider Auth2 request envelopes contain identical canonical authority bytes and different Ed25519 signatures.

The wrong-provider public key is published for inspection.

The corresponding wrong-provider private key is not included in the publication package.

## Persistent Authority State

ESP-LOCAL-006 uses a dedicated ESP-IDF NVS partition:

```text
label:   nuvl_state
offset:  0x110000
size:    0x6000
length:  24576 bytes
```

Recognized authority states include:

```text
UNSPENT
SPENT
```

The endpoint requires a valid matching persistent authority record before execution.

Accepted authority is recorded as spent before PWM command issuance.

Persistence characteristics underlying that state transition were characterized separately in ESP-LOCAL-005.

ESP-LOCAL-006 does not extend those persistence claims beyond the limitations already documented there.

## Test Matrix

The completed ESP-LOCAL-006 matrix includes:

```text
Auth1 action mutation
Auth1 context mutation
Auth1 device_id mutation
Auth1 max_uses enlargement
Auth1 untouched positive control
Auth1 replay
Auth2 wrong-provider signature control
Auth2 trusted-provider positive control
Auth2 trusted replay
```

Detailed observed outcomes are intentionally separated from this README.

See:

```text
RESULTS.md
```

## Independent Witness

The independent witness runs separately from the enforcing endpoint.

Its role is observation only.

The witness:

- does not hold provider signing material,
- does not verify authority,
- does not consume authority,
- does not alter endpoint state,
- does not make authorization decisions.

It measures positive pulse widths observed on the endpoint PWM line.

Observed output is emitted as:

```text
PWM_HIGH_US <width>
```

The witness establishes observed electrical PWM command issuance.

It does not independently establish guaranteed mechanical servo motion or exactly-once mechanical actuation.

## Directory Contents

```text
ESP_LOCAL_006/
├── README.md
├── RESULTS.md
├── PROVENANCE.md
├── SHA256SUMS.txt
├── evidence/
├── provider/
├── relay/
└── witness/
```

### `evidence/`

Contains preserved test evidence, including:

- Raspberry Pi relay-host baseline,
- Auth1 relay JSONL records,
- Auth2 relay JSONL records,
- curated COM15 endpoint transcript,
- curated COM8 witness transcript,
- raw persistent-state partition captures.

The terminal transcripts are explicitly marked as curated derivatives and are not represented as raw redirected serial logs.

### `provider/`

Contains:

- Authority #1 metadata,
- Authority #1 trusted request,
- Authority #2 metadata,
- Authority #2 trusted-provider request,
- Authority #2 wrong-provider request,
- wrong-provider public key.

The trusted provider private key and wrong-provider private key are not published in this directory.

### `relay/`

Contains the hostile relay implementation and relay-specific documentation.

### `witness/`

Contains the independent GPIO witness implementation and witness-specific documentation.

### `RESULTS.md`

Records the observed behavior of the completed test matrix.

### `PROVENANCE.md`

Records artifact origin, authority relationships, relay lineage, persistent-state capture lineage, curated-evidence lineage, and the tested-but-unpublished implementation boundary.

### `SHA256SUMS.txt`

Provides SHA-256 verification for the files actually published in the ESP-LOCAL-006 package.

## Reproduction Model

Reproduction should preserve separation between:

1. trusted provider authority generation,
2. hostile relay operation,
3. endpoint-local signature verification,
4. endpoint-local semantic admissibility,
5. persistent single-use state,
6. physical command issuance,
7. independent witness observation.

A mutation case should not be scored as an authorization result unless the modified request reaches the endpoint and exercises the endpoint validation path.

A timeout, dropped request, or transport failure is not equivalent to endpoint denial.

For wrong-provider controls, trusted and untrusted requests should preserve identical canonical authority bytes so that provider-key trust is isolated from authority-content differences.

A fresh `UNSPENT` authority should be used when a test requires an unused authority instance.

Previously consumed authority should remain consumed rather than being reset and reused as though it were fresh authority.

## Evidence Interpretation

The evidence package preserves several independent observation layers:

```text
provider authority artifact
        ↓
relay transaction record
        ↓
endpoint decision observation
        ↓
persistent-state capture
        ↓
independent PWM witness
```

No single artifact is treated as sufficient by itself to establish the full execution result.

A difference between pre-test and post-test persistent-state partition hashes establishes that the binary images differ.

The specific state transition must be established from the parsed authority record, preserved authority identifier, valid NVS CRC, endpoint observations, and replay behavior.

Curated terminal transcripts identify the published derivative artifacts themselves and do not claim to be original raw serial captures.

## Publication Boundary

The ESP-LOCAL-006 public package does not include implementation material that exposes the persistent-authority enforcement boundary.

Excluded implementation classes include:

- endpoint runtime source exposing persistence mechanics,
- authority provisioner source,
- authority provisioner binaries,
- implementation-specific state-write logic.

The publication instead preserves:

- provider authority artifacts,
- relay source,
- witness source,
- relay evidence,
- endpoint observations,
- witness observations,
- persistent-state captures,
- artifact lineage,
- published hashes.

## Boundaries

ESP-LOCAL-006 is not intended to establish:

- resistance to trusted provider private-key theft,
- resistance to complete endpoint compromise,
- secure routing,
- denial-of-service resistance,
- guaranteed availability under hostile intermediary behavior,
- trusted time or expiration enforcement,
- tamper-resistant persistent storage,
- anti-rollback protection,
- exactly-once mechanical actuation,
- guaranteed mechanical servo movement.

The relay's network position could still be used to interfere with communication by delaying or preventing delivery.

The property under test is narrower:

intermediary control over the request path must not become greater provider authority.

Observed outcomes are documented in:

```text
RESULTS.md
```

Artifact lineage is documented in:

```text
PROVENANCE.md
```

Published file integrity is documented in:

```text
SHA256SUMS.txt
```
