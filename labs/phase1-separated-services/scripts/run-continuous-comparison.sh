#!/usr/bin/env bash
set -e

CONVENTIONAL_URL="http://localhost:3101/request"
PROVIDER_FIRST_URL="http://localhost:4103/gateway"

echo "[run] Continuous comparison loop starting..."

while true; do
  TRACE_ID="trace_$(date +%s%3N)"

  curl -s -X POST "$CONVENTIONAL_URL" \
    -H "Content-Type: application/json" \
    -d "{\"trace_id\":\"$TRACE_ID\",\"token\":\"user-token\"}" >/dev/null &

  curl -s -X POST "$PROVIDER_FIRST_URL" \
    -H "Content-Type: application/json" \
    -d "{\"trace_id\":\"$TRACE_ID\",\"token\":\"user-token\"}" >/dev/null &

  wait
  sleep 0.05
done
