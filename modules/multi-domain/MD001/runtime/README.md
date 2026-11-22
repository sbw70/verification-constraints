# MD001 — Runtime Components

## Multi-Domain Stateless Verification

**Organization:** Xer0trust LLC  
**Experiment:** MD001  
**Component:** Runtime implementation  
**Language:** Python 3  
**Status:** Physical-network experiments completed

---

## 1. Purpose

This directory contains the runtime components used by MD001 — Multi-Domain Stateless Verification.

The implementation separates cryptographic assertion verification from network transport.

The central architectural distinction is:

**Transporting a verification artifact does not grant authority to create, validate, authorize, or execute the operation represented by that artifact.**

The runtime consists of four Python modules:

```text
runtime/
|
|-- artifact.py
|-- hub.py
|-- routes.py
|-- wire.py
|
`-- README.md
```

The modules perform different functions.

| Module | Responsibility |
|---|---|
| `artifact.py` | Canonical assertion encoding, signing support, and cryptographic verification |
| `hub.py` | Mechanical HTTP request forwarding and transport observations |
| `routes.py` | Static topology and route validation |
| `wire.py` | Bounded HTTP/1 framing, parsing, and byte-preserving forwarding |

Only `artifact.py` evaluates the signed assertion.

The other three modules implement transport-related functions.

---

## 2. Architectural Separation

The MD001 request path is:

```text
DOMAIN A
Producer
    |
    | Signed assertion
    v
MECHANICAL RELAY
hub.py
    |
    | Static route selection
    | HTTP framing
    | Artifact forwarding
    v
DOMAIN B
Verifier
    |
    | artifact.py
    | Public-key resolution
    | Signature verification
    | Local criteria evaluation
    v
VERIFICATION RESULT
```

The mechanical relay does not require the producer's private signing key.

It does not evaluate the Ed25519 signature.

It does not determine whether the underlying operation was authorized.

The receiving verifier performs the cryptographic evaluation using locally provisioned trust.

The modules are deliberately separated so that transport functionality does not inherit the verifier's responsibilities.

---

# 3. artifact.py — Assertion Verification

## 3.1 Responsibility

`artifact.py` implements the MD001 assertion format and its cryptographic verification behavior.

The module declares its intended scope:

```python
"""MD-001 assertions only. No network, history, execution, or evidence dependencies."""
```

The module contains no network transport implementation.

It does not contact the producer.

It does not maintain a persistent artifact-consumption ledger.

It does not execute the underlying operation.

## 3.2 Assertion Structure

The signed assertion contains an event object and a signature.

The event has exactly six fields:

```text
version
producer_id
key_id
artifact_id
event_id
outcome
```

The outer envelope contains exactly:

```text
event
signature
```

Additional envelope or event fields are rejected.

### Expected Event

The producer function creates an event containing:

```text
version = 1
producer_id = DOMAIN_A
event_id = LOCAL_SORT_V1
outcome = SUCCESS
```

The key identifier is derived from the producer's public key.

The artifact identifier is a UUID.

## 3.3 Canonical Encoding

The module uses deterministic JSON encoding.

```python
json.dumps(
    obj,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
)
```

The resulting JSON is encoded as UTF-8.

This establishes a consistent byte representation for the signed event.

The verifier also requires the received envelope to match its canonical encoding.

Noncanonical envelopes are rejected.

## 3.4 Domain-Separated Signed Bytes

The module defines:

```python
TAG = b"NUVL-MD001-ARTIFACT-v1|"
```

The bytes presented for signing are:

```text
NUVL-MD001-ARTIFACT-v1| + canonical_event_json
```

The prefix distinguishes MD001 assertion signatures from signatures generated for unrelated message formats.

The prefix is part of the signed input.

It is not an authorization token or execution command.

## 3.5 Ed25519 Signatures

The module uses Ed25519.

The producer signs the domain-separated canonical event bytes.

The signature is encoded using unpadded URL-safe Base64.

The verifier:

1. Parses the received envelope.
2. Validates its structure.
3. Resolves the producer's public key.
4. Reconstructs the signed bytes.
5. Performs Ed25519 signature verification.
6. Evaluates the local event criteria.

The private signing key is not required for verification.

## 3.6 Public-Key Binding

The key identifier is constructed as:

```text
sha256:<public-key-digest>
```

The verifier resolves the key using:

```python
trust.get(producer_id, {}).get(key_id)
```

The resolved public key is reconstructed as an Ed25519 public key.

Its fingerprint is checked against the assertion's key identifier.

This prevents the assertion from selecting an arbitrary public key outside the locally provisioned mapping.

An unknown producer/key binding is rejected.

## 3.7 Input Validation

The verifier enforces several restrictions.

| Property | Restriction |
|---|---|
| Artifact size | Maximum 65,536 bytes |
| Envelope | Exactly `event` and `signature` |
| Event fields | Exactly six defined fields |
| Version | Integer `1` |
| Artifact identifier | Canonical UUID |
| Key identifier | `sha256:` followed by 64 lowercase hexadecimal characters |
| Signature | Canonical unpadded URL-safe Base64 |
| JSON | UTF-8, no duplicate keys or nonfinite constants |
| Envelope encoding | Canonical JSON |

Malformed inputs are rejected before signature verification where applicable.

The verifier records whether a signature check was performed.

## 3.8 Local Verification Criteria

A valid signature is necessary but not sufficient for acceptance.

After successful signature verification, the module checks:

```python
event_id == "LOCAL_SORT_V1"
outcome == "SUCCESS"
```

If these criteria are not satisfied, the result is:

```text
local_criteria_rejected
```

If the signature is valid and the criteria match, the result is:

```text
accepted = true
reason = accepted
```

The criteria are local to the verifier implementation.

They do not grant permission to execute another operation.

## 3.9 Verification Results

The verifier returns a structured result containing:

```text
accepted
reason
signature_checks
artifact_sha256
```

Some malformed-input results also include diagnostic detail.

Important rejection reasons include:

```text
malformed
untrusted_producer_key_binding
invalid_signature
local_criteria_rejected
```

An invalid Ed25519 signature produces:

```text
accepted = false
reason = invalid_signature
```

The result is a verification decision.

It is not a record that an operation was executed.

## 3.10 Stateless Behavior

The module does not store previously accepted artifact identifiers.

It does not mark artifacts as spent.

It does not maintain a replay database.

A valid artifact may therefore be verified more than once.

This behavior is intentional for the MD001 experiment.

**Repeated verification is not equivalent to authorization for repeated execution.**

A system requiring single-use execution authority must enforce that property separately.

---

# 4. hub.py — Mechanical Relay

## 4.1 Responsibility

`hub.py` implements a mechanical TCP/HTTP forwarding service inherited from the MH001 architecture.

Its source declares:

```python
"""MH001 mechanical single-threaded hub. No authorization or provider-state logic."""
```

The relay receives an HTTP request, selects a configured route, and forwards the request.

It does not verify the MD001 assertion signature.

It does not issue or enlarge authority.

It does not maintain provider authorization state.

## 4.2 Request Processing

The handler performs the following operations:

```text
Receive connection
       |
       v
