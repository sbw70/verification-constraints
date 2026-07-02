# Neutral Unified Verification Layer (NUVL)

## Overview

The Neutral Unified Verification Layer (NUVL) is a stateless verification intermediary designed for insertion into an execution path without acquiring authorization authority.

NUVL performs mechanical request binding and artifact forwarding. It does not evaluate authorization policy, enforce access control, mint provider tokens, hold provider signing material, or initiate operations.

Authorization authority resides exclusively within provider-controlled systems.

This directory provides a minimal executable Python reference implementation. The architectural constraints are language-agnostic.

## Core Property

NUVL can participate in an execution path without becoming the authority that decides execution.

The request path may carry evidence.  
The provider remains the authority.

## Design Goals

NUVL is designed to:

- introduce a neutral verification layer into an operational path
- preserve exclusive authorization authority within provider-controlled systems
- avoid migration of authorization logic into intermediaries
- operate without retained state across requests
- forward verification artifacts without interpreting them
- disengage before provider-side execution decisions occur

## Non-Goals

NUVL does not:

- perform authorization evaluation
- enforce access control decisions
- validate identity credentials
- maintain policy logic
- mint provider tokens
- issue provider-side verification artifacts
- store signing keys or provider secrets
- relay provider decisions to requesters
- protect against denial-of-service conditions
- secure provider implementations

NUVL constrains authority location. It does not replace provider security controls.

## Architectural Model

Requester → NUVL → Provider

1. A requester submits opaque operation bytes to NUVL.
2. NUVL derives a request representation.
3. NUVL constructs or forwards a provider-bound verification artifact.
4. NUVL forwards the artifact to a provider-controlled system.
5. NUVL disengages and returns HTTP 204.
6. The provider independently evaluates the artifact and determines whether to initiate execution.

NUVL does not observe or receive provider-side evaluation outcomes.

## Authority Boundary

NUVL:

- holds no provider signing material
- mints no provider tokens
- maintains no authorization policy
- executes no decision logic
- retains no cross-request authorization state
- does not initiate operations

The provider-controlled system:

- defines binding semantics
- holds signing material, if used
- issues provider-side tokens or artifacts, if used
- evaluates verification artifacts
- determines whether to initiate operations
- generates execution-boundary representations

Compromise of NUVL does not confer authorization capability because authorization logic, signing material, token issuance, and execution decisions remain provider-side.

## Token Issuance

Token issuance is provider-side and outside NUVL’s scope by design.

NUVL does not mint provider tokens, issue provider-side verification artifacts, hold provider signing material, or decide whether a valid artifact authorizes execution.

The provider remains responsible for signing material, token issuance, artifact semantics, policy, authorization, and execution.

## Verification Artifact Structure

The reference implementation constructs an artifact containing:

- `request_repr` — request-byte representation
- `provider_element` — opaque provider-defined element
- `binding` — deterministic provider-defined transform output
- `version` — reference identifier

Field names are illustrative. Artifact structure and semantics are provider-defined.

The provider evaluates artifacts according to provider-defined logic.

## Stateless Operation

NUVL processes each request independently.

Information derived from a request exists only for the duration required to compute the binding and forward the artifact.

No historical, session, or cross-request authorization state is retained.

## Language-Agnostic Architecture

The reference implementation is written in Python 3 for portability and uses only the Python standard library. No third-party packages are required.

The architecture requires only:

- receipt of opaque request bytes
- a non-reversible request representation
- a deterministic provider-defined binding operation
- a forwarding mechanism
- immediate disengagement from the operational sequence

The design can be implemented in any programming language or execution environment.

## Running the Reference

Run:

`python3 nuvl.py`

Expected behavior:

- the requester receives HTTP 204
- NUVL emits no authorization outcome
- the provider independently evaluates the verification artifact
- execution occurs only if the provider initiates execution
- NUVL does not observe provider-side decisions

## Security Model

Authorization authority is provider-scoped.

NUVL does not hold provider signing material or mint provider tokens. NUVL does not evaluate authorization semantics. Authorization is realized exclusively by provider-side initiation.

NUVL enforces structural separation between artifact conveyance and authorization control.

## Link

[Project site](https://nuvltech.com)

## License

Licensed under the Apache License, Version 2.0.

This license applies to `nuvl-core/` and explicitly designated files only. Other directories, including `/modules/`, may be subject to separate licensing terms where indicated.
