# Data Service

The data service represents downstream state or persistence infrastructure activated during request handling.

Responsibilities may include:
- database interaction
- session retrieval
- context lookup
- state access
- record retrieval
- persistence operations

Position in request path:

```text
Client
→ gateway
→ application
→ data-service
→ provider-adapter
→ provider/verifier
```

In the conventional request ordering model, the data layer may be touched before provider-controlled authorization or admissibility decisions occur.

This component exists to measure:
- pre-denial database activation
- downstream infrastructure exposure
- request-path execution depth
- latency introduced prior to provider rejection
