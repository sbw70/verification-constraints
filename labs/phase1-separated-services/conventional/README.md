# Conventional Path

This directory contains the conventional enterprise-style request path used as the comparison baseline.

The conventional path represents a more typical intermediary-first execution sequence where downstream infrastructure may activate before provider-controlled admissibility decisions occur.

Typical flow:

```text
Client
→ gateway/intermediary
→ identity/session handling
→ application activation
→ database/context interaction
→ provider decision
→ allow/deny
→ response
```

The purpose of this path is not to represent every conventional architecture.

It exists as an operational comparison model for measuring:
- request timing
- service activation order
- provider visibility timing
- rejection timing
- pre-denial infrastructure activation
- pre-denial data interaction
- latency behavior
- timeout behavior
- resource usage under load

The benchmark compares this ordering against the provider-first path under equivalent workload and request conditions.
