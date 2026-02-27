# Neutral Unified Verification Layer (NUVL)

## Overview

The Neutral Unified Verification Layer (NUVL) is a stateless verification intermediary designed for insertion into an existing authorization path.

NUVL performs mechanical request binding and artifact forwarding.  
It does not evaluate authorization policy, enforce access control, or initiate operations.

Authorization authority resides exclusively within provider-controlled systems.

This repository provides a minimal executable reference implementation in Python.  
The architectural constraints are language-agnostic.

---

## Design Goals

NUVL is designed to:

- Introduce a neutral verification layer into an operational path
- Preserve exclusive authorization authority within provider-controlled systems
- Avoid migration of authorization logic into intermediaries
- Operate without retained state across requests
- Forward verification artifacts without interpreting them

---

## Non-Goals

NUVL does not:

- Perform authorization evaluation
- Enforce access control decisions
- Validate identity credentials
- Maintain policy logic
- Store signing keys or provider secrets
- Relay provider decisions to requesters
- Protect against denial-of-service conditions
- Secure provider implementations

NUVL constrains authority location. It does not replace provider security controls.

---

## Architectural Model

### Execution Flow

Requester → NUVL → Provider

1. A requester submits an opaque operation request to NUVL.
2. NUVL derives a non-reversible request representation (SHA-256 in this reference).
3. NUVL applies a provider-defined binding transform.
4. NUVL constructs a verification artifact.
5. NUVL forwards the artifact to a provider-controlled system.
6. NUVL disengages and returns a constant HTTP 204 response.

The provider independently evaluates the artifact and determines whether to initiate an operation.

NUVL does not observe or receive provider-side evaluation outcomes.

---

## Authority Boundary

### NUVL

- Holds no signing keys
- Maintains no authorization policy
- Executes no decision logic
- Retains no cross-request state
- Does not initiate operations

### Provider-Controlled System

- Defines binding semantics
- Holds signing material (if any)
- Evaluates verification artifacts
- Determines whether to initiate operations
- Generates any execution-boundary representations

Compromise of NUVL does not confer authorization capability, as no authorization logic or signing material is resident within the intermediary.

---

## Verification Artifact Structure (Reference)

The reference implementation constructs an artifact containing:

- `request_repr` — SHA-256 of request bytes
- `provider_element` — opaque provider-defined element
- `binding` — deterministic provider-defined transform output
- `version` — reference identifier

Field names are illustrative; structure is provider-defined.

The provider evaluates the artifact according to provider-defined logic.

---

## Stateless Operation

NUVL processes each request independently.

Information derived from a request exists only for the duration required to compute the binding and forward the artifact.

No historical or session state is retained.

---

## Language-Agnostic Architecture

The reference implementation is written in Python for portability and zero-dependency execution.

The architecture itself requires only:

- Receipt of opaque request bytes
- A non-reversible transformation
- A deterministic provider-defined binding operation
- A forwarding mechanism
- Immediate disengagement from the operational sequence

The design can be implemented in any programming language or execution environment.

---

## Running the Reference

```bash
python3 nuvl.py
```
---

## Expected Behavior

- The requester receives HTTP 204.
- NUVL does not emit authorization outcomes.
- The provider independently evaluates the verification artifact.
- Execution occurs only if the provider initiates execution.
- NUVL does not observe provider-side decisions.

---

## Security Model

Authorization authority is provider-scoped.

- NUVL does not hold signing material.
- NUVL does not evaluate authorization semantics.
- Authorization is realized exclusively by provider-side initiation.
- Compromise of NUVL does not grant authorization capability.

NUVL enforces structural separation between artifact conveyance and authorization control.

---

## License

Licensed under the Apache License, Version 2.0.  
  
This license applies to nuvl-core/ and explicitly designated files only. Other directories (e.g., /modules/) may be subject to separate licensing terms where indicated.
