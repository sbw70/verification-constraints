# Demo — Multi-Hub / Multi-Domain Mesh  
## Mechanical Routing • Provider-Controlled Initiation • Hub-Relayed Outcome Signals

---

## Overview

This demo composes a multi-hub relay mesh with multi-provider fanout under the NUVL constraint model.

Two independent hubs accept opaque requester traffic and apply **mechanical routing only**:

- compute a non-reversible request representation (SHA-256 in this reference)
- compute a deterministic binding transform
- route artifacts to one or more providers based on **domain routing tables**
- optionally relay the same artifact to a peer hub for additional fanout

Providers remain the only execution authorities.  
Hubs remain intermediaries: they route and relay, but do not initiate operations.

Provider outcome signals are returned to a hub `/outcome` endpoint for **observability only**.  
Hubs do not treat returned outcomes as authorization input.

---

## Design Goals

This demo is designed to:

- Demonstrate multi-hub mechanical routing without hub-side authority
- Demonstrate multi-domain separation used for routing (not semantics)
- Demonstrate multi-provider fanout per domain
- Demonstrate fail-closed behavior for oversized requests and unknown domains
- Provide a compact benchmark summary for “real-ish traffic mix” runs

---

## Non-Goals

This demo does not:

- Provide production routing, retries, persistence, or durable queues
- Provide identity, authentication, or credential validation
- Provide secure transport (TLS) or deployment hardening
- Provide centralized authorization or consensus
- Make hubs authoritative policy engines or adjudicators

This demo constrains authority location. It does not replace provider security controls.

---

## Architectural Roles

### Hub A / Hub B (Mechanical Relay Only)

Each hub:

- Accepts requests at `/submit`
- Computes `request_repr = SHA-256(request_bytes)`
- Computes `binding = mechanical_bind(request_repr, verification_context, domain)`
- Computes a correlation id (for relay/aggregation only)
- Applies a routing plan:
  - fanout to configured providers
  - optional relay to peer hub
- Returns constant HTTP 204 to the requester (no outcome semantics)

If a hub receives a JSON relay from the peer hub, it preserves the forwarded fields verbatim (mechanical relay), rather than recomputing.

Hubs do not:
- hold provider secrets
- evaluate provider thresholds
- infer semantics from outcomes
- initiate execution

---

### Providers (Execution Authority)

Providers ingest artifacts and independently decide whether to initiate.

Provider evaluation includes:

- validating the hub-produced mechanical binding
- computing a provider-controlled adaptive score (demo stand-in for inference)
- applying provider thresholds per domain

Providers may produce provider-boundary artifacts (signed) when initiated.  
These signatures are generated inside provider boundary and are not used by hubs for decision-making.

Providers report outcome signals to a hub `/outcome` endpoint for observability only.

---

## Mechanical Routing Model

Routing is domain-scoped and mechanical:

- Domains are used to select a routing plan
- Unknown domains result in no routing (fail-closed by conveyance)
- Providers may also treat domains as policy inputs, but hubs do not interpret meaning

Example behaviors in this reference:

- Some domains fan out to multiple providers
- Some domains relay to the peer hub for additional distribution
- Unknown domains result in no provider fanout and no relay

---

## Failure and Mix Controls

This demo intentionally mixes request conditions:

- Spoofed verification contexts (requester-controlled)
- Unknown domains (routing fail-closed)
- Oversized requests (hub drops before routing)
- Normal valid requests (routed according to domain plan)

The requester receives HTTP 204 regardless.  
Provider outcomes are separate observability signals.

---

## Running the Demo

Run:

    python3 multi-hub-domain-verification.py

Replit-friendly controls via environment variables:

- PORT_BASE (default 12000)
- TOTAL_REQUESTS (default 100)
- SPOOF_RATE (default 0.10)
- UNKNOWN_DOMAIN_RATE (default 0.10)
- OVERSIZE_RATE (default 0.05)
- RANDOM_SEED (unset = nondeterministic)

---

## Reference Endpoints and Ports

Computed from PORT_BASE:

- HUB_A: /submit on PORT_BASE+80
- HUB_B: /submit on PORT_BASE+81
- PROVIDER_A: /ingest on PORT_BASE+90
- PROVIDER_B: /ingest on PORT_BASE+91
- PROVIDER_C: /ingest on PORT_BASE+92

Outcome endpoints (hub-local observability):

- HUB_A: /outcome on PORT_BASE+80
- HUB_B: /outcome on PORT_BASE+81

---

## Output (Compact Summary)

At completion, the demo prints a compact summary including:

- Requester mix counts (spoofed context, unknown domain, oversized drops)
- Hub acceptance and routing totals
- Requester timing window (measures hub 204 path only)
- Provider outcome signals observed by hub outcome endpoints
- Outcome counts by provider and by domain

These are observability metrics, not authorization outputs.

---

## Architectural Invariants

Across all execution paths:

- Hubs perform routing and relay only; they do not initiate execution.
- Providers remain the sole execution authority.
- Provider secrets never reside in hubs.
- Unknown domains fail-closed at routing (no conveyance to providers).
- Oversized requests fail-closed at hub ingest.
- Outcome signals are observational and do not confer authority.

---

## License

This demo incorporates components derived from the NUVL core, which is licensed under the Apache License, Version 2.0.

Except for Apache-2.0 licensed NUVL core components, all additional orchestration, routing, relay, multi-hub logic, multi-domain routing tables, adaptive provider evaluation, and integration logic contained in this file is proprietary.

Commercial deployment, redistribution, or integration of proprietary portions requires a separate written license agreement.
