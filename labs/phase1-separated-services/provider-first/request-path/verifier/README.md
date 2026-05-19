# Verifier

This directory contains the provider-controlled verification component for the provider-first benchmark path.

The verifier is responsible for evaluating admissibility before downstream infrastructure activation occurs.

Responsibilities may include:
- request verification
- token validation
- signature validation
- admissibility decisions
- replay prevention
- request integrity validation
- verification response generation

Position in request path:

```text
Client
→ boundary
→ verifier
→ gateway
→ application
→ data-service
```

The verifier exists to represent provider-controlled decision authority occurring earlier in the request lifecycle.

This component is important to the benchmark because it helps measure:
- provider visibility timing
- rejection timing behavior
- downstream execution reduction
- admissibility-before-execution behavior
- constrained infrastructure activation
