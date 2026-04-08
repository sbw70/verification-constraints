# NUVL Demo — Identity Architecture Benchmark

## Overview

This benchmark measures the end-to-end request performance difference between
two architectural approaches to identity and verification under identical
sustained load.

**Identity-first (traditional)**

```
client
  ↓
IAM gateway
  ↓ base64 decode + JSON parse
  ↓ HMAC signature verify
  ↓ policy table lookup
  ↓ [optional auth-server jitter]
  ↓ synchronous provider forward  ← blocks until provider responds
provider
```

**Identity-second (NUVL)**

```
client
  ↓
NUVL layer
  ↓ SHA-256 request representation
  ↓ deterministic binding computation
  ↓ async artifact forward dispatch  ← off critical path
immediate HTTP 204 return
provider (runs in background)
```

The hypothesis under test:

> Moving identity off the critical request path reduces latency, stabilizes
> tail percentiles, and lowers context-switching overhead.

---

## Design Goals

- Demonstrate observable latency difference between the two architectures.
- Expose p99 sensitivity to synchronous auth-server dependency (jitter).
- Preserve NUVL constraint invariants during high-concurrency throughput.
- Report metrics that infrastructure teams recognize: p50/p95/p99, throughput,
  context switches, and wall time.

---

## Non-Goals

This reference does not:

- Provide production-grade benchmarking methodology.
- Model TLS, adversarial networks, or resource isolation controls.
- Provide transport reliability guarantees, buffering, or retry orchestration.
- Introduce new identity, session, or credential semantics.

This demo constrains authority location and isolates architectural effect.
It does not represent production performance.

---

## Architecture Detail

### Identity-first: What runs on the critical path

Every request incurs the full synchronous chain before a response is returned:

| Step | Operation | Notes |
|------|-----------|-------|
| 1 | Base64 decode + JSON parse | Object allocation per request |
| 2 | HMAC-SHA256 verify | Cryptographic compute |
| 3 | Policy table lookup | Represents a cache or DB call |
| 4 | Auth-server jitter (probabilistic) | Models slow OAuth/IAM backend |
| 5 | Synchronous HTTP POST to provider | Client blocked until step 5 returns |

The client receives no response until the provider round-trip completes.

### Identity-second (NUVL): What runs on the critical path

| Step | Operation | Notes |
|------|-----------|-------|
| 1 | SHA-256 request representation | Single hash, no I/O |
| 2 | Deterministic binding computation | Second SHA-256, no I/O |
| 3 | Async forward dispatch | Daemon thread, non-blocking |
| 4 | HTTP 204 return | Client unblocked immediately |

Provider evaluation happens asynchronously. NUVL holds no signing material,
evaluates no policy, and cannot relay provider authorization decisions.

---

## Benchmark Definition

### Request volume

```python
TOTAL_REQUESTS = 10_000
```

### Concurrency

```python
CONCURRENCY = 20
```

Each architecture is benchmarked with an identical pool of 20 concurrent
worker threads issuing requests back-to-back.

### Auth-server jitter (identity-first only)

```python
IAM_JITTER_P  = 0.02   # 2 % of requests hit a slow auth path
IAM_JITTER_MS = 6.0    # +6 ms added when jitter fires
```

Jitter is injected inside the IAM gateway to model occasional slow auth-server
responses — the primary cause of p99 inflation in identity-first stacks.

### Repeatability

```python
RANDOM_SEED = None   # non-deterministic
RANDOM_SEED = 1234   # deterministic
```

---

## Metrics Reported

| Metric | Description |
|--------|-------------|
| p50 latency | Median request round-trip time (ms) |
| p95 latency | 95th-percentile round-trip time (ms) |
| p99 latency | 99th-percentile round-trip time (ms) |
| avg latency | Mean round-trip time (ms) |
| min / max latency | Best and worst observed single request (ms) |
| throughput | Requests per second over total wall time |
| vol. context switches | Voluntary context switch delta for benchmark phase |
| invol. context switches | Involuntary context switch delta for benchmark phase |

---

## Ports

Four in-process HTTP servers are started automatically:

| Role | Port | Path |
|------|------|------|
| Identity-first IAM gateway | `127.0.0.1:8181` | `POST /auth` |
| Identity-first provider | `127.0.0.1:9191` | `POST /ingest` |
| Identity-second NUVL | `127.0.0.1:8282` | `POST /nuvl` |
| Identity-second provider | `127.0.0.1:9292` | `POST /ingest` |

---

## Running the Reference

```bash
python3 nuvl-identity-architecture-benchmark.py
```

Expected output shape:

```
[1/2] Running identity-first benchmark ...
      Done. Wall time: X.XXX s
[2/2] Running identity-second (NUVL) benchmark ...
      Done. Wall time: X.XXX s

==================================================================
IDENTITY ARCHITECTURE BENCHMARK — RESULTS
==================================================================
Metric                           Identity-first  Identity-second
------------------------------------------------------------------
  p50 latency (ms)                        X.XXX            X.XXX
  p95 latency (ms)                        X.XXX            X.XXX
  p99 latency (ms)                        X.XXX            X.XXX
  ...
------------------------------------------------------------------
  Deltas (identity-second vs identity-first baseline):
  p50 delta                             baseline            +X.X%
  p95 delta                             baseline            +X.X%
  p99 delta                             baseline            +X.X%
  throughput delta                      baseline            +X.X%
==================================================================
```

---

## Expected Behavior

- The requester receives constant HTTP 204 responses from both architectures.
- Identity-first p99 latency exceeds p50 by a measurable margin due to the
  synchronous provider dependency and auth jitter.
- Identity-second latency is bounded by local compute (two SHA-256 hashes),
  independent of provider response time.
- Throughput favors identity-second because the critical path is shorter and
  contains no blocking I/O.
- Context switch counts are typically higher for identity-first due to blocking
  I/O waits on the provider round-trip.

---

## Security Model

Authorization authority is provider-scoped in the identity-second architecture.

- NUVL does not hold signing material.
- NUVL does not evaluate authorization policy.
- NUVL cannot relay or substitute for provider-controlled execution authority.
- The async artifact conveyance does not grant NUVL any authority over
  provider-side initiation decisions.

The identity-first architecture places the IAM gateway on the authority path
by design. This benchmark isolates the latency and scheduling cost of that
placement — it does not argue for or against any particular security model.

---

## License

Licensed under the Apache License, Version 2.0.
