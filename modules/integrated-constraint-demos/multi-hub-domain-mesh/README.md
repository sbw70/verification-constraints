# Demo — Multi-NUVL / Multi-Hub Relay + Quorum Audit
## Mechanical Forwarding • Provider-Controlled Initiation • Hub-Relayed Signed Outcomes

---

## Overview

This demo composes two independent NUVL fronts with a two-hub relay mesh and multi-provider fanout under the NUVL constraint model.

Two NUVL instances accept opaque requester traffic and perform **representation + forwarding only**:

- compute a non-reversible request representation (`SHA-256(request_bytes)`)
- read opaque headers (`X-Verification-Context`, `X-Domain`)
- forward `{request_repr, verification_context, domain}` to a hub endpoint
- return constant HTTP 204

Two hubs relay and fan out artifacts **mechanically**:

- fan out the received artifact to all providers (no semantics)
- relay the same artifact to the peer hub (mesh-style duplication)

Providers remain the only execution authorities.  
Hubs remain intermediaries: they route and relay, but do not initiate operations.

Provider outcome signals are posted to a non-authoritative auditor for **observability only**.  
The auditor computes a 2-of-3 quorum result per `request_repr`, but does not initiate execution and does not feed decisions back into NUVL or hubs.

---

## Design Goals

This demo is designed to:

- Demonstrate two NUVL fronts that forward representations only (constant 204)
- Demonstrate a two-hub peer relay mesh (mechanical duplication + fanout)
- Demonstrate multi-provider fanout without hub-side authority
- Demonstrate provider-controlled initiation using domain-scoped thresholds
- Demonstrate signed provider outcome signals and auditor-side verification
- Demonstrate non-authoritative 2-of-3 quorum aggregation
- Provide a compact benchmark summary for “real-ish traffic mix” runs

---

## Non-Goals

This demo does not:

- Provide production routing, retries, persistence, or durable queues
- Provide identity, authentication, or credential validation
- Provide secure transport (TLS) or deployment hardening
- Provide centralized authorization or consensus
- Make NUVL, hubs, or the auditor authoritative policy engines or adjudicators
- Provide domain-based routing tables inside hubs (fanout is uniform in this reference)

This demo constrains authority location. It does not replace provider security controls.

---

## Architectural Roles

### NUVL_A / NUVL_B (Representation + Forward Only)

Each NUVL instance:

- Accepts requests at `/nuvl`
- Computes `request_repr = SHA-256(request_bytes)`
- Reads opaque headers:
  - `X-Verification-Context`
  - `X-Domain`
- Forwards `{request_repr, verification_context, domain}` to its local hub at `/hub`
- Returns constant HTTP 204
- Does not observe provider outcomes

Failover is requester-driven: requests before the selected index go to `NUVL_A`, after the index go to `NUVL_B`.

NUVL does not evaluate provider decisions.

---

### Hub A / Hub B (Mechanical Relay Only)

Each hub:

- Accepts artifacts at `/hub`
- Fans out received artifacts to **all** configured providers (no semantics)
- Relays the same artifact to the peer hub (mesh duplication)
- Tracks peer relay counts for summary output
- Returns constant HTTP 204

Hubs do not:
- hold provider secrets
- evaluate provider thresholds
- infer semantics from outcomes
- initiate execution

---

### Providers (Execution Authority)

Providers ingest artifacts and independently decide whether to initiate.

Provider evaluation includes:

- computing a provider-controlled score (demo stand-in for inference)
- applying provider thresholds per domain (`payments`, `identity`, `storage`)

One provider (`PROVIDER_C`) is configured to simulate Byzantine behavior:

- after a randomized index, `PROVIDER_C` flips its `initiated` bit

Providers emit signed outcome signals to the auditor:

- signature is `HMAC(provider_key, request_repr)`

---

### Auditor (Observer-Only Quorum Aggregation)

The auditor:

- accepts outcomes at `/audit`
- verifies provider signatures
- aggregates 2-of-3 quorum over `{initiated}` per `request_repr`
- tracks:
  - signed outcomes received
  - rejected (bad signature) outcomes
  - quorum successes / failures

The auditor does not:
- initiate execution
- override provider authority
- feed results back into NUVL or hubs

Aggregation is observational only.

---

## Mechanical Routing Model

Routing in this reference is **mechanical fanout + mesh relay**:

- hubs do not select providers based on domain
- hubs do not interpret domain semantics
- domain is carried as an opaque field and is used by providers for threshold selection

---

## Failure and Mix Controls

This demo intentionally mixes request conditions:

- Spoofed verification contexts (requester-controlled, ~10%)
- Randomized failover point during the run (bounded index range)
- Randomized Byzantine flip point for `PROVIDER_C` (bounded index range)

The requester receives HTTP 204 regardless.  
Provider outcomes are separate observability signals.

---

## Running the Demo

Run:

    python3 <file-name>.py

Default ports:

- NUVL_A: 8000  (POST /nuvl)
- NUVL_B: 8001  (POST /nuvl)
- HUB_A:  8100  (POST /hub)
- HUB_B:  8101  (POST /hub)
- Auditor: 8200 (POST /audit)
- Providers: 9001 / 9002 / 9003 (POST /ingest)

Key tunables (edit in file):

- TOTAL_REQUESTS
- RANDOM_SEED (set `None` for nondeterministic)
- FAILOVER_MIN / FAILOVER_MAX
- BYZANTINE_MIN / BYZANTINE_MAX
- QUORUM_THRESHOLD
- MAX_WORKERS / HTTP_TIMEOUT_S

---

## Output (Compact Summary)

At completion, the demo prints a compact summary including:

- Total requests
- Randomized failover index used
- Byzantine flip index used for `PROVIDER_C`
- Requester timing window (measures NUVL 204 path only)
- Hub peer relay counts
- Provider initiation totals and by-domain breakdown
- Auditor observed outcomes:
  - signed outcomes received
  - bad signatures rejected
  - quorum successes / failures

These are observability metrics, not authorization outputs.

---

## Architectural Invariants

Across all execution paths:

- NUVL performs representation + forwarding only; constant HTTP 204.
- Hubs relay and fan out mechanically; they do not initiate execution.
- Providers remain the sole execution authority.
- Provider secrets never reside in NUVL or hubs.
- Outcome signals are observational and do not confer authority to intermediaries.
- Quorum aggregation does not become an execution authority.

---

## License

This demo incorporates components derived from the NUVL core, which is licensed under the Apache License, Version 2.0.

Except for Apache-2.0 licensed NUVL core components, all additional orchestration, routing, relay, multi-hub logic, multi-domain handling, adaptive provider evaluation, byzantine simulation, quorum aggregation, and integration logic contained in this file is proprietary.

Commercial deployment, redistribution, or integration of proprietary portions requires a separate written license agreement.
