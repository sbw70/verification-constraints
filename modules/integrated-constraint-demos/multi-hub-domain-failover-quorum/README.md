# Demo — Multi-Hub Multi-Domain: Failover + Quorum
## Mechanical Relay • Provider-Controlled Initiation • Byzantine Injection • Non-Authoritative Aggregation

---

## Overview

This demo composes two NUVL fronts, two hubs, three providers, and a non-authoritative auditor into a failover + quorum simulation under the NUVL constraint model.

Flow:

Requester → NUVL_A / NUVL_B → HUB_A / HUB_B → Providers → Auditor

The system simulates:

- Requester-driven region failover (NUVL_A → NUVL_B)
- Multi-hub conveyance (mechanical fanout only)
- Multi-domain provider evaluation (`payments`, `identity`, `storage`)
- Provider-only initiation authority
- Signed provider outcome signals
- 2-of-3 quorum aggregation (observer-only)
- Byzantine behavior injection at a randomized index
- Provider “suspect scoring” based on quorum disagreement

Across all paths:

- NUVL performs representation + forwarding only.
- Hubs perform conveyance only.
- Providers remain the sole execution authority.
- The auditor aggregates but does not authorize.

---

## Design Goals

This demo is designed to:

- Demonstrate requester-driven failover between two NUVL fronts.
- Demonstrate multi-hub mechanical routing without hub authority.
- Demonstrate multi-provider independent initiation decisions.
- Demonstrate domain-scoped provider thresholds.
- Demonstrate provider-signed outcome reporting.
- Demonstrate non-authoritative 2-of-3 quorum aggregation.
- Demonstrate adversarial (Byzantine) decision flipping.
- Provide disagreement-based suspect scoring for observability.

---

## Non-Goals

This demo does not:

- Provide production routing, retries, persistence, or durable queues.
- Provide identity, authentication, or credential validation.
- Provide secure transport (TLS) or deployment hardening.
- Provide centralized authorization or consensus.
- Make hubs or the auditor authoritative policy engines.
- Feed quorum outcomes back into execution.

This demo constrains authority location. It does not replace provider security controls.

---

## Architectural Roles

### NUVL_A / NUVL_B (Neutral Fronts)

Each NUVL instance:

- Accepts opaque POST requests
- Computes `request_repr = SHA-256(request_bytes)`
- Reads:
  - `X-Verification-Context`
  - `X-Domain`
- Forwards `{request_repr, verification_context, domain}` to its configured hub `/submit`
- Returns constant HTTP 204

Failover occurs at `FAILOVER_AT`, shifting traffic from NUVL_A to NUVL_B.

NUVL does not:
- Evaluate thresholds
- Observe outcomes
- Initiate execution

---

### HUB_A / HUB_B (Mechanical Conveyance Only)

Each hub:

- Accepts artifacts at `/submit`
- Fans out artifacts to all providers (no semantics)
- Tracks relay counts for summary metrics
- Returns constant HTTP 204

Hubs do not:
- Hold provider secrets
- Evaluate provider decisions
- Infer semantics from outcomes
- Initiate execution

They are transport-only components.

---

### Providers (Execution Authority)

Each provider:

- Computes a deterministic provider-controlled score
- Applies domain-scoped thresholds:
  - `payments`
  - `identity`
  - `storage`
- Determines `initiated = True | False`
- Emits a signed outcome to the auditor

One provider is selected (or configured) as Byzantine:

- After `ACTIVE_BYZANTINE_AT`, its `initiated` bit flips
- This simulates adversarial or faulty behavior

Execution authority remains provider-scoped.

---

### Auditor (Observer-Only Quorum Aggregation)

The auditor:

- Accepts provider outcomes at `/audit`
- Verifies provider signatures
- Aggregates 2-of-3 quorum per `request_repr`
- Tracks:
  - Quorum successes
  - Quorum failures
  - Per-provider disagreement counts

Additional logic:

- Disagreement scoring measures how often a provider’s vote differs from the quorum outcome.
- A “most inconsistent provider” is identified for observability purposes only.

The auditor does not:
- Initiate execution
- Override provider authority
- Feed results back into hubs or NUVL

Aggregation is observational only.

---

## Multi-Domain Behavior

Requests are randomly assigned one of:

- `payments`
- `identity`
- `storage`

Providers apply thresholds per domain.

Domains are opaque to NUVL and hubs.

---

## Failover and Byzantine Simulation

### Requester Failover

At `FAILOVER_AT`:

- Traffic shifts from NUVL_A to NUVL_B
- Providers and auditor remain shared

This demonstrates transport-path changes without authority migration.

---

### Byzantine Injection

A provider is selected:

- Via environment variables (`BYZANTINE_PROVIDER`, `BYZANTINE_AT`)
- Or randomly within bounded ranges

After the flip index:

- The provider inverts its decision bit
- Quorum aggregation exposes disagreement

This demonstrates that:

- Intermediaries do not collapse into authority
- Aggregation reveals inconsistency without becoming authoritative

---

## Running the Demo

Run:

    python3 multi-hub-domain-failover-quorum.py

Environment variables:

- `TOTAL_REQUESTS`
- `FAILOVER_AT`
- `QUORUM_THRESHOLD`
- `EXPECTED_CONTEXT`
- `RANDOM_SEED`
- `BYZANTINE_PROVIDER`
- `BYZANTINE_AT`
- `NUVL_A_PORT`
- `NUVL_B_PORT`
- `HUB_A_PORT`
- `HUB_B_PORT`
- `AUDITOR_PORT`
- `WORKER_COUNT`
- `POST_QUEUE_MAX`

Defaults are benchmark-friendly and Replit-safe.

---

## Output (Compact Summary)

At completion, the demo prints:

- Total requests
- Failover index used
- Byzantine provider and flip index
- Timing window (NUVL 204 path)
- Hub fanout counts
- Provider initiation totals
- Provider initiation counts by domain
- Quorum successes / failures
- Per-provider disagreement rate
- Most inconsistent provider

These are observability metrics, not authorization results.

---

## Architectural Invariants

Across all execution paths:

- NUVL performs representation + forwarding only.
- Hubs perform mechanical conveyance only.
- Providers remain the sole execution authority.
- Provider secrets do not reside in hubs or NUVL.
- Quorum aggregation does not confer authority.
- Byzantine behavior is observable but does not migrate control.

---

## License

This demo incorporates components derived from the NUVL core, which is licensed under the Apache License, Version 2.0.

Except for Apache-2.0 licensed NUVL core components, all additional orchestration, failover logic, quorum aggregation, byzantine simulation, multi-hub routing, multi-domain threshold logic, worker pool implementation, and integration logic contained in this file is proprietary.

Commercial deployment, redistribution, or integration of proprietary portions requires a separate written license agreement.
