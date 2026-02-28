# Region Failover + Randomized Byzantine Quorum (Minimal Demo)

## Overview

This demo composes a small set of NUVL-adjacent constraint behaviors into a single, runnable reference:

Requester → NUVL_A / NUVL_B → HUB_A / HUB_B → Providers → Non-Authoritative Auditor

It demonstrates:

- **Region failover** between two independent NUVL fronts (A → B mid-run)
- **Multi-hub relay** as a mechanical conveyance tier
- **Provider-scoped adaptive decision** (domain thresholds)
- **Randomized Byzantine behavior** (one provider flips after a random index)
- **2-of-3 quorum aggregation** by an external auditor

Core invariant: **NUVL fronts bind/represent + forward only** and return constant HTTP 204.  
Authorization/execution authority remains **provider-controlled**.

---

## Design Goals

This demo is designed to:

- Show that **failover** does not migrate authority into intermediaries.
- Show that **transport/relay layers** can remain non-authoritative.
- Show that **provider decisions** can be aggregated for observability without centralizing execution control.
- Introduce a controlled **Byzantine injection** to stress quorum behavior.

---

## Non-Goals

This demo does not:

- Provide production reliability (durable queues, retries, persistence).
- Provide secure transport (TLS), auth, identity, or credentialing.
- Provide consensus, ordering, settlement, or “global truth.”
- Allow hubs/NUVL/auditor to initiate execution.

This is an **authority-location** demonstration, not a deployment blueprint.

---

## Components and Responsibilities

### NUVL Fronts (Region A / Region B)

Two independent NUVL HTTP servers:

- Accept opaque request bytes.
- Compute `request_repr = SHA-256(payload)`.
- Pass through opaque headers:
  - `X-Verification-Context`
  - `X-Domain`
- Forward an artifact to the local hub.
- Return **HTTP 204** with no body.
- Do **not** receive or interpret provider outcomes.

Failover is requester-driven via `FAILOVER_AT`.

---

### Hubs (Mechanical Conveyance)

Each hub:

- Receives the artifact from its region’s NUVL.
- Fans out the same artifact to all providers.
- Performs no policy checks.
- Returns **HTTP 204**.

Hubs are **transport-only** in this model.

---

### Providers (Authoritative Boundaries)

Each provider:

- Computes a deterministic score (HMAC-derived) using provider-only key material.
- Applies a domain threshold (`payments`, `identity`, `storage`).
- Produces a boolean “initiated” signal.
- Signs the signal and sends it to the auditor.

One provider becomes Byzantine at runtime:

- `ACTIVE_BYZ_PROVIDER` is randomly selected.
- After `ACTIVE_BYZ_AT`, that provider **flips** its decision bit.

Providers remain the only authoritative decision points.

---

### Auditor (Non-Authoritative Aggregation)

The auditor:

- Verifies provider signatures.
- Aggregates 3 provider signals per request representation.
- Computes **2-of-3 quorum**:
  - `QUORUM_SUCCESS` if ≥ 2 providers report initiated
  - `QUORUM_FAIL` otherwise

The auditor is **observational**. It does not initiate operations and does not feed back into NUVL.

---

## Execution Flow

1. Requester sends requests `0..TOTAL_REQUESTS-1`.
2. For `i < FAILOVER_AT`, requests go to **NUVL_A**; otherwise to **NUVL_B**.
3. Each NUVL computes `request_repr` and forwards `{request_repr, verification_context, domain}` to its hub.
4. Each hub fans out the artifact to all providers.
5. Each provider evaluates independently and emits a signed signal to the auditor.
6. The auditor aggregates signals and updates quorum counters.

Requester always sees **HTTP 204** from NUVL fronts.

---

## Running

Run:

    python3 region-fallover-quorum.py

Defaults (as configured in the file):

- `TOTAL_REQUESTS = 750`
- `FAILOVER_AT = 375`
- `QUORUM_THRESHOLD = 2`
- `RANDOM_SEED = 1337`

Ports:

- Region A: `NUVL_A_PORT=8000`, `HUB_A_PORT=8100`
- Region B: `NUVL_B_PORT=8001`, `HUB_B_PORT=8101`
- Auditor: `AUDITOR_PORT=8200`
- Providers: `9001`, `9002`, `9003`

---

## Expected Output

At completion, the demo prints:

- Total requests
- Failover index
- Randomly selected Byzantine provider
- Random flip index
- Total time + average per request
- Provider initiation counts
- Auditor quorum successes / failures

These are **demo observability counters**. NUVL remains outcome-blind.

---

## Architectural Invariants

- NUVL returns constant **HTTP 204** and never emits outcomes.
- Hubs are conveyance-only; they do not decide.
- Providers determine initiation independently.
- Auditor aggregates but does not initiate execution.
- Failover does not move authority into transport layers.
- Byzantine behavior is contained by quorum aggregation without centralizing control.

---

## License

This demo incorporates Apache-2.0 licensed components derived from the NUVL core.

Except for Apache-2.0 licensed NUVL core components, all additional orchestration, failover logic, quorum aggregation, adversarial simulation, and integration logic contained in this file is proprietary.

Commercial deployment, redistribution, or integration of proprietary portions requires a separate written license agreement.
