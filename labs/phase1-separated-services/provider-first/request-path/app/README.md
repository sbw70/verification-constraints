# Application

This directory contains the primary application execution layer for the provider-first benchmark path.

The application layer represents business logic and execution behavior that activates after provider-controlled admissibility decisions occur.

Responsibilities may include:
- request processing
- business logic execution
- workflow coordination
- downstream service interaction
- response generation
- application state handling

Position in request path:

```text
Client
→ boundary
→ verifier
→ gateway
→ application
→ data-service
```

Unlike the conventional intermediary-first model, the application layer activates only after verification and admissibility evaluation complete.

This component is important to the benchmark because it helps measure:
- downstream activation reduction
- post-admissibility execution behavior
- constrained application activation
- execution timing differences
