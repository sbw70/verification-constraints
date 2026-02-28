# Demo — Region-Failover Quorum Under Adversarial Replica Drift
## Dual NUVL Fronts • Hub Fan-Out • Provider-Signed Outcomes • Non-Authoritative Quorum

---

## Overview

This demo composes **region failover** with **multi-provider fanout** and a **non-authoritative quorum auditor** under the NUVL constraint model.

Flow:

Requester → NUVL_A / NUVL_B → HUB_A / HUB_B → Provider Fan-Out → Auditor (observer-only)

The system simulates:

- Two region NUVL fronts (A/B) with a deterministic failover point
- Hub fan-out to three independent providers
- Provider-controlled initiation using a deterministic scoring stand-in
- A randomized Byzantine replica that flips its decision after a chosen index
- 2-of-3 quorum aggregation performed by a non-authoritative auditor

Across all flows:

- NUVL performs representation + forwarding only.
- Hubs perform conveyance + fan-out only.
- Providers remain the only execution authorities.
- The auditor aggregates signals but does not initiate execution.

Failover and adversarial behavior are introduced to demonstrate that transport conditions and disagreement do not migrate authorization semantics into intermediaries.

---

## Design Goals

This demo is designed to:

- Demonstrate requester-driven region failover across two NUVL fronts.
- Demonstrate hub fan-out to multiple providers without hub authority.
- Demonstrate provider-only initiation decisions using provider-controlled logic.
- Demonstrate provider-signed outcome signals.
- Demonstrate non-authoritative 2-of-3 quorum aggregation.
- Demonstrate randomized Byzantine drift without centralizing control.

---

## Non-Goals

This demo does not:

- Provide production-grade transport, retries, persistence, or durability.
- Provide secure transport (TLS) or hardened deployment controls.
- Provide identity, authentication, or credential validation infrastructure.
- Provide distributed consensus, global ordering, or state replication.
- Allow NUVL, hubs, or the auditor to initiate execution.

This is an authority-location demonstration, not a hardened deployment reference.

---

## Architectural Roles

### NUVL Fronts (Region A and Region B)

Two independent NUVL instances accept opaque requests.

Each NUVL:

- Computes `request_repr = SHA-256(request_bytes)`
- Reads requester headers:
  - `X-Verification-Context`
  - `X-Domain`
- Forwards `request_repr` + opaque headers to its region hub
- Returns constant HTTP 204
- Does not observe provider outcomes

Failover is requester-driven: requests before `FAILOVER_AT` route to Region A; after `FAILOVER_AT` route to Region B.

NUVL does not evaluate provider decisions.

---

### Hubs (Conveyance + Fan-Out Only)

Each hub:

- Accepts forwarded artifacts from its local NUVL
- Fans out the artifact to all providers (mechanical relay)
- Returns constant HTTP 204

Hubs do not:

- Evaluate domain policy
- Evaluate verification context
- Hold provider secrets
- Initiate execution
- Aggregate outcomes

---

### Providers (Authoritative Decision Boundaries)

Each provider:

- Computes a provider-controlled score:

  `score = HMAC(provider_key, pid|domain|rr|ctx)`

- Applies a domain-scoped threshold (`payments`, `identity`, `storage`)
- Determines `initiated = True | False`
- Emits a signed outcome to the auditor:

  `signature = HMAC(provider_key, request_repr)`

A randomized provider is selected as Byzantine at runtime:

- After `ACTIVE_BYZ_AT`, that provider flips its `initiated` bit.

This simulates adversarial or faulty drift within one replica without moving authority into the auditor or hubs.

---

### Auditor (Non-Authoritative Quorum Aggregation)

The auditor:

- Receives provider outcomes at `/audit`
- Verifies provider signatures (provider-key verification)
- Aggregates 2-of-3 quorum per `request_repr`
- Tracks quorum successes and failures

The auditor does not:

- Initiate execution
- Override providers
- Feed outcomes back into NUVL or hubs

Aggregation is observational only.

---

## Domain-Scoped Behavior

Requests carry a domain:

- `payments`
- `identity`
- `storage`

Providers apply thresholds per domain.  
Domains remain opaque to NUVL and hubs (transport metadata only).

---

## Failover & Adversarial Drift

### Region Failover

At `FAILOVER_AT`:

- Requests before threshold → NUVL_A → HUB_A
- Requests after threshold → NUVL_B → HUB_B

Failover is driven by the requester’s routing selection and does not change authority location.

### Byzantine Drift

At runtime:

- `ACTIVE_BYZ_PROVIDER` is chosen randomly from the providers
- `ACTIVE_BYZ_AT` is chosen randomly in the later portion of the run
- After that index, the selected provider flips its `initiated` decision

This tests disagreement tolerance under quorum without turning aggregation into an execution authority.

---

## Running the Demo

Run:

    python3 region-failover-byzantine-quorum.py

Defaults:

- `TOTAL_REQUESTS = 750`
- `FAILOVER_AT = 375`
- `QUORUM_THRESHOLD = 2`
- `RANDOM_SEED = 1337`

Ports:

- NUVL_A: 8000
- NUVL_B: 8001
- HUB_A: 8100
- HUB_B: 8101
- Auditor: 8200
- Providers: 9001 / 9002 / 9003

---

## Output (Compact Summary)

At completion, the demo prints:

- Total requests
- Failover index (Region A → Region B)
- Byzantine provider and flip index
- Total elapsed time and average per request (requester send path)
- Provider initiation totals
- Quorum successes and failures

All printed metrics are observational.

No execution state migrates into NUVL, hubs, or the auditor.

---

## Architectural Invariants

Across all execution paths:

- NUVL holds no provider keys and returns constant HTTP 204.
- Hubs relay mechanically and do not interpret semantics.
- Providers independently determine initiation.
- Provider outcomes are signed inside the provider boundary.
- Auditor aggregates but does not initiate execution.
- Failover does not change authority location.
- Byzantine drift does not centralize control.
- Quorum aggregation does not become an execution authority.

Execution authority remains exclusively scoped to provider-controlled systems.

---

## License

This demo incorporates components derived from the NUVL core, which is licensed under the Apache License, Version 2.0.

Except for Apache-2.0 licensed NUVL core components, all additional orchestration, region failover logic, hub fan-out wiring, quorum aggregation, Byzantine drift simulation, and integration code contained in this file is proprietary.

Commercial deployment, redistribution, or integration of proprietary portions requires a separate written license agreement.
