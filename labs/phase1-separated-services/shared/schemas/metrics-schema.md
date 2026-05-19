# Metrics Schema

This schema defines the normalized metric structure used throughout the benchmark environment.

The purpose of the metrics schema is to ensure both request paths produce directly comparable telemetry and measurement data.

## Metric Shape

```json
{
  "trace_id": "trace_123",
  "path": "provider_first",
  "service": "verifier",
  "metric": "provider_seen_time_ms",
  "value": 4.2,
  "unit": "ms",
  "timestamp_ms": 1710000000000
}
```

## Required Fields

| Field | Purpose |
|---|---|
| `trace_id` | Shared request trace identifier |
| `path` | Benchmark path |
| `service` | Service emitting the metric |
| `metric` | Metric name |
| `value` | Numeric metric value |
| `unit` | Measurement unit |
| `timestamp_ms` | Metric timestamp |

## Path Values

```text
conventional
provider_first
```

## Standard Metrics

```text
request_latency_ms
provider_seen_time_ms
provider_decision_time_ms
gateway_processing_time_ms
application_activation_time_ms
data_service_time_ms
request_total_time_ms
requests_per_second
timeouts_total
errors_total
denials_total
allowed_total
db_touch_before_denial
systems_activated_before_denial
cpu_percent
memory_mb
```

## Standard Units

```text
ms
count
percent
mb
rps
```

## Purpose

This schema normalizes benchmark telemetry across all services and request paths.

Both architectures should emit metrics using the same measurement vocabulary so timing, activation behavior, and infrastructure interaction remain directly comparable.