Parse HTTP request
       |
       v
Read destination header
       |
       v
Resolve configured route
       |
       v
Read request body
       |
       v
Record ingress observation
       |
       v
Open downstream connection
       |
       v
Forward request
       |
       v
Receive downstream response
       |
       v
Return response to requester
```

The destination header is:

```text
X-MH-Destination
```

The accepted destination identifiers are:

```text
PROVIDER_A
PROVIDER_B
```

The relay rejects missing, duplicate, or unsupported destination values.

The destination header selects a configured route.

It does not authorize the operation described by the artifact.

## 4.3 Mechanical Forwarding

The relay constructs the downstream request using `wire.py`.

The request body is forwarded without intentional modification.

The relay may reconstruct HTTP framing and replace the Host header for the next hop.

The distinction is:

```text
HTTP transport framing may change.

Signed artifact body must remain unchanged.
```

This property is important because changing signed artifact bytes would invalidate the signature.

## 4.4 No Automatic Retry

The implementation makes one downstream connection attempt.

The request is sent using:

```python
downstream.sendall(packet)
```

The source explicitly specifies:

```python
# Exactly one send attempt. Never retry.
```

The relay does not implement automatic retry, redirect, or failover behavior.

This avoids introducing additional submission attempts through the relay.

It does not guarantee that a downstream application processes a request exactly once.

## 4.5 Transport Observations

The relay records:

```text
hub_id
sequence
timestamp
ingress_body_sha256
egress_body_sha256
preserved_headers
next_hop
transport_result
```

The observations are written as JSON lines.

The ingress observation is flushed before attempting downstream submission.

The relay also records a final transport result.

These observations support investigation of the forwarding path.

They are not authorization decisions.

## 4.6 Observation Limitations

The relay calculates an egress body hash before calling `sendall`.

Therefore, the egress diagnostic records the bytes intended for transmission.

It does not independently establish that the downstream host received those bytes.

The physical MD001 experiments address this distinction through separate packet captures and verifier-ingress observations.

## 4.7 Error Handling

The relay generates bounded HTTP error responses for selected transport failures.

Examples include:

```text
invalid_destination
downstream_timeout
downstream_unreachable_or_io
unsupported_downstream_response
client_io_or_observation_error
```

These errors describe transport behavior.

They do not establish whether the underlying signed assertion is cryptographically valid.

---

# 5. routes.py — Static Route Validation

## 5.1 Responsibility

`routes.py` validates the frozen MH001 routing topology.

The module declares:

```python
"""Strict, static MH001 topology. Loading never resolves names or contacts hosts."""
```

The routing configuration uses numeric IP addresses.

It does not perform DNS resolution during configuration loading.

## 5.2 Supported Destinations

The module defines:

```python
DESTINATIONS = {
    "PROVIDER_A",
    "PROVIDER_B"
}
```

The frozen topology supports:

```text
HUB_A
HUB_B
PROVIDER_A
PROVIDER_B
```

The route validator requires the expected next-hop relationships.

It does not permit arbitrary route definitions.

## 5.3 Configuration Validation

The module validates:

- Exact configuration fields.
- Hub identity.
- Numeric endpoint addresses.
- Port ranges.
- Frozen timeout values.
- Required destination entries.
- Expected next-hop identities.
- Self-routing restrictions.
- Route-pair consistency.
- Routing-loop prevention.

Duplicate JSON configuration keys are rejected.

Nonfinite JSON constants are rejected.

## 5.4 Numeric Endpoints

An endpoint must contain exactly:

```text
host
port
```

The host must be a canonical numeric unicast IP address.

The port must be an integer between:

```text
1 and 65535
```

DNS names are not accepted.

This prevents route selection from depending on DNS resolution.

## 5.5 Frozen Timeout Values

The route validator requires:

```text
HUB_A = 15 seconds
HUB_B = 10 seconds
```

These values are part of the inherited MH001 topology.

They are not derived from MD001 authorization policy.

## 5.6 Routing Boundaries

The validator rejects:

- Unexpected destinations.
- Invalid hub identities.
- Inconsistent next-hop endpoints.
- Self-routes.
- Routing loops.
- Incorrect terminal providers.
- Forbidden reverse hub relationships.

These restrictions constrain transport topology.

They do not grant or deny execution authority.

---

# 6. wire.py — HTTP Framing and Transport

## 6.1 Responsibility

`wire.py` implements bounded HTTP/1 parsing and request reconstruction.

The module declares:

```python
"""Bounded HTTP/1 framing; opaque field lines are preserved byte-for-byte."""
```

It is responsible for transport syntax.

It does not parse the MD001 signed assertion as an authorization object.

It does not perform Ed25519 verification.

## 6.2 Request Limits

The module defines:

```python
MAX_BODY = 65536
MAX_HEAD = 65536
```

These values establish:

```text
Maximum request body: 65,536 bytes
Maximum header section: 65,536 bytes
```

The parser also limits the number of header entries.

Requests exceeding supported bounds are rejected.

The response parser does not impose the same 65,536-byte body limit.

## 6.3 HTTP Parsing

The module parses:

- Request lines.
- Header fields.
- Content-Length.
- Request bodies.
- Response status lines.
- Response headers.
- Response bodies.

It requires supported HTTP/1 framing.

Malformed or unsupported framing produces a `WireError`.

## 6.4 Unsupported Transport Features

The implementation rejects or does not implement:

- Chunked transfer encoding.
- Unsupported transfer encoding.
- CONNECT tunneling.
- Expect/100-continue behavior.
- HTTP protocol upgrades.
- Unsupported connection tokens.
- Malformed Content-Length.
- Truncated request bodies.

These restrictions reduce ambiguity in the supported transport path.

They do not make the implementation a general-purpose HTTP proxy.

## 6.5 Header Preservation

The module excludes selected hop-by-hop headers during forwarding.

These include:

```text
Host
Connection
Keep-Alive
Proxy-Connection
TE
Trailer
Transfer-Encoding
Upgrade
Proxy-Authenticate
Proxy-Authorization
```

Other retained header lines are forwarded using their original raw representation.

The Host header is reconstructed for the configured downstream endpoint.

The signed artifact body is not intentionally rewritten.

## 6.6 Numeric Connection Targets

The connection function uses numeric IP addresses.

The source explicitly specifies:

```python
# One numeric endpoint, one connect call: no DNS, failover, redirect, or retry.
```

The transport therefore does not depend on DNS-based next-hop discovery.

## 6.7 Response Handling

The module buffers the complete framed downstream response before forwarding it.

This prevents a partial downstream response from being followed by a fabricated relay error.

The response parser validates supported HTTP framing.

The relay then returns the received response to the requester.

The response remains a downstream application result.

The transport layer does not reinterpret it as an authorization grant.

---

# 7. Source Provenance

The runtime modules have different origins.

### MD001-Specific Artifact Module

```text
artifact.py
```

This module implements the MD001 assertion contract.

Its purpose is cryptographic verification of the defined assertion format.

### MH001-Derived Transport Modules

```text
hub.py
routes.py
wire.py
```

These modules preserve the mechanical forwarding and static-routing behavior used in the earlier MH001 implementation.

The MD001 implementation reuses transport functionality without importing the earlier provider authorization or consumption model.

The original project and runtime integrity records are preserved in:

```text
../ORIGINAL_PROJECT_LOCK.json
../RUNTIME_LOCK.json
```

Additional source-provenance documentation is available in:

```text
../desktop/MULTI_DOMAIN_001/
```

---

# 8. Component Boundaries

The implementation deliberately limits each component's responsibilities.

| Capability | artifact.py | hub.py | routes.py | wire.py |
|---|---|---|---|---|
| Canonical assertion encoding | Yes | No | No | No |
| Ed25519 verification | Yes | No | No | No |
| Public-key trust resolution | Yes | No | No | No |
| Local assertion criteria | Yes | No | No | No |
| HTTP forwarding | No | Yes | No | Supporting |
| Static route validation | No | No | Yes | No |
| HTTP framing | No | Uses | No | Yes |
| Transport observations | No | Yes | No | No |
| Durable artifact-consumption ledger | No | No | No | No |
| Execution authorization | No | No | No | No |
| Physical operation execution | No | No | No | No |

The runtime separates verification from transport.

It does not implement a complete execution-authorization system.

---

# 9. Relationship to Scored Experiments

The runtime components support three physical-network experiments.

## B01 — Valid Assertion

The producer creates a signed assertion.

The relay transports it.

The verifier accepts it using locally provisioned public-key trust.

Recorded result:

```text
PASS
```

Evidence:

```text
../evidence/B01_SCORED_20261119_223940/
```

## N01 — Modified Assertion

A signed field is modified after signing.

The original signature remains attached.

The verifier rejects the modified assertion.

Recorded result:

```text
PASS
```

Evidence:

```text
../evidence/N01_SCORED_20261119_224654/
```

## B02 — Producer-Unavailable Verification

The original signed assertion is preserved.

The producer is physically disconnected.

The assertion is resubmitted through the relay.

A fresh verifier process accepts the original assertion.

Recorded result:

```text
PASS
```

Evidence:

```text
../evidence/B02_SCORED_20261119_225126/
```

The scored evidence directories contain the primary observations.

The runtime source alone does not establish that a physical experiment succeeded.

---

# 10. Security Properties and Limitations

## Properties Implemented

The source implements:

- Canonical assertion encoding.
- Ed25519 signature verification.
- Locally provisioned public-key binding.
- Rejection of modified signed assertions.
- Strict artifact structure validation.
- Bounded request parsing.
- Static numeric routing.
- Mechanical request forwarding.
- No automatic downstream retry.
- Transport diagnostic observations.

## Properties Not Implemented

The runtime does not implement:

- Identity-provider authentication.
- Execution authorization.
- Durable single-use authority consumption.
- Replay prevention.
- Revocation infrastructure.
- Signing-key compromise recovery.
- Physical actuation enforcement.
- General-purpose HTTP proxy functionality.
- Production-grade confidentiality.
- TLS transport.

The laboratory transport uses plaintext HTTP.

The signed assertion provides cryptographic integrity and authenticity relative to the provisioned key.

It does not provide confidentiality.

## Important Distinction

A valid signature establishes that the assertion was signed using the corresponding private key.

It does not independently establish that the asserted event actually occurred.

Likewise, a successful verification result does not authorize execution of a subsequent operation.

Those responsibilities remain outside this runtime's defined scope.

---

# 11. Independent Review

A reviewer can inspect the runtime without operating the laboratory network.

Recommended sequence:

1. Inspect `artifact.py` for assertion encoding and signature verification.
2. Inspect `hub.py` for mechanical forwarding and transport observations.
3. Inspect `routes.py` for static route restrictions.
4. Inspect `wire.py` for HTTP framing and byte-preservation behavior.
5. Compare source identities against `RUNTIME_LOCK.json`.
6. Review the local validation records.
7. Review the physical-network scored evidence.

Supporting directories:

```text
../validation/

../support/MD001_DEPLOYMENT_R1/

../support/MD001_RUNTIME_REVIEW_R1/

../evidence/
```

The runtime compatibility review documents the distinction between the frozen dependency requirement and the installed Linux environments used during preparation.

The scored evidence documents actual laboratory behavior.

---

# 12. Conclusion

The MD001 runtime separates cryptographic assertion verification from mechanical transport.

`artifact.py` evaluates signed assertions using locally provisioned public-key trust.

`hub.py`, `routes.py`, and `wire.py` provide bounded transport, static routing, and HTTP framing without becoming assertion-signing or execution-authorizing components.

The runtime does not maintain shared authorization state or a durable artifact-consumption ledger.

The physical-network B01, N01, and B02 experiments provide the corresponding evidence for valid assertion verification, modified-assertion rejection, and verification after producer unavailability.

**The central boundary is preserved: transporting a signed assertion does not confer authority to create, validate, authorize, or execute the operation it describes.**
