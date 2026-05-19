# Request Path

This directory contains the ordered execution chain for the conventional benchmark path.

The request path represents the sequence of infrastructure and application components activated during request handling before provider-controlled admissibility decisions occur.

Typical execution flow:

```text
Client
→ gateway
→ application
→ data-service
→ provider-adapter
→ provider/verifier
→ allow/deny
→ response
```

The purpose of this request path is to simulate a more conventional intermediary-first execution model where downstream systems may activate before provider-controlled authorization occurs.

Components within this path may:
- allocate execution resources
- process requests
- enrich context
- interact with state or persistence layers
- coordinate downstream services
- accumulate latency before provider rejection

This request path exists as the comparison baseline for measuring:
- provider visibility timing
- downstream activation depth
- pre-denial infrastructure interaction
- latency accumulation
- rejection timing
- resource utilization
- intermediary-side orchestration behavior
