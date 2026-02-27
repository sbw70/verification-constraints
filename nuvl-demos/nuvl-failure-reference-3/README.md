# NUVL Failure Reference 3 — Malformed Artifact

## Overview

This reference demonstrates an artifact-structure failure scenario in which NUVL does not forward a valid verification artifact, and instead transmits intentionally malformed JSON to the provider ingest endpoint.

NUVL remains a stateless intermediary:

- It receives opaque request bytes.
- It does not evaluate authorization policy, enforce access control, or initiate operations.
- It returns a constant HTTP 204 response and disengages.

In this reference, artifact formation is intentionally bypassed to demonstrate provider-side authority under malformed artifact conditions.

Authorization authority remains exclusively within provider-controlled systems.

---

## Design Goals

This reference is designed to:

- Demonstrate that artifact structure validity is enforced provider-side
- Show that NUVL does not become a validator or schema authority
- Preserve provider-exclusive execution authority under malformed artifact conditions
- Maintain constant-response disengagement behavior in the intermediary

---

## Non-Goals

This reference does not:

- Provide artifact schema enforcement in NUVL
- Provide delivery guarantees or retries
- Provide requester visibility into provider outcomes
- Provide identity, credential validation, or session state
- Model production-grade transport hardening

This demo constrains authority location. It does not secure provider implementations.

---

## Scenario Definition

### Failure Condition

NUVL intentionally transmits malformed JSON to the provider ingest endpoint.

In this reference:

- Normal artifact formation is bypassed.
- A truncated JSON fragment is sent:

```python
data = b'{"request_repr":'
```

The provider receives input that cannot be parsed as valid JSON.

### Authority Boundary

- NUVL does not validate or interpret provider-side artifact requirements.
- The provider independently determines whether input is acceptable and whether initiation is permitted.
- Provider-only signing material (HMAC key in this reference) remains inside the provider boundary.
- Malformed artifacts do not transfer evaluation authority to the intermediary.

---

## Architectural Model

### Execution Flow

Requester → NUVL → Provider

1. A requester submits opaque request bytes to NUVL.
2. NUVL intentionally bypasses normal artifact construction.
3. NUVL forwards malformed JSON to the provider ingest endpoint.
4. NUVL disengages and returns HTTP 204 with a blank body.
5. The provider applies provider-defined acceptance and evaluation logic.

NUVL does not observe provider-side evaluation outcomes.

---

## Artifact Conveyance Behavior

This reference intentionally violates artifact formatting to demonstrate that:

- Artifact correctness is not determined by the intermediary.
- The provider remains the sole authority for acceptance criteria.
- Intermediary transport does not imply artifact validity.

---

## Running the Reference

```bash
python3 nuvl-failure-reference-3.py
```

Ports used by this reference:

- NUVL: `127.0.0.1:8080` (`POST /nuvl`)
- Provider: `127.0.0.1:9090` (`POST /ingest`)

---

## Expected Behavior

- The requester receives HTTP 204 responses.
- NUVL forwards malformed input without acting as a validator.
- Provider-side acceptance and initiation logic remains provider-controlled.
- NUVL remains outcome-blind and authority-neutral.

---

## Security Model

Authorization authority is provider-scoped.

- NUVL does not hold signing material.
- NUVL does not evaluate authorization semantics.
- Artifact structure enforcement is provider-defined.
- Authorization is realized exclusively by provider-side initiation.

This reference demonstrates that malformed artifact conveyance does not migrate authority into the intermediary.

---

## License

Licensed under the Apache License, Version 2.0.
