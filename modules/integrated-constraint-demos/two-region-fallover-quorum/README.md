# Two-Region / Two-NUVL / Two-Mesh — Failover + Deterministic Byzantine Quorum

## Overview

This demo composes multiple architectural constraint modules into a single runnable reference:

Requester → NUVL_R1 / NUVL_R2 → Hub Mesh (R1 / R2) → Provider Fan-Out → Non-Authoritative Quorum Auditor

The system simulates:

- Two-region NUVL fronts with requester-driven failover
- Two-hub mechanical relay mesh per region
- Multi-domain request routing surfaces (opaque to intermediaries)
- Provider-side adaptive scoring + domain thresholds
- Deterministic Byzantine drift introduced mid-run
- 2-of-3 quorum aggregation on provider initiation signals
- Domain-scoped quorum results (success/fail by domain)

Across all flows:

- NUVL performs representation + binding + forwarding only.
- Hubs perform conveyance + fan-out + relay only.
- Providers remain the only execution authority.
- The auditor aggregates signals but does not initiate execution.

Failover and adversarial behavior are introduced during the run to demonstrate that distributed transport conditions do not migrate authorization semantics into intermediaries.

---

## Design Goals

This demo is designed to:

- Demonstrate region failover across two independent NUVL fronts.
- Demonstrate mechanical two-hub relay mesh per region.
- Demonstrate multi-domain artifact formation and forwarding.
- Demonstrate provider-side binding verification and initiation decisions.
- Demonstrate deterministic Byzantine drift after failover.
- Demonstrate non-authoritative 2-of-3 quorum aggregation.
- Provide domain-scoped quorum summaries without centralizing authority.

---

## Non-Goals

This demo does not:

- Provide secure transport (TLS) or production authentication.
- Provide durable storage, replay protection, or persistence guarantees.
- Provide distributed consensus, global ordering, or settlement semantics.
- Provide identity or credential infrastructure.
- Allow NUVL, hubs, or the auditor to initiate execution.
- Centralize authorization logic into intermediaries or aggregators.

This is an authority-location demonstration, not a hardened deployment reference.

---

## Architectural Roles

### NUVL Fronts (Region 1 and Region 2)

Two independent NUVL instances accept opaque requests.

Each NUVL:

- Computes `request_repr = SHA-256(request_bytes)`
- Reads opaque headers:
  - `X-Verification-Context`
  - `X-Domain`
  - `X-Seq`
- Computes a deterministic binding:
  - `binding = nuvl_bind(request_repr, verification_context, domain)`
- Forwards the artifact to its region hub
- Returns constant HTTP 204
- Does not observe provider outcomes

Failover occurs at `FAILOVER_AT`, shifting requester traffic from Region 1 to Region 2.

NUVL does not evaluate provider decisions.

---

### Hubs (Conveyance + Relay Only)

Each region runs two hubs (a local mesh):

- HUB_R?_A and HUB_R?_B

Each hub:

- Accepts artifacts from its local NUVL or peer hub
- Mechanically fans out to its region’s providers
- Mechanically relays artifacts to its peer hub
- Accepts provider outcome posts at `/outcome`
- Does not evaluate policy or initiation state

Hubs remain transport and conveyance components only.

---

### Providers (Authoritative Decision Boundaries)

Each region runs three providers:

- PROVIDER_A, PROVIDER_B, PROVIDER_C

Each provider:

- Verifies mechanical binding correctness (provider checks intermediary binding)
- Computes a provider-controlled adaptive score (seeded / provider-only)
- Applies domain-scoped thresholds
- Determines `initiated = True | False` within the provider boundary
- Emits an outcome signal to the hub outcome endpoint

One provider exhibits deterministic Byzantine drift:

- PROVIDER_B begins drifting after a deterministic index (`byz_start`)
- After drift begins, reported outcomes may invert on a deterministic schedule

Execution authority remains provider-scoped.

---

### Auditor (Non-Authoritative Quorum Aggregation)

The auditor:

- Observes provider outcome signals via hub outcome endpoints
- Aggregates 2-of-3 quorum on `initiated`
- Tracks:
  - Quorum successes / failures
  - Quorum results by domain (success/fail counts)

The auditor does not:

- Initiate execution
- Override provider authority
- Feed decisions back into NUVL or hubs

Aggregation is observational only.

---

## Domain-Scoped Behavior

Requests include one of:

- `payments`
- `storage`
- `identity`
- `compute`

Providers apply domain-specific thresholds.

Domains remain opaque to NUVL and hubs (used only as mechanical fields and provider inputs).

---

## Failover & Adversarial Injection

### Region Failover

At `FAILOVER_AT`:

- Requests before threshold → NUVL_R1 → Hub Mesh R1 → Providers R1
- Requests after threshold → NUVL_R2 → Hub Mesh R2 → Providers R2

Failover is requester-driven.

### Deterministic Byzantine Drift

A deterministic start point is computed:

- `byz_start = deterministic_byzantine_start(TOTAL_REQUESTS, FAILOVER_AT)`

After `byz_start`:

- PROVIDER_B begins drifting (reported initiation may flip on a deterministic pattern)

This tests quorum robustness without collapsing authority into aggregation layers.

---

## Running the Demo

Run:

    python3 two-region-fallover-quorum.py

Default ports:

Region 1:
- NUVL_R1: 8010
- HUB_R1_A: 8110
- HUB_R1_B: 8111
- Providers: 8210 / 8211 / 8212

Region 2:
- NUVL_R2: 8020
- HUB_R2_A: 8120
- HUB_R2_B: 8121
- Providers: 8220 / 8221 / 8222

Tunables at the top of the file include:

- TOTAL_REQUESTS
- FAILOVER_AT
- POST_WORKERS
- POST_QUEUE_MAX
- HTTP_TIMEOUT_S

---

## Output Summary

At completion, the demo prints:

- Total requests
- Failover index (Region 1 → Region 2)
- Byzantine start index (Provider_B drift begins)
- HTTP ok / error counts
- Total elapsed time + average per request
- Quorum successes / failures
- Quorum results by domain (success/fail counts)

All metrics are observational.

No execution state migrates into transport or aggregation layers.

---

## Architectural Invariants

Across all execution paths:

- NUVL holds no provider keys.
- NUVL returns constant HTTP 204.
- Hubs route mechanically and do not interpret semantics.
- Providers independently determine initiation.
- Quorum aggregation is non-authoritative observation.
- Failover changes transport topology, not authority location.
- Byzantine drift does not centralize control.
- Quorum does not become an execution authority.

Execution authority remains exclusively scoped to provider-controlled systems.

---

## License

This demo incorporates Apache-2.0 licensed components derived from the NUVL core.

Except for Apache-2.0 licensed NUVL core components, all orchestration, failover logic, quorum aggregation, adversarial simulation, disagreement scoring, and integration code contained in this file is proprietary.

Commercial deployment, redistribution, or integration of proprietary portions requires a separate written license agreement.
