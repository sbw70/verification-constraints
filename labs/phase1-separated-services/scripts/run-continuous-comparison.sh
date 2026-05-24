#!/usr/bin/env bash
set -euo pipefail

CONVENTIONAL_URL="${CONVENTIONAL_URL:-http://localhost:3101/request}"
PROVIDER_FIRST_URL="${PROVIDER_FIRST_URL:-http://localhost:4103/gateway}"

RPS="${RPS:-20}"
BURST_RPS="${BURST_RPS:-80}"
BURST_SECONDS="${BURST_SECONDS:-5}"
BURST_EVERY_SECONDS="${BURST_EVERY_SECONDS:-60}"
VALID_RATIO="${VALID_RATIO:-30}"

VALID_TOKEN="${VALID_TOKEN:-admin-token}"
INVALID_TOKEN="${INVALID_TOKEN:-user-token}"

request_count=0

echo "Continuous comparison load started"
echo "Conventional:       $CONVENTIONAL_URL"
echo "Provider-first:     $PROVIDER_FIRST_URL"
echo "Steady RPS pairs:   $RPS"
echo "Burst RPS pairs:    $BURST_RPS for ${BURST_SECONDS}s every ${BURST_EVERY_SECONDS}s"
echo "Valid ratio:        ${VALID_RATIO}%"
echo

make_payload() {
  local token="$1"
  local action="$2"
  local n="$3"

  cat <<JSON
{
  "trace_id": "continuous_trace_${n}",
  "request_id": "continuous_req_${n}",
  "token": "${token}",
  "action": "${action}",
  "resource": "acct_001"
}
JSON
}

send_pair() {
  local r
  local token
  local action
  local payload

  request_count=$((request_count + 1))
  r=$((RANDOM % 100))

  if [ "$r" -lt "$VALID_RATIO" ]; then
    token="$VALID_TOKEN"
    action="admin:access"
  else
    token="$INVALID_TOKEN"
    action="admin:access"
  fi

  payload="$(make_payload "$token" "$action" "$request_count")"

  curl -sS -o /dev/null \
    -w "conventional,%{http_code},%{time_total}\n" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "$CONVENTIONAL_URL" &

  curl -sS -o /dev/null \
    -w "provider-first,%{http_code},%{time_total}\n" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "$PROVIDER_FIRST_URL" &

  wait
}

run_load() {
  local rps="$1"
  local seconds="$2"
  local delay
  local end

  delay="$(awk "BEGIN { print 1 / $rps }")"
  end=$((SECONDS + seconds))

  while [ "$SECONDS" -lt "$end" ]; do
    send_pair
    sleep "$delay"
  done
}

while true; do
  steady_for=$((BURST_EVERY_SECONDS - BURST_SECONDS))

  run_load "$RPS" "$steady_for"

  echo "$(date -Is) burst start"
  run_load "$BURST_RPS" "$BURST_SECONDS"
  echo "$(date -Is) burst end"
done
