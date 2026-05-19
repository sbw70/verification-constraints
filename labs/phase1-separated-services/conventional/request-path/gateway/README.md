# Gateway

The gateway is the first infrastructure component in the conventional request path.

Responsibilities may include:
- request ingress
- routing
- header processing
- session forwarding
- protocol normalization
- upstream coordination
- traffic handling

Position in request path:

```text
Client
→ gateway
→ application
→ data-service
→ provider-adapter
→ provider/verifier
```

In the conventional path, the gateway accepts and forwards requests before provider-controlled authorization occurs.

The gateway is intentionally placed before provider verification to demonstrate intermediary-first execution behavior.
