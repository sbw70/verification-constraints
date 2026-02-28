# Demo — Multi-Hub Multi-Domain Mesh
## Dual NUVL Fronts • Multi-Hub Relay • Provider Signatures • Regional Fallover • 2-of-3 Aggregation

---

## Overview

This integration demo composes two region-scoped NUVL fronts with a dual-hub relay mesh, three independent provider-controlled execution boundaries, and a non-authoritative quorum auditor.

Two NUVL instances (Region A and Region B) accept opaque requester traffic and forward **representations only** to their local hub. Hubs mechanically fan out artifacts to providers and relay artifacts to the peer hub. Providers independently evaluate artifacts and report signed outcomes to an auditor. The auditor aggregates 2-of-3 outcomes per request representation.

Across the demo:

- NUVL binds/forwards only and returns constant HTTP 204.
- Hubs route/relay mechanically (no authorization semantics).
- Providers exclusively determine initiation.
- Auditor aggregates outcomes observationally (non-executing).

---

## Design Goals

This demo is designed to:

- Demonstrate region failover (requester switches from Region A to Region B mid-run)
- Demonstrate multi-hub relay without centralized authority
- Demonstrate provider-only initiation under domain-scoped thresholds
- Demonstrate non-authoritative 2-of-3 quorum aggregation over provider-signed outcomes
- Demonstrate deterministic adversarial behavior via a Byzantine provider flip point
- Keep console output compact while still providing meaningful summary metrics

---

## Non-Goals

This demo does not:

- Provide production-grade failover, retries, persistence, or durable queues
- Provide secure transport (TLS) or deployment hardening
- Provide identity systems or credential validation
- Provide distributed consensus or global ordering guarantees
- Make hubs, NUVL, or the auditor authoritative policy engines

This demo constrains authority location. It is not a secure deployment baseline.

---

## Architectural Roles

### Region NUVL Fronts (Bind + Forward Only)

Two NUVL instances run concurrently:

- Region A: listens on `NUVL_A_PORT`
- Region B: listens on `NUVL_B_PORT`

Each NUVL:

- Accepts opaque request bytes
- Computes `request_repr = SHA-256(request_bytes)`
- Reads opaque headers:
  - `X-Verification-Context`
  - `X-Domain`
- Forwards `{request_repr, verification_context, domain}` to its local hub
- Returns constant HTTP 204 and disengages

NUVL does not hold provider keys, does not evaluate provider decisions, and does not collect outcomes.

---

### Hubs (Mechanical Fanout + Peer Relay)

Two hubs run concurrently:

- Hub A: listens on `HUB_A_PORT`
- Hub B: listens on `HUB_B_PORT`

Each hub:

- Receives JSON artifacts from its local NUVL (or from peer hub)
- Fans out artifacts mechanically to all providers
- Relays artifacts mechanically to the peer hub
- Tracks relay counts for summary output

Hubs do not evaluate authorization semantics and do not initiate execution.

---

### Providers (Execution Authority + Signatures)

Three providers evaluate artifacts independently.

Each provider:

- Computes a provider-controlled score based on provider secret material
- Applies a domain-scoped threshold table
- Determines `initiated = True | False`
- Emits a signed outcome to the auditor:
  - `{provider, request_repr, domain, initiated, signature}`

One provider (PROVIDER_C) flips its `initiated` bit after a randomized threshold to simulate Byzantine behavior.

Execution authority remains exclusively provider-scoped.

---

### Auditor (Non-Authoritative Quorum)

The auditor:

- Receives provider outcome messages
- Verifies provider signatures using provider keys
- Aggregates outcomes per request representation
- Applies a 2-of-3 quorum rule (`QUORUM_THRESHOLD`)
- Tracks summary counters:
  - signed outcomes
  - bad signatures rejected
  - quorum successes / failures

The auditor does not initiate execution and does not feed decisions back into NUVL or hubs.

---

## Failover and Adversarial Controls

### Region Failover (Requester)

During the run, the requester switches region ports at a randomized index:

- Requests before `failover_at` go to Region A NUVL
- Requests after `failover_at` go to Region B NUVL

Failover is requester-visible, not mediated by NUVL/hubs.

### Byzantine Provider

A randomized flip point activates adversarial behavior:

- PROVIDER_C flips `initiated` after `byzantine_flip_at`

This models a faulty or adversarial provider without collapsing authority into the auditor.

---

## Domain-Scoped Behavior

Each request includes a domain value selected from:

- `payments`
- `identity`
- `storage`

Providers apply domain thresholds independently.

Domains are treated as opaque by NUVL and hubs.

---

## Running the Demo

Run:

    python3 multi-hub-domain-mesh.py

Default ports:

- Region A NUVL: 127.0.0.1:8000  
- Region B NUVL: 127.0.0.1:8001  
- Hub A: 127.0.0.1:8100  
- Hub B: 127.0.0.1:8101  
- Auditor: 127.0.0.1:8200  
- Providers: 127.0.0.1:9001 / 9002 / 9003  

---

## Tunable Parameters

Run controls:

- `TOTAL_REQUESTS`
- `RANDOM_SEED`

Randomized during run (bounded):

- `FAILOVER_MIN` / `FAILOVER_MAX`
- `BYZANTINE_MIN` / `BYZANTINE_MAX`

Quorum policy:

- `QUORUM_THRESHOLD` (2-of-3)

Provider policy:

- `PROVIDER_THRESHOLDS` (domain-scoped)

Transport tuning:

- `MAX_WORKERS`
- `HTTP_TIMEOUT_S`

---

## Output (Compact Summary)

At completion, the demo prints:

- Total requests and failover index
- Byzantine flip index
- Requester HTTP ok/error counts
- Timing window (requester-side)
- Hub relay counts
- Provider initiation totals and per-domain initiation totals
- Auditor results:
  - signed outcomes received
  - bad signatures rejected
  - quorum successes / failures

All outputs are observational and do not alter initiation authority.

---

## Architectural Invariants

Across all execution paths:

- NUVL holds no provider keys and returns constant HTTP 204.
- Hubs route and relay mechanically; they do not evaluate semantics.
- Providers independently determine initiation inside provider boundaries.
- Auditor aggregates outcomes but does not initiate execution.
- Failover and Byzantine behavior do not migrate authority into intermediaries.
- Quorum aggregation does not centralize execution control.

---

## License

This demo incorporates components derived from the NUVL core, which is licensed under the Apache License, Version 2.0.

Except for Apache-2.0 licensed NUVL core components, all additional orchestration, failover, quorum, adversarial, and integration logic contained in this file is proprietary.

Commercial deployment, redistribution, or integration of proprietary portions requires a separate written license agreement.
