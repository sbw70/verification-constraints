# Request Path

This directory contains the ordered execution chain for the provider-first benchmark path.

The provider-first request path represents a constrained execution model where provider-controlled admissibility occurs before downstream application infrastructure activates.

Typical execution flow:

```text
Client
→ boundary
→ verifier
→ gateway
→ application
→ data-service
→ response
```

Unlike the conventional intermediary-first model, the provider-first path attempts to constrain execution before downstream systems allocate resources, activate workflows, or interact with stateful infrastructure.

The purpose of this path is to measure the behavioral differences created by changing request ordering and admissibility position within the execution chain.

Components within this path may:
- evaluate admissibility earlier
- reduce downstream activation before denial
- reduce intermediary-side execution depth
- reduce latency accumulation before rejection
- constrain infrastructure activation scope

This request path exists to measure:
- provider visibility timing
- denial timing behavior
- downstream activation reduction
- pre-denial infrastructure interaction
- execution confinement behavior
- resource utilization differences
- intermediary execution reduction
