#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost}"
CONVENTIONAL_URL="${CONVENTIONAL_URL:-$BASE_URL:4000/api/conventional/data}"
PROVIDER_FIRST_URL="${PROVIDER_FIRST_URL:-$BASE_URL:4100/api/provider-first/data}"

RPS="${RPS:-20}"
BURST_RPS="${BURST_RPS:-80}"
BURST_SECONDS="${BURST_SECONDS:-5}"
BURST_EVERY_SECONDS="${BURST_EVERY_SECONDS:-60}"

VALID_TOKEN="${VALID_TOKEN:-admin-token}"
INVALID_TOKEN="${INVALID_TOKEN:-user-token}"

echo "Continuous comparison load started"
echo "Conventional:     $CONVENTIONAL_URL"
echo "Provider-first:   $PROVIDER_FIRST_URL"
echo "RPS:              $RPS"
echo "Burst RPS:        $BURST_RPS for ${BURST_SECONDS}s every ${BURST_EVERY_SECONDS}s"
echo

send_one() {
  local target="$1"
  local token="$2"

  curl -sS -o /dev/null \
    -w "%{http_code} %{time_total}\n" \
    -H "Authorization: Bearer ${token}" \
    "$target" || true
}

run_load() {
  local rps="$1"
  local seconds="$2"
  local delay
  delay="$(awk "BEGIN { print 1 / $rps }")"

  local end=$((SECONDS + seconds))

  while [ "$SECONDS" -lt "$end" ]; do
    if [ $((RANDOM % 2)) -eq 0 ]; then
      target="$CONVENTIONAL_URL"
    else
      target="$PROVIDER_FIRST_URL"
    fi

    if [ $((RANDOM % 10)) -lt 7 ]; then
      token="$INVALID_TOKEN"
    else
      token="$VALID_TOKEN"
    fi

    send_one "$target" "$token" >/dev/null &
    sleep "$delay"
  done

  wait
}

while true; do
  steady_for=$((BURST_EVERY_SECONDS - BURST_SECONDS))

  run_load "$RPS" "$steady_for"

  echo "$(date -Is) burst start"
  run_load "$BURST_RPS" "$BURST_SECONDS"
  echo "$(date -Is) burst end"
done
