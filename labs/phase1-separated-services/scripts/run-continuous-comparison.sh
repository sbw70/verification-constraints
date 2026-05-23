#!/usr/bin/env bash

set -euo pipefail

CONVENTIONAL_URL="${CONVENTIONAL_URL:-http://localhost:3101/request}"
PROVIDER_FIRST_URL="${PROVIDER_FIRST_URL:-http://localhost:4101/boundary-check}"

RPS="${RPS:-20}"
VALID_RATIO="${VALID_RATIO:-30}"
SLEEP_SECONDS="$(awk "BEGIN { print 1 / $RPS }")"

echo "Starting continuous comparison load"
echo "Conventional URL:   $CONVENTIONAL_URL"
echo "Provider-first URL: $PROVIDER_FIRST_URL"
echo "RPS:                $RPS"
echo "Valid ratio:        $VALID_RATIO%"
echo

request_count=0

while true; do
  request_count=$((request_count + 1))

  trace_id="trace-${request_count}"
  request_id="req-${request_count}"

  random_value=$((RANDOM % 100))

  if [ "$random_value" -lt "$VALID_RATIO" ]; then
    token="admin-token"
  else
    token="user-token"
  fi

  payload=$(
    cat <<JSON
{
  "trace_id": "$trace_id",
  "request_id": "$request_id",
  "token": "$token",
  "action": "read",
  "resource": "account-record"
}
JSON
  )

  curl -s -o /dev/null -w "conventional,%{http_code},%{time_total}\n" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "$CONVENTIONAL_URL" &

  curl -s -o /dev/null -w "provider-first,%{http_code},%{time_total}\n" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "$PROVIDER_FIRST_URL" &

  wait

  sleep "$SLEEP_SECONDS"
done
