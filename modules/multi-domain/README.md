# Stateless Verification Architecture Across Multiple Domains

## Overview

This repository provides a minimal executable reference implementation for a domain-scoped verification architecture.

A neutral intermediary performs mechanical request representation and artifact conveyance across domain boundaries.  
It does not evaluate authorization policy, enforce access control, or initiate operations.

Authorization authority remains domain-scoped: each domain independently determines whether to initiate execution.

This reference implementation is written in Python for portability and zero-dependency execution.  
The architectural constraints are language-agnostic.

---

## Design Goals

This architecture is designed to:

- Support verification conveyance across multiple domains without centralizing authorization
- Preserve domain-scoped authority and execution initiation
- Avoid migration of authorization logic into intermediaries
- Avoid shared signing material across domains
- Operate without retained state across requests at the intermediary
- Enable independent domain evaluation using domain-selected logic

---

## Non-Goals

This architecture does not:

- Provide a universal authorization decision across domains
- Merge or reconcile domain policies into a shared enforcement layer
- Require identity propagation across domain boundaries
- Require shared signing keys or shared policy semantics
- Protect against denial-of-service conditions
- Secure domain implementations

This architecture constrains authority location. It does not replace domain security controls.

---

## Architectural Model

### Execution Flow

Requester → Intermediary → Domain A / Domain B / Domain C

1. A requester submits an opaque operation request to the intermediary.
2. The intermediary derives a non-reversible request representation (SHA-256 in this reference).
3. The intermediary constructs and conveys a verification artifact to one or more domains.
4. Each domain independently evaluates the artifact using domain-selected logic.
5. Execution is authorized only by domain-side initiation of execution within that domain boundary.
6. The intermediary returns a constant HTTP 204 response and does not observe outcomes.

---

## Authority Boundary

### Intermediary

- Holds no signing keys
- Maintains no authorization policy
- Executes no decision logic
- Retains no cross-request state
- Does not initiate operations
- Does not emit evaluation outcomes

### Domain-Controlled Systems

- Define domain-local evaluation semantics
- Hold domain-local signing material (if any)
- Evaluate verification artifacts
- Determine whether to initiate execution
- Emit any domain-side execution boundary representations

Cross-domain compromise does not automatically grant cross-domain authorization authority.

---

## Running the Reference

~~~bash
python3 MDSV.py
~~~

## Expected behavior

- The requester receives HTTP 204.
- Each domain independently prints `INITIATED` when its authorization conditions are satisfied.
- No authorization decision is returned to the requester.
- The intermediary does not emit evaluation outcomes.

---

## Security Model

Authorization authority is domain-scoped.

- Intermediaries do not hold signing material.
- Domains do not share authorization logic.
- Execution initiation occurs only within domain boundaries.
- Cross-domain compromise does not automatically grant cross-domain authority.

The architecture enforces authority isolation rather than shared enforcement.

---

## Licensing

This module is not released under the Apache 2.0 license applied to the repository root.

Commercial licensing terms apply.

Non-commercial research evaluation may be available upon request.
