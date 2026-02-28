# Demo- Multi-Provider Initiation  
## Multi-Provider • Adaptive Thresholds • Deterministic Byzantine • 2-of-3 Quorum

---

## Overview

This integration demo composes the NUVL core with:

- Three independent provider-controlled execution boundaries  
- Provider-side adaptive decision logic (domain-scoped thresholds)  
- Deterministic Byzantine behavior (one provider flips outcomes after a configured threshold)  
- A non-authoritative quorum auditor (2-of-3 rule)  
- Transport-level chaos (drop + delay) at the intermediary layer  

NUVL remains strictly mechanical:

- Derives a non-reversible request representation (SHA-256 in this reference)
- Computes deterministic binding
- Constructs verification artifacts
- Fans out artifacts to multiple providers
- Returns constant HTTP 204 and disengages

NUVL does not evaluate provider policy, interpret execution state, or aggregate quorum.

All initiation authority remains inside provider boundaries.

---

## Architectural Roles

### NUVL (Stateless Intermediary)

- Accepts opaque request bytes
- Derives request representation
- Applies deterministic binding transform
- Constructs artifact
- Fans out to all providers
- Returns constant HTTP 204

NUVL does not:

- Inspect provider outcomes
- Validate quorum
- Store execution state
- Hold provider secrets

---

### Providers (Execution Authority)

Each provider independently:

- Verifies binding integrity
- Computes provider-controlled adaptive score
- Applies domain-specific threshold table
- Determines initiated = True or False
- Signs boundary signals internally
- Reports outcome to auditor

One designated provider flips its initiation signal deterministically after a configured request count.

Execution authority never leaves the provider boundary.

---

### Auditor (Non-Authoritative)

The auditor:

- Receives provider outcome messages
- Aggregates 2-of-3 quorum on provider_initiated
- Tracks statistics per domain
- Does not initiate execution
- Does not inform NUVL
- Does not override providers

Quorum is observational, not authoritative.

---

## Failure & Adversarial Controls

### Transport-Level (NUVL)

- Probabilistic forward drop (providers never see artifact)
- Probabilistic forward delay (jitter)
- Bounded forward queue to prevent thread explosion

NUVL still returns constant 204 in all cases.

---

### Provider-Side

- Domain threshold tables control acceptance rates
- Provider-only HMAC seeds shape adaptive scoring
- Deterministic Byzantine provider flips decision after threshold

This tests quorum resilience without centralizing authority.

---

## Domain-Scoped Policy

Requests carry an X-Domain header:

- payments
- identity
- storage
- compute

Providers apply domain-specific thresholds independently.

NUVL treats domain as opaque.

---

## Running the Demo

Run:

    python3 multi-provider-initiation.py

Default ports:

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
- PROGRESS_EVERY  
- RANDOM_SEED  

NUVL Chaos:

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

## Architectural Invariants

Across all execution paths:

- NUVL holds no provider keys.
- NUVL does not validate provider signatures.
- Providers do not consult each other.
- Auditor does not initiate execution.
- Transport chaos does not alter authority boundaries.
- Execution authority remains exclusively scoped to provider-controlled systems.

---

## License

This demo incorporates Apache-2.0 licensed components derived from the NUVL core.

Except for Apache-2.0 licensed NUVL core components, all orchestration, failover, quorum, adversarial, and integration logic contained in this file is proprietary.

Commercial deployment, redistribution, or integration of proprietary portions requires a separate written license agreement.
