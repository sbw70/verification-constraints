# Stateless Verification Architecture Across Multiple Domains

## Overview

This module provides a minimal executable reference implementation for a domain-scoped verification architecture.

A neutral intermediary performs mechanical request representation and artifact conveyance across domain boundaries.

It does not evaluate authorization policy, enforce access control, or initiate operations.

Authorization authority remains domain-scoped: each domain independently determines whether to initiate execution.

The reference implementation is written in Python for portability and zero-dependency execution.

The architectural constraints are language-agnostic.

The module also contains **MD001**, a separately developed and physically tested implementation evaluating signed assertion verification across independent technical domains.

---

## 1. Module Contents

    multi-domain/
    |
    |-- README.md
    |-- AI_ASSIST.md
    |-- MDSV.py
    |
    `-- MD001/
        |-- README.md
        |-- md001.py
        |-- observe.py
        |-- requirements.txt
        |
        |-- runtime/
        |-- configs/
        |-- validation/
        |-- desktop/
        |-- support/
        |
        `-- evidence/

The module contains two distinct implementations.

| Implementation | Purpose | Evidence |
| -------------- | ------- | -------- |
| `MDSV.py` | Minimal domain-scoped verification reference | Executable demonstration |
| `MD001/` | Signed assertion verification across a physical network | Three completed scored experiments |

These implementations illustrate related architectural constraints but use different verification mechanisms.

Their behavior and evidence should not be conflated.

---

## 2. Design Goals

This architecture is designed to:

- Support verification conveyance across multiple domains without centralizing authorization.
- Preserve domain-scoped authority and execution initiation.
- Avoid migration of authorization logic into intermediaries.
- Avoid shared signing material across domains.
- Operate without retained authorization state at the intermediary.
- Enable independent domain evaluation using domain-selected logic.

The intermediary may perform mechanical routing and artifact conveyance.

It does not become the authority responsible for authorizing operations.

---

## 3. Non-Goals

This architecture does not:

- Provide a universal authorization decision across domains.
- Merge domain policies into a shared enforcement layer.
- Require identity propagation across domain boundaries.
- Require shared signing keys or shared policy semantics.
- Protect against every denial-of-service condition.
- Secure compromised provider implementations.
- Guarantee that an asserted event actually occurred.

The architecture constrains authority location.

It does not replace domain security controls.

---

# PART I — MINIMAL REFERENCE IMPLEMENTATION

## 4. MDSV.py

`MDSV.py` is the original executable reference implementation.

It demonstrates domain-aware mechanical routing without centralizing authorization.

### Architecture

    REQUESTER
        |
        v
    NEUTRAL INTERMEDIARY
        |
        | X-Domain
        | Mechanical binding
        |
        +----------+
        |          |
        v          v
    DOMAIN A    DOMAIN B
        |          |
        v          v
    LOCAL       LOCAL
    EVALUATION  EVALUATION

The intermediary derives a SHA-256 representation of the request.

It constructs a deterministic binding incorporating:

    BIND_V1
    domain
    request representation
    verification context

The binding is not an authorization decision.

Each provider independently evaluates the received artifact.

The reference implementation uses provider-specific HMAC keys within its provider functions.

Those keys are not used by the intermediary's request-processing function.

### Execution Flow

1. A requester submits an operation request.
2. The intermediary reads the requested domain.
3. The intermediary selects the configured provider route.
4. The intermediary derives a SHA-256 request representation.
5. The intermediary constructs a mechanical binding.
6. The intermediary asynchronously conveys the artifact.
7. The provider independently evaluates the artifact.
8. The provider determines whether to initiate the represented operation.
9. The intermediary returns HTTP 204 without receiving the provider's decision.

The reference demonstrates separation between mechanical routing and provider-local evaluation.

It does not implement a complete production authorization system.

### Running the Reference

    python3 MDSV.py

The demonstration starts:

    Intermediary: port 8080

    Domain A: port 9090

    Domain B: port 9091

The requester submits one example request to each domain.

Expected requester response:

    HTTP 204

Provider-local output includes:

    DOMAIN_A: INITIATED
    DOMAIN_B: INITIATED

These messages represent the demonstration's provider-local evaluation results.

They are not evidence of physical actuation.

### Reference Limitations

The implementation uses demonstration-only provider secrets.

It uses plaintext HTTP and does not provide production-grade authentication, confidentiality, or operational enforcement.

Its provider evaluation checks the configured domain, verification context, and deterministic binding.

It should not be treated as proof that arbitrary requesters are authorized.

---

# PART II — MD001 PHYSICAL-NETWORK EXPERIMENT

## 5. MD001 — Multi-Domain Stateless Verification

MD001 evaluates whether an assertion originating in one technical domain can be independently verified in another domain.

The implementation uses:

- Ed25519 signed assertions.
- Locally provisioned public-key trust.
- A mechanical network relay.
- A separate receiving-domain verifier.
- Recorded artifact hashes.
- Physical-network packet captures.
- Scored positive and negative experiments.

Unlike the minimal `MDSV.py` reference, MD001 uses asymmetric cryptographic signatures.

The receiving verifier does not require the producer's private signing key.

### MD001 Architecture

    DOMAIN A
    Producer
    10.10.10.10
        |
        | Signed assertion
        v
    MECHANICAL RELAY
    30.30.30.30:18081
        |
        | Forwarded assertion
        v
    DOMAIN B INGRESS
    40.40.40.40:18443
        |
        v
    DOMAIN B VERIFIER
    127.0.0.1:18444
        |
        | Ed25519 verification
        v
    VERIFICATION RESULT

