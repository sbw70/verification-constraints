# Phase 1 — Separated Services

Phase 1 moves the benchmark harness from a single-process simulation into multiple independent services communicating across real network boundaries.

The goal is to begin measuring operational behavior between separated components instead of simulated in-process function calls.

This phase introduces:
- independent services
- network-based request flow
- separated execution paths
- observable service activation order
- measurable inter-service latency

This phase is still intentionally lightweight.

It is not intended to replicate a full enterprise deployment.

The purpose is to create a controlled side-by-side comparison environment for observing how request ordering changes system behavior before provider-controlled admissibility decisions occur.

## Core Question

```text
How much infrastructure activates before the provider can say no?
```

## Comparison Model

The benchmark environment contains two execution paths:

### Conventional Path

```text
Client
→ intermediary/gateway
→ application activation
→ database/context interaction
→ provider decision
→ allow/deny
```

### Provider-First Path

```text
Client
→ provider-first boundary
→ verifier/provider admissibility decision
→ application activation only if allowed
→ response
```

The purpose is not to force identical architecture.

The purpose is to compare:
- ordering
- activation timing
- infrastructure exposure
- rejection timing
- pre-denial execution behavior

under equivalent request intent and workload conditions.

## Shared Components

Both paths share:
- dashboard
- metrics schema
- load generation
- workload patterns
- request types
- outcome vocabulary

This ensures the comparison remains operationally consistent.

## Initial Services

Phase 1 introduces independent services such as:

```text
gateway
verifier
application API
dashboard
load generator
```

These services communicate across real network boundaries instead of direct in-process calls.

## Measurement Goals

Phase 1 focuses on observing:
- provider visibility timing
- service activation order
- latency differences
- denial timing
- pre-denial infrastructure activation
- pre-denial database interaction
- timeout propagation
- resource behavior under mixed traffic

## Expected Outcome

The expected result is not architectural equivalence.

The expected result is observable operational difference caused by request ordering.

## Future Expansion

Later phases may introduce:
- PostgreSQL
- Keycloak
- gateway policy layers
- orchestration behavior
- replay handling
- persistent metrics
- containerized deployment
- distributed service placement

The purpose of Phase 1 is to establish measurable multi-service behavior before introducing enterprise-scale complexity.
