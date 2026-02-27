# NUVL Failure Reference 2 — Forwarding Malfunction

## Overview

This reference demonstrates a forwarding disruption scenario in which NUVL performs request binding but does not deliver the verification artifact to the provider-controlled system.

NUVL remains a stateless intermediary:

- It derives a non-reversible request representation (SHA-256 in this reference).
- It applies the deterministic provider-defined binding transform.
- It constructs a verification artifact.
- It disengages and returns a constant HTTP 204 response.

In this reference, artifact conveyance is intentionally suppressed.

Authorization authority remains exclusively within provider-controlled systems.

---

## Design Goals

This reference is designed to:

- Demonstrate structural separation between binding and conveyance
- Show that NUVL does not assume delivery guarantees
- Preserve provider-exclusive execution authority under transport failure conditions
- Maintain stateless intermediary behavior despite forwarding disruption

---

## Non-Goals

This reference does not:

- Implement delivery retry semantics
- Implement transport-level reliability guarantees
- Provide acknowledgment correlation between provider and requester
- Provide authorization evaluation within NUVL
- Introduce coordination logic into the intermediary

This demo constrains authority location. It does not model production network resilience.

---

## Scenario Definition

### Failure Condition

NUVL computes a valid binding but intentionally drops the artifact before transmission.

In this reference:

- `request_repr` is computed as `SHA-256(request_bytes)` (hex)
- `binding` is derived deterministically using the provider-defined binding transform
- The forwarding function is intentionally disabled:

```python
def forward_artifact_async(_artifact: dict) -> None:
    # FAILURE: drop forward (provider never sees anything)
    return
```

The artifact is constructed but not transmitted.

### Authority Boundary

- NUVL performs binding but does not evaluate authorization semantics.
- The provider holds binding expectations and signing material.
- Provider-side boundary signature computation remains internal to the provider.
- Execution authority does not migrate into the intermediary under forwarding disruption.

---

## Architectural Model

### Execution Flow

Requester → NUVL → (No Delivery) → Provider

1. A requester submits opaque request bytes to NUVL.
2. NUVL derives `request_repr` and computes the deterministic binding.
3. NUVL constructs a verification artifact.
4. Artifact forwarding is intentionally suppressed.
5. NUVL disengages and returns HTTP 204.
6. The provider does not receive the artifact.

NUVL does not observe or infer provider-side execution state.

---

## Verification Artifact Structure (Reference)

This reference constructs an artifact containing:

- `request_repr` — SHA-256 of request bytes
- `verification_context` — opaque header value
- `binding` — deterministic provider-defined transform output

Field names are illustrative. Structure is provider-defined.

---

## Stateless Operation

NUVL processes each request independently.

Information derived from a request exists only for the duration required to compute the binding and construct the artifact.

No cross-request state is retained.

---

## Running the Reference

```bash
python3 nuvl-failure-reference-2.py
```

Ports used by this reference:

- NUVL: `127.0.0.1:8080` (`POST /nuvl`)
- Provider: `127.0.0.1:9090` (`POST /ingest`)

---

## Expected Behavior

- The requester receives HTTP 204 responses.
- NUVL performs deterministic binding.
- Artifact forwarding is intentionally suppressed.
- NUVL does not emit authorization outcomes.
- Provider-side authority remains exclusive to the provider-controlled boundary.

---

## Security Model

Authorization authority is provider-scoped.

- NUVL does not hold signing material.
- NUVL does not evaluate authorization semantics.
- NUVL does not guarantee artifact delivery.
- Authorization is realized exclusively by provider-side initiation.

This reference demonstrates that interruption of artifact conveyance does not transfer execution authority to the intermediary.

---

## License

Licensed under the Apache License, Version 2.0.
