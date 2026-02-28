# Demo — Offline Relay + Temporal Gatekeeping Stress Test
## Deferred Conveyance • Provider-Online Gate • Provider-Controlled Initiation

---

## Overview

This demo composes an **offline relay buffer** with a **provider-side temporal gate** under the NUVL constraint model.

Flow:

Requester → NUVL (bind + forward) → Relay (offline buffer) → Uplink (deferred delivery) → Provider (authority)

The system simulates:

- A provider boundary that is **offline for an initial window**
- A conveyance-only relay that **buffers artifacts while the provider is offline**
- A periodic uplink that drains the relay buffer once the provider becomes online
- Provider-controlled initiation that is **independent of delivery timing**
- Binding verification at the provider boundary to prevent semantic drift during offline periods

Across all flows:

- NUVL computes representation + deterministic binding and forwards only.
- The relay stores and forwards only; it does not evaluate or initiate.
- The provider is the only execution authority.
- Timing gaps and deferred delivery do not migrate authority into intermediaries.

---

## Design Goals

This demo is designed to:

- Demonstrate offline/air-gap style buffering as conveyance-only behavior.
- Demonstrate provider-controlled “online gate” as the only temporal authority.
- Demonstrate that deferred delivery does not change initiation semantics.
- Demonstrate deterministic binding verification at the provider boundary.
- Demonstrate mixed traffic (valid vs spoofed contexts) under deferred relay.
- Provide a compact benchmark summary for stress-style runs.

---

## Non-Goals

This demo does not:

- Provide production durability, persistence, or crash-safe queues.
- Provide secure transport (TLS), authentication, or identity infrastructure.
- Provide multi-provider consensus, quorum, or global ordering.
- Provide real scheduling, time windows, or clock-trust semantics.
- Make the relay authoritative or allow it to infer execution meaning.

This is an authority-location and deferred-conveyance demonstration, not a hardened deployment reference.

---

## Architectural Roles

### NUVL (Neutral: Bind + Forward)

NUVL:

- Accepts requests at `/nuvl`
- Computes `request_repr = SHA-256(request_bytes)`
- Reads:
  - `X-Verification-Context`
  - `X-Domain`
  - `X-Seq`
- Computes a deterministic binding:

  `binding = nuvl_bind(request_repr, verification_context, domain)`

- Forwards an artifact to the relay:

  `{request_repr, verification_context, domain, binding, seq}`

- Returns constant HTTP 204 to the requester

NUVL does not:
- Observe provider availability
- Observe provider outcomes
- Initiate execution

---

### Relay (Offline Buffer: Conveyance Only)

The relay:

- Accepts artifacts at `/relay`
- Buffers artifacts in-memory while the provider is offline
- Does not validate bindings or contexts
- Does not initiate execution
- Holds no provider secrets

The relay is a store-and-forward intermediary only.

---

### Uplink (Deferred Transmission)

The uplink loop:

- Periodically attempts to deliver buffered artifacts to the provider
- Only drains the relay buffer when the provider is online
- Sends artifacts in small batches (bounded) to simulate practical uplink behavior

The uplink is transport behavior only and is not an authority component.

---

### Provider (Authority: Temporal Gatekeeping + Initiation)

The provider:

- Accepts artifacts at `/ingest`
- Enforces a provider-controlled online gate:

  - If offline: drops artifacts (HTTP 204) without evaluation
  - If online: evaluates artifacts

- Validates deterministic binding:

  - Computes `expected = nuvl_bind(rr, ctx, domain)`
  - Requires `binding == expected`

- Applies a temporal gate condition (demo form):

  - `initiated = binding_ok AND ctx == EXPECTED_CONTEXT`

- Computes a provider-boundary signature (provider-only secret) as an internal boundary artifact

Provider authority characteristics:

- Initiation occurs only inside the provider boundary.
- Deferred delivery does not confer authority to the relay or uplink.
- The provider decides when it is “online” and when evaluation occurs.

---

## Deferred Conveyance Model

This demo explicitly separates:

- **Conveyance time** (when the relay receives / stores / forwards artifacts)
from
- **Initiation time** (when the provider is online and evaluates artifacts)

Artifacts may be delayed arbitrarily without changing initiation semantics because:

- The provider re-derives expected binding deterministically
- The provider enforces context acceptance inside the boundary
- No intermediary is permitted to reinterpret timing gaps as authorization evidence

---

## Failure and Mix Controls

This demo intentionally mixes request conditions:

- Provider offline window for the first `OFFLINE_FIRST_N` requests
- Spoofed contexts every 10th request (`CTX_SPOOFED`)
- Normal requests with expected context (`CTX_ALPHA`)

The requester always receives HTTP 204 for accepted NUVL ingest.  
Provider initiation occurs only when online and when binding + context pass.

---

## Running the Demo

Run:

    python3 offline-temporal-gatekeeping.py

Key tunables (edit in file):

- `TOTAL_REQUESTS`
- `OFFLINE_FIRST_N`
- `UPLINK_INTERVAL_S`
- `POST_WORKERS`
- `POST_QUEUE_MAX`

Ports:

- NUVL: `/nuvl` on `NUVL_PORT`
- Relay: `/relay` on `RELAY_PORT`
- Provider: `/ingest` on `PROVIDER_PORT`

---

## Output (Compact Summary)

At completion, the demo prints:

- Total requests
- Provider offline window size
- Requester 204 count and error count (measures NUVL 204 path)
- Total requester time and average per request
- Relay buffered artifacts remaining
- Uplink enqueued delivery count

Provider (authority) metrics:

- Artifacts seen while online
- Initiations (valid binding + expected context)
- Binding mismatches observed by provider

These are observability metrics, not authorization outputs from intermediaries.

---

## Architectural Invariants

Across all execution paths:

- NUVL performs representation + deterministic binding + forward only.
- The relay buffers and forwards only; it does not evaluate or initiate.
- Uplink behavior is transport-only and does not confer authority.
- Provider is the sole execution authority and controls the online gate.
- Deferred delivery does not alter authorization semantics.
- Binding verification prevents semantic drift across offline periods.
- Provider secrets never reside in NUVL, relay, or uplink components.

---

## License

This demo incorporates components derived from the NUVL core, which is licensed under the Apache License, Version 2.0.

Except for Apache-2.0 licensed NUVL core components, all additional orchestration, offline relay buffering, deferred uplink logic, temporal gatekeeping behavior, stress harness logic, and integration code contained in this file is proprietary.

Commercial deployment, redistribution, or integration of proprietary portions requires a separate written license agreement.
