#!/usr/bin/env bash
set -euo pipefail

curl -sS -X POST http://localhost:3101/request \
  -H "Content-Type: application/json" \
  -d '{
    "trace_id": "conv_trace_script",
    "request_id": "conv_req_script",
    "token": "bad-token",
    "action": "admin:access",
    "resource": "acct_001"
  }'
