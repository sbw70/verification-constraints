# Application Service

The application service represents the primary execution layer in the conventional request path.

Responsibilities may include:
- request handling
- business logic execution
- orchestration
- workflow coordination
- downstream service activation
- context enrichment

Position in request path:

```text
Client
→ gateway
→ application
→ data-service
→ provider-adapter
→ provider/verifier
```

In the conventional path, the application layer may begin execution before provider-controlled admissibility decisions occur.

The purpose of this component is to measure:
- execution activation before denial
- latency accumulation
- downstream orchestration behavior
- intermediary-side resource consumption
