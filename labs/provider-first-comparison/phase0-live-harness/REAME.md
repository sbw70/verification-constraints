# Phase 0 Live Harness

This is a single-process live benchmark harness for comparing provider-first request ordering against conventional request ordering.

It runs as one Node.js process and provides:
- live dashboard
- built-in background traffic
- conventional path simulation
- provider-first path simulation
- latency metrics
- provider timing metrics
- denial behavior metrics
- pre-denial database touch metrics
- basic host/process resource metrics

## Important Scope

This is Phase 0.

It is not a full distributed enterprise stack.

The verifier, database, API, and dashboard currently run inside one process. This makes the harness useful for validating measurement logic and dashboard behavior before splitting components into separate services.

## Paths Compared

### Conventional

```text
Client
→ application/database touch
→ provider verifier
→ allow/deny
