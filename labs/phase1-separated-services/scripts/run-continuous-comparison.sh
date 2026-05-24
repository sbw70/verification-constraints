#!/usr/bin/env bash
set -u

# Locked public entrypoints (override allowed but not required)
CONVENTIONAL_URL="${CONVENTIONAL_URL:-http://localhost:3201/request}"
PROVIDER_FIRST_URL="${PROVIDER_FIRST_URL:-http://localhost:4103/gateway}"

# Loop pacing
SLEEP_SECONDS="${SLEEP_SECONDS:-0.05}"

# Token contract (must match service contract)
TOKEN_FIELD="${TOKEN_FIELD:-token}"
TOKEN="${TOKEN:-user-token}"

echo "[run] Continuous comparison loop starting..."
echo "[run] conventional:   $CONVENTIONAL_URL"
echo "[run] provider-first: $PROVIDER_FIRST_URL"
echo "[run] token field:    $TOKEN_FIELD"
echo "[run] token value:    $TOKEN"

while true; do
  NOW_MS="$(date +%s%3N)"
  TRACE_ID="trace_${NOW_MS}"

  CONVENTIONAL_BODY=$(cat <<JSON
{"trace_id":"$TRACE_ID","request_id":"${TRACE_ID}_conventional","$TOKEN_FIELD":"$TOKEN","action":"read","resource":"demo"}
JSON
)

  PROVIDER_FIRST_BODY=$(cat <<JSON
{"trace_id":"$TRACE_ID","request_id":"${TRACE_ID}_provider_first","$TOKEN_FIELD":"$TOKEN","action":"read","resource":"demo"}
JSON
)

  curl -sS --max-time 2 -X POST "$CONVENTIONAL_URL" \
    -H "Content-Type: application/json" \
    -d "$CONVENTIONAL_BODY" >/dev/null &

  PID_CONVENTIONAL=$!

  curl -sS --max-time 2 -X POST "$PROVIDER_FIRST_URL" \
    -H "Content-Type: application/json" \
    -d "$PROVIDER_FIRST_BODY" >/dev/null &

  PID_PROVIDER_FIRST=$!

  wait "$PID_CONVENTIONAL" || echo "[warn] conventional request failed: $TRACE_ID"
  wait "$PID_PROVIDER_FIRST" || echo "[warn] provider-first request failed: $TRACE_ID"

  sleep "$SLEEP_SECONDS"
done
