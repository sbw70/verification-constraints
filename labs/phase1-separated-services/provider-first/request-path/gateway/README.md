# Gateway

This directory contains the gateway layer for the provider-first benchmark path.

The gateway represents the intermediary routing layer that activates only after provider-controlled admissibility decisions occur.

Responsibilities may include:
- request routing
- protocol handling
- upstream forwarding
- response forwarding
- connection handling
- request normalization

Position in request path:

```text
Client
→ boundary
→ verifier
→ gateway
→ application
→ data-service
```

Unlike the conventional request path, the provider-first gateway activates after admissibility evaluation rather than before it.

This component is important to the benchmark because it helps demonstrate reduced intermediary-side execution before provider authorization occurs.
