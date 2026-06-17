# Data Service

This directory contains the data interaction layer for the provider-first benchmark path.

The data service represents stateful infrastructure that activates only after provider-controlled admissibility decisions occur.

Responsibilities may include:
- database interaction
- persistence operations
- context retrieval
- state access
- query execution
- downstream data coordination

Position in request path:

```text
Client
→ boundary
→ verifier
→ gateway
→ application
→ data-service
```

Unlike the conventional request path, the provider-first data service is intended to avoid activation during denied or inadmissible requests whenever possible.

This component is important to the benchmark because it helps measure:
- pre-denial database interaction reduction
- stateful infrastructure confinement
- downstream activation differences
- post-admissibility execution behavior
