#!/usr/bin/env bash
set -euo pipefail

curl -sS -X POST http://localhost:4103/gateway \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "pf_trace_script",
    "request_id": "pf_req_script",
    "token": "bad-token",
    "action": "admin:access",
    "resource": "acct_001"
  }'
