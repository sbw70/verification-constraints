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
```

### Provider-First

```text
Client
→ provider verifier
→ application/database touch only if allowed
→ response
```

## Core Measurement

The main measurement is:

```text
How much system activity occurs before provider denial?
```

In this phase, that is represented by database touches before denial.

## Run

```bash
npm install
node lab.js
```

Then open:

```text
http://localhost:3000
```

On the live droplet, open:

```text
http://134.209.221.94:3000/
```

## Next Phases

Future phases should split the harness into real services:

```text
phase1-split-verifier
phase2-postgres
phase3-gateway
phase4-keycloak
```

The purpose of Phase 0 is to establish the live comparison harness before adding infrastructure complexity.
