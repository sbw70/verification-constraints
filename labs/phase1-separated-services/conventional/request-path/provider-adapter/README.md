# Provider Adapter

The provider adapter is responsible for translating internal application requests into provider-compatible verification requests.

Responsibilities may include:
- request translation
- verification request construction
- provider communication
- response normalization
- protocol adaptation
- retry handling
- timeout handling

Position in request path:

```text
Client
→ gateway
→ application
→ data-service
→ provider-adapter
→ provider/verifier
```

The provider adapter exists to represent the final intermediary-side execution layer before provider-controlled authorization occurs.

In conventional enterprise architectures, this layer commonly performs additional processing before the provider decision is returned.

This component is important to the benchmark because it helps demonstrate:
- execution occurring before admissibility
- downstream activation depth
- intermediary coordination behavior
- latency accumulation before denial
- authority drift through orchestration layers
