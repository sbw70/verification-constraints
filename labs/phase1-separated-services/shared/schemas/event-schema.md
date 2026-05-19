# Event Schema

This schema defines the benchmark event format used by both request paths.

Every service should emit events in the same structure so conventional and provider-first behavior can be compared directly.

## Event Shape

```json
{
  "trace_id": "trace_123",
  "path": "conventional",
  "service": "gateway",
  "event": "request_received",
  "timestamp_ms": 1710000000000,
  "elapsed_ms": 0,
  "outcome": "initiated",
  "request_id": "req_123",
  "token_type": "valid_user",
  "action": "transaction:create",
  "resource": "acct_123",
  "provider_decision_seen": false,
  "db_touched": false,
  "notes": ""
}
```

## Required Fields

| Field | Purpose |
|---|---|
| `trace_id` | Shared identifier for one request across all services |
| `path` | `conventional` or `provider_first` |
| `service` | Component emitting the event |
| `event` | What happened at that service |
| `timestamp_ms` | Wall-clock timestamp in milliseconds |
| `elapsed_ms` | Time since request initiation |
| `outcome` | Current request state |
| `request_id` | Unique request identifier |
| `token_type` | Type of test token used |
| `action` | Requested action |
| `resource` | Target resource |
| `provider_decision_seen` | Whether provider/verifier has been reached |
| `db_touched` | Whether data/state layer was touched |
| `notes` | Optional diagnostic text |

## Path Values

```text
conventional
provider_first
```

## Standard Events

```text
request_initiated
request_received
identity_checked
gateway_forwarded
application_activated
data_service_touched
provider_adapter_called
boundary_checked
verifier_seen
provider_allowed
provider_denied
response_returned
request_timed_out
request_errored
```

## Standard Outcomes

```text
initiated
in_progress
allowed
denied
timed_out
errored
```

## Purpose

This schema keeps both benchmark paths comparable.

The internal ordering may differ, but both paths must emit events using the same vocabulary.
