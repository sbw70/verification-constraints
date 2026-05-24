#!/usr/bin/env bash
set -euo pipefail

CONVENTIONAL_URL="${CONVENTIONAL_URL:-http://localhost:3101/request}"
PROVIDER_FIRST_URL="${PROVIDER_FIRST_URL:-http://localhost:4103/gateway}"

RPS="${RPS:-20}"
BURST_RPS="${BURST_RPS:-80}"
BURST_SECONDS="${BURST_SECONDS:-5}"
BURST_EVERY_SECONDS="${BURST_EVERY_SECONDS:-60}"

ALLOW_RATIO="${ALLOW_RATIO:-30}"

ALLOW_TOKEN="${ALLOW_TOKEN:-admin-token}"
DENY_TOKEN="${DENY_TOKEN:-user-token}"

ACTION="${ACTION:-admin:access}"
RESOURCE="${RESOURCE:-acct_001}"

request_count=0

echo "Continuous comparison load started"
echo "Conventional:       $CONVENTIONAL_URL"
echo "Provider-first:     $PROVIDER_FIRST_URL"
echo "Steady RPS pairs:   $RPS"
echo "Burst RPS pairs:    $BURST_RPS for ${BURST_SECONDS}s every ${BURST_EVERY_SECONDS}s"
echo "Allow ratio:        ${ALLOW_RATIO}%"
echo "Action:             $ACTION"
echo "Resource:           $RESOURCE"
echo

make_payload() {
  local token="$1"
  local n="$2"
  local expected="$3"

  cat <<JSON
{
  "trace_id": "continuous_trace_${n}",
  "request_id": "continuous_req_${n}",
  "token": "${token}",
  "expected_result": "${expected}",
  "action": "${ACTION}",
  "resource": "${RESOURCE}"
}
JSON
}

send_pair() {
  local r
  local token
  local expected
  local payload

  request_count=$((request_count + 1))
  r=$((RANDOM % 100))

  if [ "$r" -lt "$ALLOW_RATIO" ]; then
    token="$ALLOW_TOKEN"
    expected="allowed"
  else
    token="$DENY_TOKEN"
    expected="denied"
  fi

  payload="$(make_payload "$token" "$request_count" "$expected")"

  curl -sS -o /dev/null \
    -w "conventional,%{http_code},%{time_total},${expected}\n" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "$CONVENTIONAL_URL" &

  curl -sS -o /dev/null \
    -w "provider-first,%{http_code},%{time_total},${expected}\n" \
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

  if [ "$steady_for" -gt 0 ]; then
    run_load "$RPS" "$steady_for"
  fi

  echo "$(date -Is) burst start"
  run_load "$BURST_RPS" "$BURST_SECONDS"
  echo "$(date -Is) burst end"
done
