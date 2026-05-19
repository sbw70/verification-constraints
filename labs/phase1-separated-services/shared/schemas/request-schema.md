# Request Schema

This schema defines the normalized request structure used across both benchmark paths.

The purpose of the schema is to keep workload intent identical while allowing request ordering behavior to differ between architectures.

## Request Shape

```json
{
  "request_id": "req_123",
  "trace_id": "trace_123",
  "timestamp_ms": 1710000000000,
  "path": "conventional",
  "token": "token_value",
  "token_type": "valid_user",
  "action": "transaction:create",
  "resource": "acct_123",
  "payload": {
    "amount": 250,
    "destination_account": "acct_999"
  },
  "headers": {
    "x-trace-id": "trace_123"
  }
}
```

## Required Fields

| Field | Purpose |
|---|---|
| `request_id` | Unique request identifier |
| `trace_id` | Shared identifier across the execution chain |
| `timestamp_ms` | Request creation timestamp |
| `path` | Target benchmark path |
| `token` | Authentication or session token |
| `token_type` | Test token classification |
| `action` | Requested business action |
| `resource` | Target resource identifier |
| `payload` | Request body or transaction data |
| `headers` | Supplemental request metadata |

## Path Values

```text
conventional
provider_first
```

## Standard Token Types

```text
valid_user
valid_admin
invalid_token
expired_token
replay_token
wrong_scope
wrong_account
```

## Standard Actions

```text
profile:read
transaction:create
transaction:approve
admin:access
account:update
```

## Purpose

Both benchmark paths should receive functionally identical requests.

The benchmark compares:
- execution ordering
- infrastructure activation
- admissibility timing
- rejection timing
- downstream activation behavior

The benchmark does not compare different workloads or request semantics.
