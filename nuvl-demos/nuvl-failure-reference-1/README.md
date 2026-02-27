# NUVL Failure Reference 1 — Malformed Binding

## Overview

This reference demonstrates a binding-integrity failure scenario in which NUVL forwards a verification artifact containing a deliberately malformed (mismatching) binding value.

NUVL remains a stateless intermediary:

- It derives a non-reversible request representation (SHA-256 in this reference).
- It constructs an artifact.
- It forwards the artifact to a provider-controlled system.
- It disengages and returns a constant HTTP 204 response.

NUVL does not evaluate authorization policy, enforce access control, or initiate operations.

Authorization authority resides exclusively within provider-controlled systems.

---

## Design Goals

This reference is designed to:

- Demonstrate that a malformed binding does not create intermediary decision authority
- Preserve provider-exclusive evaluation of binding correctness
- Keep NUVL outcome-blind and stateless under binding failure conditions
- Show that artifact forwarding can occur without intermediary interpretation

---

## Non-Goals

This reference does not:

- Provide identity, authentication, or credential validation
- Provide replay protection, freshness semantics, or clock coordination
- Require NUVL to validate artifact correctness
- Require NUVL to receive or relay provider outcomes
- Hardening against denial-of-service or transport-layer abuse

This demo constrains authority location. It does not secure provider implementations.

---

## Scenario Definition

### Failure Condition

NUVL intentionally emits a binding value that cannot match provider-expected derivation.

In this reference:

- `request_repr` is computed as `SHA-256(request_bytes)` (hex)
- `verification_context` is read from `X-Verification-Context`
- `binding` is forcibly set to a constant malformed value:

```python
binding = "00" * 32
```

The artifact is forwarded exactly as constructed.

### Authority Boundary

- NUVL holds no signing keys and performs no semantic checks.
- The provider independently computes its expected binding and evaluates the artifact.
- Any provider-side boundary signature (HMAC in this reference) is computed inside the provider boundary and is not exported to NUVL.

---

## Architectural Model

### Execution Flow

Requester → NUVL → Provider

1. Requester submits opaque request bytes to NUVL.
2. NUVL computes `request_repr` and constructs an artifact.
3. NUVL forwards the artifact asynchronously to the provider ingest endpoint.
4. NUVL disengages and returns HTTP 204 with a blank body.
5. The provider evaluates the artifact under provider-defined logic.

NUVL does not observe provider-side evaluation outcomes.

---

## Verification Artifact Structure (Reference)

This reference forwards an artifact containing:

- `request_repr` — SHA-256 of request bytes
- `verification_context` — opaque header value
- `binding` — intentionally malformed binding value

Field names are illustrative. Structure is provider-defined.

---

## Running the Reference

```bash
python3 nuvl-failure-reference-1.py
```

Ports used by this reference:

- NUVL: `127.0.0.1:8080` (`POST /nuvl`)
- Provider: `127.0.0.1:9090` (`POST /ingest`)

---

## Expected Behavior

- The requester receives HTTP 204 responses.
- NUVL forwards artifacts without interpretation.
- The provider evaluates binding correctness exclusively within its boundary.
- NUVL does not emit or relay authorization outcomes.

---

## Security Model

Authorization authority is provider-scoped.

- NUVL does not hold signing material.
- NUVL does not evaluate authorization semantics.
- Authorization is realized exclusively by provider-side initiation.
- Compromise of NUVL does not grant authorization capability.

This reference demonstrates that binding integrity enforcement remains provider-controlled even when the intermediary forwards malformed artifacts.

---

## License

Licensed under the Apache License, Version 2.0.