The relay transports the signed assertion.

Domain B independently evaluates it using locally provisioned public-key trust.

The relay does not possess the producer's signing authority.

### Operation Under Test

Domain A performs a local sorting operation:

    Input:
    [9, 1, 4, 2]

    Output:
    [1, 2, 4, 9]

The producer generates a signed assertion identifying:

    LOCAL_SORT_V1
    SUCCESS

Domain B evaluates the signed assertion.

The experiment tests verification of the assertion, not independent proof of the underlying sorting event.

---

## 6. MD001 Scored Results

Three physical-network experiments were completed on November 19, 2026.

| Experiment | Test | Result |
| ---------- | ---- | ------ |
| B01 | Valid signed assertion | PASS |
| N01 | Modified signed assertion | PASS |
| B02 | Verification after producer power loss | PASS |

### B01 — Valid Assertion

A valid signed assertion was transported through the mechanical relay.

Domain B accepted the assertion.

Recorded result:

    HTTP 200
    accepted = true
    reason = accepted
    signature_checks = 1

### N01 — Modified Assertion

A signed field was modified:

    SUCCESS -> FAILURE

The original signature was retained.

Domain B rejected the modified assertion.

Recorded result:

    HTTP 422
    accepted = false
    reason = invalid_signature
    signature_checks = 1

### B02 — Producer Unavailable

The original B01 assertion was preserved.

Domain A was physically disconnected from power.

The original assertion was resubmitted.

Domain B performed a fresh signature check and accepted it.

**Overall scored result: 3/3 PASS.**

---

## 7. MD001 Evidence and Documentation

The MD001 directory contains the complete implementation and supporting experimental records.

### Main Experiment

MD001 — Experiment Overview

### Scored Evidence

- B01 — Valid Assertion
- N01 — Modified Assertion
- B02 — Producer-Unavailable Verification

### Implementation

- Runtime Components
- Runtime Configuration
- Original Desktop Implementation

### Supporting Records

- Validation History
- Deployment Preparation
- Runtime Compatibility Review
- Public-Key Trust Configuration

### Supporting Experimental Evidence

- Positive Preflight
- Negative Preflight
- Runtime and Host Export

Each evidence directory contains its own documentation.

---

## 8. What MD001 Demonstrates

Within the recorded laboratory configuration, MD001 demonstrated:

**Valid assertion verification:** Domain B accepted a signed assertion originating from Domain A.

**Modification detection:** Domain B rejected an assertion whose signed content was modified.

**Producer independence:** Domain B verified the original assertion after Domain A was physically disconnected.

These observations support separation between assertion production, transport, and independent verification.

They do not establish that the underlying operation was authorized.

---

## 9. What MD001 Does Not Demonstrate

MD001 does not implement:

- Durable single-use authority consumption.
- Replay prevention.
- Execution authorization.
- Physical actuation enforcement.
- Signing-key compromise recovery.
- General protection against compromised provider hosts.

A valid assertion may be verified repeatedly.

That behavior is consistent with stateless assertion verification.

**Repeated verification does not authorize repeated execution.**

Systems requiring single-use execution authority must enforce that property separately.

---

## 10. Authority Boundary

The common architectural constraint across the module is that an intermediary may convey verification material without becoming the authority responsible for the represented operation.

### Intermediary

The intermediary may:

- Receive requests.
- Construct mechanical representations.
- Select configured routes.
- Forward verification artifacts.

It must not:

- Originate provider authorization.
- Enlarge provider-granted authority.
- Substitute authorization decisions.
- Execute provider-controlled operations.
- Treat routing information as authorization.

### Provider-Controlled Systems

Providers remain responsible for:

- Domain-local evaluation.
- Authorization criteria.
- Signing-key custody.
- Execution decisions.
- Operational enforcement.
- Any required replay or consumption controls.

The intermediary does not replace these functions.

---

## 11. Independent Review

Reviewers interested in the architectural reference should begin with:

    MDSV.py

Reviewers interested in the physical-network experiment should begin with:

    MD001/README.md

The MD001 evidence can be examined without deploying the implementation.

Recommended evidence order:

    B01 — Valid assertion

    N01 — Modified assertion

    B02 — Producer unavailable

Supporting preflight, validation, runtime, and configuration records are preserved separately.

Historical unsuccessful validation attempts remain part of the published record.

---

## 12. AI-Assisted Development Constraints

The module contains:

    AI_ASSIST.md

This file defines constraints for AI-assisted development and modification.

The central restrictions include:

- Domain routing must not become authorization.
- Intermediaries must not evaluate provider policy.
- Cross-domain fallback must not be introduced.
- Domain identifiers must not be treated as entitlement.
- Provider-controlled authority must remain within provider boundaries.

Review this file before modifying the module.

---

## 13. Licensing

This module is not released under the Apache 2.0 license applied to the repository root.

Commercial licensing terms apply.

Non-commercial research evaluation may be available upon request.

See the repository's module-specific licensing notices for applicable terms.

---

## 14. Conclusion

The multi-domain module contains two complementary implementations.

`MDSV.py` demonstrates domain-scoped evaluation with mechanical request representation and routing.

`MD001` extends the experimental evidence through signed assertions, independent verification, controlled modification, and producer-unavailable verification across a physical laboratory network.

The MD001 scored results were:

    B01 — PASS
    N01 — PASS
    B02 — PASS

Both implementations preserve the central architectural distinction:

**Mechanical conveyance of verification material does not transfer authorization authority to the intermediary.**
