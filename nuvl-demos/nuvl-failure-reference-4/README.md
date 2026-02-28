# NUVL Failure Reference 4 — Network Failure (Provider Unreachable)

## Overview

This reference demonstrates a network failure scenario in which NUVL performs deterministic request binding and attempts to forward a verification artifact, but the provider-controlled system is intentionally unavailable.

NUVL remains a stateless intermediary:

- It derives a non-reversible request representation (SHA-256 in this reference).
- It applies a deterministic binding transform.
- It constructs a verification artifact.
- It attempts asynchronous forwarding.
- It disengages and returns a constant HTTP 204 response.

In this reference, the provider is not started. Artifact forwarding therefore fails at the transport layer.

Authorization authority remains exclusively within provider-controlled systems.

---

## Design Goals

This reference is designed to:

- Demonstrate that transport failure does not create intermediary execution authority
- Preserve provider-exclusive initiation under provider unreachability conditions
- Show that NUVL does not infer execution outcomes from network state
- Maintain constant-response disengagement behavior under network disruption

---

## Non-Goals

This reference does not:

- Provide transport-level delivery guarantees or retries
- Provide queueing, buffering, or store-and-forward reliability
- Provide requester correlation to provider decisions
- Provide identity validation, authentication, or session state
- Model production-grade network security controls

This demo constrains authority location. It does not implement network resilience mechanisms.

---

## Scenario Definition

### Failure Condition

The provider-controlled system is intentionally not running.

NUVL computes the artifact normally and attempts to forward it to:

- `http://127.0.0.1:9090/ingest`

Forwarding fails due to provider unreachability. The forwarding attempt is best-effort and asynchronous.

### Authority Boundary

- NUVL does not initiate execution and does not assume decision authority.
- Provider-side initiation can occur only inside the provider-controlled system.
- Provider absence prevents initiation; transport failure does not transfer authority to NUVL.

---

## Architectural Model

### Execution Flow

Requester → NUVL → (Unreachable Provider)

1. A requester submits opaque request bytes to NUVL.
2. NUVL derives `request_repr` and computes the deterministic binding.
3. NUVL constructs a verification artifact.
4. NUVL attempts to forward the artifact asynchronously.
5. NUVL disengages and returns HTTP 204 with a blank body.
6. Provider is unavailable and does not receive the artifact.

NUVL does not observe provider-side evaluation outcomes and does not infer execution state.

---

## Verification Artifact Structure (Reference)

This reference constructs an artifact containing:

- `request_repr` — SHA-256 of request bytes
- `verification_context` — opaque header value
- `binding` — deterministic binding transform output

Field names are illustrative. Structure is provider-defined.

---

## Running the Reference

```bash
python3 nuvl-failure-reference-4.py
```

Ports used by this reference:

- NUVL: `127.0.0.1:8080` (`POST /nuvl`)
- Provider: intentionally not started (`127.0.0.1:9090`)

---

## Expected Behavior

- The requester receives HTTP 204 responses.
- NUVL performs deterministic binding and attempts forwarding.
- Provider is unreachable and does not receive artifacts.
- NUVL remains outcome-blind and authority-neutral.

---

## Security Model

Authorization authority is provider-scoped.

- NUVL does not hold signing material.
- NUVL does not evaluate authorization semantics.
- NUVL does not guarantee artifact delivery.
- Authorization is realized exclusively by provider-side initiation.

This reference demonstrates that provider unreachability yields a fail-closed condition without transferring execution authority to the intermediary.

---

## License

Licensed under the Apache License, Version 2.0.
