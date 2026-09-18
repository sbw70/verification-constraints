# ESP-LOCAL-006 Hostile Relay

This directory contains the application-layer hostile relay used during ESP-LOCAL-006.

The relay was inserted between the requester/provider side of the test path and the ESP32-S3 endpoint in order to exercise intermediary manipulation without transferring trusted provider signing capability to the intermediary.

## Contents

`esp_local_006_hostile_relay.py`

Python TCP relay used to forward, mutate, substitute, and replay ESP-LOCAL-006 request envelopes.

## Tested Role

The relay occupied the following position:

```text
requester / provider
        ↓
ESP-LOCAL-006 hostile relay
        ↓
ESP32-S3 endpoint-local enforcement
        ↓
physical command path
```

The relay could inspect and modify request content before forwarding it to the endpoint.

It did not possess the trusted provider private key and did not have the ability to generate a valid trusted-provider signature for modified authority.

At startup the relay explicitly reports:

```text
provider_private_key=ABSENT
signing_capability=ABSENT
```

This distinction defines the ESP-LOCAL-006 threat model.

The relay represents a compromised or hostile intermediary with control over transport and request content, not an intermediary that has obtained trusted provider signing material.

## Request Format

The relay processes newline-delimited JSON request envelopes containing:

```json
{
  "authority_b64": "<base64 canonical authority bytes>",
  "signature_b64": "<base64 Ed25519 signature>"
}
```

For mutation modes, the relay:

1. decodes the request envelope,
2. decodes the authority object,
3. modifies the selected authority field,
4. serializes the modified authority,
5. replaces `authority_b64`,
6. retains the original provider signature,
7. forwards the resulting request to the endpoint.

Because the original signature is retained, a mutation changes the signed content without creating a new valid provider signature.

## Supported Modes

The relay implements the following modes:

### `pass`

Forwards the received request without modifying its bytes.

This mode is used for byte-preserving forwarding controls and for requests whose signatures or replay state are intended to be evaluated unchanged by the endpoint.

### `mutate-action`

Changes:

```text
action = move_servo_admin
```

while retaining the original provider signature.

### `mutate-context`

Changes:

```text
context = esp_local_006_relay_mutated
```

while retaining the original provider signature.

### `mutate-device`

Changes:

```text
device_id = esp32-xiao-servo-99
```

while retaining the original provider signature.

### `mutate-max-uses`

Changes:

```text
max_uses = 2
```

while retaining the original provider signature.

This mode exercises attempted enlargement of the provider-issued single-use bound.

### `replay`

Forwards the same request payload twice to the endpoint and records both endpoint responses.

The relay includes this mode as a reproduction capability. The preserved ESP-LOCAL-006 evidence also includes replay cases exercised through byte-preserving forwarding of the same previously accepted request.

## Default Ports

The relay defaults are:

```text
listen host:  0.0.0.0
listen port:  19060
target port:  19061
timeout:      5 seconds
```

The target endpoint IPv4 address is supplied with `--target`.

The timeout can be overridden with `--timeout`.

## Example Invocation

A pass-through relay can be started with:

```text
python3 esp_local_006_hostile_relay.py \
  --target <endpoint-ip> \
  --mode pass
```

A mutation case can be started with:

```text
python3 esp_local_006_hostile_relay.py \
  --target <endpoint-ip> \
  --mode mutate-max-uses
```

A specific evidence log can be selected with:

```text
--log <path>
```

## Logging

Each completed relay transaction is written as one JSON object per line.

For ordinary forwarding and mutation cases, records include:

- UTC timestamp,
- requester peer address,
- relay mode,
- target endpoint,
- ingress byte count,
- egress byte count,
- ingress SHA-256,
- egress SHA-256,
- endpoint response,
- endpoint-response SHA-256.

For replay mode, the relay records separate hashes and response contents for the first and second endpoint responses.

Errors are also logged as JSON records containing:

- timestamp,
- peer,
- mode,
- exception type,
- exception detail.

## Byte-Preserving Controls

In `pass` mode, the ingress and egress request bytes are unchanged.

The corresponding relay records therefore allow comparison of:

```text
ingress_sha256
egress_sha256
```

Matching values establish that the relay forwarded the request envelope without changing its bytes.

This was used during ESP-LOCAL-006 controls involving trusted-provider, wrong-provider, and replayed authority requests.

## Mutation Controls

Mutation modes intentionally produce different ingress and egress request hashes.

The relay does not attempt to repair or replace the original signature after changing authority content.

This allows the endpoint to determine whether altered authority remains executable without relying on the relay to make the authorization decision.

## Failure Handling

Relay exceptions are returned to the requester as structured relay errors and are recorded in the JSONL log.

A transport failure or timeout is not equivalent to an endpoint authorization denial.

ESP-LOCAL-006 scoring therefore requires the request to reach the endpoint and exercise the endpoint validation path before a mutation case is counted as an authorization result.

Observed transport anomalies and their treatment are documented in:

```text
../RESULTS.md
```

## Security Boundary

The relay is intentionally outside the trusted authority-generation boundary.

It can:

- observe request envelopes,
- forward requests,
- alter signed authority content,
- substitute request material,
- repeat requests,
- delay processing through its network position,
- prevent delivery by failing to forward.

It cannot, within the tested configuration:

- generate a valid trusted-provider signature,
- originate trusted provider authority,
- enlarge trusted authority while preserving signature validity,
- change endpoint persistent authority state directly,
- make the endpoint acceptance decision.

ESP-LOCAL-006 does not model compromise in which the relay also possesses the trusted provider private key.

## Related Evidence

Preserved Auth1 relay records:

```text
../evidence/ESP_LOCAL_006_RELAY_AUTH1.jsonl
```

Preserved Auth2 relay records:

```text
../evidence/ESP_LOCAL_006_RELAY_AUTH2.jsonl
```

The Raspberry Pi 3 relay-host baseline is stored at:

```text
../evidence/ESP_LOCAL_006_PI3_BASELINE.txt
```

Endpoint decision evidence is stored at:

```text
../evidence/ESP_LOCAL_006_ENDPOINT_COM15_CURATED.txt
```

Independent physical-command witness evidence is stored at:

```text
../evidence/ESP_LOCAL_006_WITNESS_COM8_CURATED.txt
```

Observed outcomes are documented in:

```text
../RESULTS.md
```

Artifact lineage is documented in:

```text
../PROVENANCE.md
```

Published artifact hashes are recorded in:

```text
../SHA256SUMS.txt
```
