# Provider-First Path

This directory contains the provider-first / NUVL-style request path used in the comparison environment.

The provider-first path attempts to move provider-controlled admissibility decisions earlier in the execution sequence before downstream infrastructure activates.

Typical flow:

```text
Client
→ provider-first boundary
→ verifier/provider admissibility decision
→ identity/session handling
→ application activation only if allowed
→ database/context interaction only if allowed
→ response
```

The purpose of this path is to measure whether earlier provider-controlled admissibility changes observable operational behavior.

Measurements may include:
- provider visibility timing
- rejection timing
- pre-denial activation
- database interaction before denial
- latency differences
- timeout behavior
- infrastructure activation order
- resource usage under invalid traffic

This path is not intended to prove that all intermediaries are harmful or unnecessary.

The benchmark exists to compare how request ordering changes operational behavior under equivalent workload conditions.
