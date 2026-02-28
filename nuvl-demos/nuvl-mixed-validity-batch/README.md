# NUVL Demo — Mixed Validity Batch (25)

## Overview

This reference demonstrates a controlled mixed-validity batch run in which a requester issues 25 requests through NUVL while injecting a mixture of validity conditions.

NUVL remains a stateless verification intermediary:

- It derives a non-reversible request representation (SHA-256 in this reference).
- It applies a deterministic binding transform over request representation and an opaque verification context.
- It constructs a verification artifact.
- It forwards the artifact to a provider-controlled system.
- It disengages and returns a constant HTTP 204 response.

Authorization authority resides exclusively within provider-controlled systems.

---

## Design Goals

This reference is designed to:

- Exercise NUVL under mixed-validity traffic without introducing intermediary policy semantics
- Demonstrate stateless processing across a batch of heterogeneous request conditions
- Preserve provider-exclusive authorization authority across all requests
- Validate that transport handling and constant-response behavior remain invariant under batch execution

---

## Non-Goals

This reference does not:

- Provide identity, authentication, or credential validation
- Provide replay protection, freshness semantics, or clock coordination
- Provide delivery guarantees, queueing, or retry orchestration
- Provide aggregation-based authorization or batch-level decision logic
- Provide requester visibility into provider evaluation outcomes

This demo constrains authority location. It does not secure provider implementations.

---

## Scenario Definition

### Batch Composition (25)

This reference executes a 25-request run with a mixture of request conditions:

- Valid requests using the expected verification context
- Requests using non-expected / spoofed verification context values
- Oversized requests exceeding the configured maximum request size threshold

The batch is randomized per execution using a shuffled index selection.

The goal is to introduce heterogeneity without adding state or semantic interpretation into NUVL.

### Validity Injection Mechanisms

This reference injects mixed validity by varying:

- `X-Verification-Context` header values
- request payload size relative to `MAX_REQUEST_BYTES`

NUVL processes each inbound request independently and applies the same mechanical rules per request.

---

## Architectural Model

### Execution Flow

Requester → NUVL → Provider

For each request in the batch:

1. Requester submits opaque request bytes to NUVL with an `X-Verification-Context` header.
2. NUVL enforces a fixed maximum request size (`MAX_REQUEST_BYTES`).
3. NUVL derives `request_repr` as `SHA-256(request_bytes)` (hex).
4. NUVL computes a deterministic binding transform.
5. NUVL constructs a verification artifact and forwards it asynchronously.
6. NUVL disengages and returns HTTP 204 with a blank body.
7. The provider evaluates artifacts under provider-defined logic.

NUVL does not observe provider-side evaluation outcomes.

---

## Verification Artifact Structure (Reference)

For non-oversized requests, the reference implementation constructs an artifact containing:

- `request_repr` — SHA-256 of request bytes
- `verification_context` — opaque header value
- `binding` — deterministic binding transform output

Field names are illustrative; structure is provider-defined.

---

## Stateless Operation

NUVL retains no cross-request state.

Mixed validity is introduced solely through per-request variation of:

- payload size
- verification context

No batch-level coordination, ordering semantics, or inference mechanisms are introduced.

---

## Running the Reference

```bash
python3 nuvl-mixed-validity-batch.py
```

Ports used by this reference:

- NUVL: `127.0.0.1:8080` (`POST /nuvl`)
- Provider: `127.0.0.1:9090` (`POST /ingest`)

---

## Expected Behavior

- The requester receives HTTP 204 responses for accepted-size requests.
- Oversized requests are dropped by NUVL according to the configured maximum request size threshold.
- NUVL forwards constructed artifacts without interpreting verification semantics.
- Provider-side initiation authority remains exclusive to the provider-controlled boundary.
- NUVL does not emit or relay authorization outcomes.

---

## Security Model

Authorization authority is provider-scoped.

- NUVL does not hold signing material.
- NUVL does not evaluate authorization semantics.
- Authorization is realized exclusively by provider-side initiation.
- Mixed-validity traffic does not migrate authority into the intermediary.

This reference demonstrates that heterogeneous request conditions can be exercised without introducing intermediary policy logic or batch-level authority.

---

## License

Licensed under the Apache License, Version 2.0.
