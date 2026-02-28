# Demo — Multi-Provider Initiation  
## Multi-Provider • Adaptive Thresholds • Deterministic Byzantine • 2-of-3 Quorum

---

## Overview

This demo composes the NUVL core with a multi-provider execution mesh and an external quorum auditor.

The system includes:

- One stateless NUVL intermediary
- Three independent provider-controlled execution boundaries
- Provider-side adaptive threshold evaluation
- Deterministic Byzantine behavior (one provider flips after a configured threshold)
- A non-authoritative 2-of-3 quorum auditor
- Optional transport-level chaos at the intermediary

NUVL remains strictly mechanical:

- Derives a non-reversible request representation
- Computes deterministic binding
- Constructs verification artifacts
- Fans out artifacts to providers
- Returns constant HTTP 204

NUVL does not interpret execution state, evaluate policy, or aggregate quorum.

Execution authority remains exclusively inside provider boundaries.

---

## Design Goals

This demo is designed to:

- Demonstrate distributed provider-side authority
- Demonstrate adaptive provider evaluation independent of the intermediary
- Demonstrate deterministic Byzantine behavior without collapsing authority
- Demonstrate quorum aggregation without centralizing execution control
- Demonstrate intermediary fail-closed transport behavior
- Provide measurable stress characteristics under mixed request conditions

---

## Non-Goals

This demo does not:

- Provide production-grade persistence or retries
- Provide secure transport (TLS)
- Provide centralized authorization
- Provide cross-provider consensus enforcement
- Make NUVL or the auditor authoritative decision engines

This demo demonstrates authority separation, not enterprise deployment hardening.

---

## Architectural Roles

### NUVL (Stateless Intermediary)

NUVL:

- Accepts opaque request bytes
- Computes request representation
- Applies deterministic binding
- Constructs artifact
- Fans out to all providers
- Returns constant 204 and disengages

NUVL does not:

- Hold provider secrets
- Inspect provider scores
- Validate provider signatures
- Evaluate quorum
- Store execution state

---

### Providers (Execution Authority)

Each provider independently:

- Validates mechanical binding
- Computes provider-controlled adaptive score
- Applies domain-specific threshold table
- Determines `initiated = True | False`
- Optionally generates provider-boundary signatures
- Reports outcome to auditor

One configured provider flips its initiation bit deterministically after a threshold to simulate Byzantine behavior.

Execution authority never leaves provider boundaries.

---

### Auditor (Observational Quorum)

The auditor:

- Receives provider outcome signals
- Aggregates 2-of-3 quorum on `provider_initiated`
- Tracks per-domain statistics
- Does not initiate execution
- Does not inform NUVL
- Does not override provider authority

Quorum is observational, not authoritative.

---

## Evaluation Model

Provider decision logic combines:

- Binding integrity validation
- Provider-only adaptive scoring
- Domain-scoped threshold tables

Domains influence provider policy but remain opaque to NUVL.

The intermediary remains blind to provider evaluation semantics.

---

## Failure & Adversarial Controls

### Intermediary (Transport Layer)

- Probabilistic forward drop
- Probabilistic forward delay
- Bounded forward queue

NUVL always returns constant HTTP 204.

---

### Provider Layer

- Adaptive scoring per provider
- Domain threshold configuration
- Deterministic Byzantine provider flip

This tests quorum resilience without centralizing authority.

---

## Running the Demo

Run:

    python3 multi-provider-initiation.py

Default services:

- NUVL: 127.0.0.1:8080
- Auditor: 127.0.0.1:7070
- Provider A: 127.0.0.1:9090
- Provider B: 127.0.0.1:9091
- Provider C: 127.0.0.1:9092

---

## Tunable Parameters

Requester:

- TOTAL_REQUESTS
- CONCURRENCY
- RANDOM_SEED

Intermediary Chaos:

- P_DROP_FORWARD
- P_DELAY_FORWARD
- DELAY_MS_RANGE

Provider Adversarial:

- BYZANTINE_PROVIDER_ID
- BYZANTINE_AT

Auditor:

- QUORUM_K

Provider Policy:

- DOMAIN_THRESHOLDS

---

## Output

The demo prints:

- Requester transport timing
- Provider initiation counts
- Binding failure counts
- Quorum successes and failures
- Per-domain aggregation statistics

All outputs are observational and do not affect execution authority.

---

## Architectural Invariants

Across all execution paths:

- NUVL holds no provider secrets.
- NUVL does not evaluate provider logic.
- Providers do not consult each other.
- Auditor does not initiate execution.
- Byzantine behavior does not migrate authority.
- Quorum does not centralize execution.
- Execution authority remains exclusively scoped to provider-controlled systems.

---

## License

This demo incorporates Apache-2.0 licensed components derived from the NUVL core.

Except for Apache-2.0 licensed NUVL core components, all orchestration, quorum logic, adversarial simulation, adaptive evaluation, and integration code contained in this file is proprietary.

Commercial deployment, redistribution, or integration of proprietary portions requires a separate written license agreement.
