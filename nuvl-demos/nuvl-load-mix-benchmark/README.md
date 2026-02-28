# NUVL Demo — Load Mix Benchmark (10k)

## Overview

This reference provides a high-volume load mix benchmark that exercises NUVL under sustained request throughput while injecting a controlled distribution of failure conditions.

NUVL remains a stateless verification intermediary:

- It derives a non-reversible request representation (SHA-256 in this reference).
- It applies a deterministic binding transform over request representation and an opaque verification context.
- It constructs verification artifacts and forwards them asynchronously.
- It returns a constant HTTP 204 response and disengages.

This benchmark varies intermediary behavior (good bind, binding mismatch, malformed JSON, dropped forward) to demonstrate that load and failure injection do not migrate authorization semantics into NUVL.

Authorization authority remains exclusively within provider-controlled systems.

---

## Design Goals

This reference is designed to:

- Demonstrate NUVL behavior under sustained load (10,000 requests)
- Exercise mixed validity and forwarding disruption at scale
- Preserve stateless bind-and-forward behavior during throughput stress
- Provide provider-boundary observability without making NUVL outcome-aware

---

## Non-Goals

This reference does not:

- Provide production-grade benchmarking methodology
- Provide transport reliability guarantees, buffering, or retry orchestration
- Provide requester correlation to provider evaluation outcomes
- Provide identity, credential validation, or session state
- Model TLS, adversarial networks, or resource isolation controls

This demo constrains authority location. It does not represent production performance.

---

## Benchmark Definition

### Total Request Volume

- `TOTAL_REQUESTS = 10000`

### Mix Distribution

The benchmark selects a per-request mode using a randomized distribution:

- `GOOD` — valid binding and normal artifact forwarding
- `BINDING_FAIL` — intentionally wrong binding value
- `MALFORMED_JSON` — intentionally malformed JSON payload to provider ingest
- `DROP_FORWARD` — artifact is not forwarded (provider does not receive input)

The distribution is configured via:

- `P_GOOD`
- `P_BINDING_FAIL`
- `P_MALFORMED_JSON`
- `P_DROP_FORWARD`

The probabilities are intended to sum to `1.0`.

### Repeatability

A fixed seed may be supplied for repeatable runs:

- `RANDOM_SEED = <int>` for deterministic runs
- `RANDOM_SEED = None` for non-deterministic runs

---

## Architectural Model

### Execution Flow

Requester → NUVL → Provider

For each request in the benchmark:

1. Requester submits opaque request bytes to NUVL with `X-Verification-Context`.
2. NUVL enforces a fixed maximum request size (`MAX_REQUEST_BYTES`).
3. NUVL derives `request_repr` as `SHA-256(request_bytes)` (hex).
4. NUVL selects a benchmark mode and executes the corresponding conveyance behavior.
5. NUVL returns HTTP 204 with a blank body and disengages.
6. The provider ingests received artifacts and applies provider-defined evaluation logic.

NUVL does not observe provider-side evaluation outcomes.

---

## Provider Boundary Observability

This reference includes optional provider-side accounting to summarize provider ingest behavior.

These counters exist inside the provider boundary and do not alter NUVL’s role.

Provider-side output is summarized rather than printed per request.

This benchmark preserves the constraint that NUVL remains outcome-blind even when provider-side observability exists.

---

## Running the Reference

```bash
python3 nuvl-load-mix-benchmark.py
```

Ports used by this reference:

- NUVL: `127.0.0.1:8080` (`POST /nuvl`)
- Provider: `127.0.0.1:9090` (`POST /ingest`)

---

## Expected Behavior

- The requester receives constant HTTP 204 responses.
- NUVL performs deterministic request representation and controlled mode selection.
- Artifact forwarding is best-effort and asynchronous.
- Provider-side initiation authority remains exclusive to the provider-controlled boundary.
- Benchmark load and injected failures do not introduce authorization semantics into NUVL.

---

## Security Model

Authorization authority is provider-scoped.

- NUVL does not hold signing material.
- NUVL does not evaluate authorization semantics.
- Authorization is realized exclusively by provider-side initiation.
- Mixed validity and forwarding disruption do not migrate authority into the intermediary.

This reference demonstrates stability of the NUVL boundary constraints under sustained throughput with injected failure conditions.

---

## License

Licensed under the Apache License, Version 2.0.
