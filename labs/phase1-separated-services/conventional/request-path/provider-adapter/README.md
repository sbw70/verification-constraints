# Provider Adapter

The provider adapter is the conventional path component responsible for forwarding late-stage authorization or admissibility requests to the provider/verifier layer.

Position in request path:

```text
Client
→ gateway
→ application
→ data-service
→ provider-adapter
→ provider/verifier
```

In this ordering, downstream systems may already:
- allocate execution resources
- activate application logic
- establish sessions
- interact with context/state
- touch data services

before provider-controlled authorization occurs.

The adapter itself does not hold provider authority.

It acts as the conventional path interface to external provider-controlled verification systems.
