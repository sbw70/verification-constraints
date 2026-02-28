# Multi-Hub / Multi-Domain Audit — Failover + Byzantine Quorum

## Overview

This demo composes multiple architectural constraint modules into a single runnable reference:

Requester → NUVL_A / NUVL_B → HUB_A / HUB_B → Provider Fan-Out → Non-Authoritative Auditor

The system simulates:

- Dual-region NUVL fronts
- Multi-hub mechanical relay
- Domain-scoped provider policies
- Deterministic Byzantine behavior
- 2-of-3 quorum aggregation
- Disagreement (“suspect”) scoring

Across all flows:

- NUVL performs representation + forwarding only.
- Hubs perform conveyance + fan-out only.
- Providers remain the only execution authority.
- The auditor aggregates signals but does not initiate execution.

Failover and adversarial behavior are introduced mid-run to demonstrate that distributed transport conditions do not migrate authorization semantics into intermediaries.

---

## Design Goals

This demo is designed to:

- Demonstrate region failover across two NUVL fronts.
- Demonstrate mechanical multi-hub conveyance.
- Demonstrate domain-scoped provider threshold policies.
- Demonstrate provider-signed outcome signals.
- Demonstrate non-authoritative quorum aggregation.
- Demonstrate deterministic Byzantine injection.
- Provide observable disagreement metrics without centralizing authority.

---

## Non-Goals

This demo does not:

- Provide production-grade persistence or durability.
- Provide secure transport (TLS).
- Provide identity or credential infrastructure.
- Provide distributed consensus or global ordering.
- Allow hubs, NUVL, or the auditor to initiate execution.
- Centralize authorization logic.

This is an authority-location demonstration, not a hardened deployment reference.

---

## Architectural Roles

### NUVL Fronts (Region A and Region B)

Two independent NUVL instances accept opaque requests.

Each NUVL:

- Computes `request_repr = SHA-256(request_bytes)`
- Reads opaque headers:
  - `X-Verification-Context`
  - `X-Domain`
- Forwards representation + headers to its region hub
- Returns constant HTTP 204
- Does not observe provider outcomes

Failover occurs at `FAILOVER_AT`, shifting requester traffic from Region A to Region B.

NUVL does not evaluate provider decisions.

---

### Hubs (Conveyance Only)

HUB_A and HUB_B:

- Accept artifacts from their local NUVL
- Mechanically fan out to all providers
- Track relay counts for summary reporting
- Do not evaluate policy or initiation state

Hubs remain transport components only.

---

### Providers (Authoritative Decision Boundaries)

Each provider:

- Computes a provider-controlled adaptive score
- Applies domain-scoped thresholds
- Determines `initiated = True | False`
- Emits a signed outcome to the auditor

One provider is selected as Byzantine:

- After `ACTIVE_BYZANTINE_AT`, it flips its decision bit
- The flip simulates adversarial or faulty behavior

Execution authority remains provider-scoped.

---

### Auditor (Non-Authoritative Aggregation)

The auditor:

- Verifies provider signatures
- Aggregates 2-of-3 quorum on `initiated`
- Tracks:
  - Quorum successes / failures
  - Provider disagreement rates
- Computes “suspect scoring” based on vote divergence

The auditor does not:

- Initiate execution
- Override provider authority
- Feed decisions back into NUVL or hubs

Aggregation is observational only.

---

## Domain-Scoped Behavior

Requests include one of:

- `payments`
- `identity`
- `storage`

Providers apply threshold logic per domain.

Domains are opaque to NUVL and hubs.

---

## Failover & Adversarial Injection

### Region Failover

At `FAILOVER_AT`:

- Requests before threshold → NUVL_A
- Requests after threshold → NUVL_B

Failover is requester-driven.

### Byzantine Injection

A provider is selected at runtime.

After `ACTIVE_BYZANTINE_AT`:

- That provider inverts its `initiated` decision.

This tests quorum robustness without collapsing authority into aggregation layers.

---

## Running the Demo

Run:

    python3 two-region-failover-quorum-drift.py

Default ports:

- NUVL_A: 8000
- NUVL_B: 8001
- HUB_A: 8100
- HUB_B: 8101
- Auditor: 8200
- Providers: 9001 / 9002 / 9003

Environment variables allow override of:

- TOTAL_REQUESTS
- FAILOVER_AT
- QUORUM_THRESHOLD
- RANDOM_SEED
- BYZANTINE_PROVIDER
- BYZANTINE_AT
- WORKER_COUNT
- POST_QUEUE_MAX

---

## Output Summary

At completion, the demo prints:

- Total requests
- Failover index
- Byzantine provider + flip index
- Total elapsed time + average per request
- Hub relay counts
- Provider initiation totals
- Provider initiation by domain
- Quorum successes / failures
- Provider disagreement rate (“suspect scoring”)

All metrics are observational.

No execution state migrates into transport or aggregation layers.

---

## Architectural Invariants

Across all execution paths:

- NUVL holds no provider keys.
- NUVL returns constant HTTP 204.
- Hubs route mechanically and do not interpret semantics.
- Providers independently determine initiation.
- Auditor aggregates but does not initiate execution.
- Failover does not change authority location.
- Byzantine behavior does not centralize control.
- Quorum aggregation does not become an execution authority.

Execution authority remains exclusively scoped to provider-controlled systems.

---

## License

This demo incorporates Apache-2.0 licensed components derived from the NUVL core.

Except for Apache-2.0 licensed NUVL core components, all orchestration, failover logic, quorum aggregation, adversarial simulation, disagreement scoring, and integration code contained in this file is proprietary.

Commercial deployment, redistribution, or integration of proprietary portions requires a separate written license agreement.
