# Demo — Two-Region Quorum Audit with Byzantine Drift  
## Deterministic Replay • Region Failover • Dual Hub Mesh • Provider-Controlled Initiation

---

## Overview

This demo composes **two regions** (R1 and R2), each with:

- a neutral NUVL front (`/nuvl`)
- a **two-hub mesh** (Hub A ↔ Hub B) that performs mechanical relay only
- three providers (A/B/C) that remain the only execution authorities

Requests are deterministically generated and sent to **Region 1** until `FAILOVER_AT`, then switched to **Region 2**.  
Providers evaluate artifacts independently and report **outcome signals** back to hub `/outcome` endpoints for **observability only**.

A deterministic **Byzantine drift** is injected: after a computed index, **Provider_B flips ~50% of reported outcomes** while preserving “real” initiation logic internally.

---

## Design Goals

This demo is designed to:

- Demonstrate **region failover** under a constant requester interface (HTTP 204 path)
- Demonstrate a **two-hub mesh** per region (peer relay) without hub-side authority
- Demonstrate **provider-controlled initiation** with hub-produced mechanical bindings
- Demonstrate **quorum audit aggregation (2-of-3)** from provider-reported outcomes
- Demonstrate **adversarial replica drift** (provider reports diverge) under replayable conditions
- Provide a compact benchmark summary including per-domain quorum results

---

## Non-Goals

This demo does not:

- Provide production routing, retries, persistence, or durable queues
- Provide identity, authentication, or credential validation
- Provide secure transport (TLS), mTLS, or deployment hardening
- Make hubs authoritative policy engines, adjudicators, or consensus participants
- Treat quorum outcomes as authorization inputs

This demo constrains authority location. It does not replace provider security controls.

---

## Architectural Roles

### NUVL Fronts (Neutral)

Each region exposes a NUVL endpoint:

- Accepts opaque request bytes at `/nuvl`
- Computes `request_repr = SHA-256(request_bytes)`
- Computes `binding = nuvl_bind(request_repr, verification_context, domain)`
- Emits an artifact to its region hub submit endpoint
- Returns constant HTTP 204 to requester (no outcome semantics)

NUVL does not:
- hold provider secrets
- decide initiation
- interpret returned outcomes

---

### Hubs (Mechanical Relay Only)

Each region has two hubs in a peer mesh:

- Hub A ↔ Hub B relay artifacts to each other via `/submit`
- Each hub fans out artifacts to configured region providers
- Each hub exposes `/outcome` to receive provider outcome signals

Hubs do not:
- evaluate provider thresholds
- validate signatures beyond basic parsing
- treat outcomes as authorization input
- initiate execution

Outcome intake exists for **observability only** (auditor aggregation).

---

### Providers (Execution Authority)

Each provider independently evaluates:

- binding correctness (`binding_ok`)
- a deterministic score (stand-in for provider inference)
- per-domain thresholds

Providers are the only components that can “initiate” (in demo terms).  
Providers also produce provider-boundary artifacts (HMAC) internally, but the demo keeps those light.

#### Byzantine Drift Injection

- After `byz_start`, `PROVIDER_B` flips ~50% of **reported** outcomes (`initiated_reported`)
- The “real” initiation logic remains based on binding + score + threshold
- This models a drifting / adversarial replica producing inconsistent signals

---

## Deterministic Replay Model

The run is replayable:

- Requests are generated deterministically by sequence (`seq`)
- Domain selection is deterministic: `domain = DOMAINS[seq % len(DOMAINS)]`
- Payload structure is deterministic (`make_payload`)
- Byzantine start index is deterministic given `RUN_SEED`, and is chosen to occur **after failover** when possible

This makes drift events easier to reproduce and compare across runs.

---

## Failover Model

The requester sends:

- to Region 1 NUVL endpoint for `seq < FAILOVER_AT`
- to Region 2 NUVL endpoint for `seq >= FAILOVER_AT`

Failover is client-side selection of region entrypoint; downstream topology remains provider-controlled and hub-neutral.

---

## Running the Demo

Run:

    python3 two-region-quorum-byzantize-drift.py

Key tunables (environment variables):

- `TOTAL_REQUESTS` (default: 100)
- `FAILOVER_AT` (default: TOTAL_REQUESTS//2)
- `QUORUM_THRESHOLD` (default: 2)
- `EXPECTED_CONTEXT` (default: CTX_ALPHA)

Optional drift controls:

- `BYZANTINE_PROVIDER` (if set, overrides which provider drifts)
- `BYZANTINE_AT` (if set, overrides drift start index)
- `RANDOM_SEED` (optional; affects only helper choices when used)

---

## Reference Endpoints and Ports

Two regions, same shape:

**Region 1**
- NUVL: `/nuvl` on `NUVL_R1_PORT`
- Hub A: `/submit`, `/outcome` on `HUB_R1_A_PORT`
- Hub B: `/submit`, `/outcome` on `HUB_R1_B_PORT`
- Providers: `/ingest` on `PROV_R1_A_PORT`, `PROV_R1_B_PORT`, `PROV_R1_C_PORT`

**Region 2**
- NUVL: `/nuvl` on `NUVL_R2_PORT`
- Hub A: `/submit`, `/outcome` on `HUB_R2_A_PORT`
- Hub B: `/submit`, `/outcome` on `HUB_R2_B_PORT`
- Providers: `/ingest` on `PROV_R2_A_PORT`, `PROV_R2_B_PORT`, `PROV_R2_C_PORT`

---

## Output (Compact Summary)

At completion, the demo prints:

- request counts and failover point
- computed byzantine start index (`byz_start`)
- requester HTTP success/error counts (measures the 204 path)
- total time and average per request
- quorum audit totals (success/fail)
- per-domain success/fail counts

These are observability metrics, not authorization outputs.

---

## Architectural Invariants

Across all execution paths:

- NUVL fronts perform representation + binding and forward only.
- Hubs are conveyance-only intermediaries (fanout + relay + outcome intake).
- Providers remain the only execution authorities.
- Quorum aggregation is observational and does not confer authority.
- Drift in reported outcomes is detectable at the audit layer without moving authority into hubs.

---

## License

This demo incorporates components derived from the NUVL core, which is licensed under the Apache License, Version 2.0.

Except for Apache-2.0 licensed NUVL core components, all additional orchestration, replay harness logic, regional topology, hub mesh relay, quorum auditing, byzantine drift injection, and integration logic contained in this file is proprietary.

Commercial deployment, redistribution, or integration of proprietary portions requires a separate written license agreement.
