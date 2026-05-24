#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

RUN_ID="${RUN_ID:-live-$(date -u +%Y%m%dT%H%M%SZ)}"
SLEEP_SECONDS="${SLEEP_SECONDS:-2}"
OUT_DIR="${OUT_DIR:-evidence/live}"
CSV_FILE="${CSV_FILE:-evidence/csv/live-comparison.csv}"
JSONL_FILE="$OUT_DIR/${RUN_ID}.jsonl"
LOG_FILE="$OUT_DIR/${RUN_ID}.log"

mkdir -p "$OUT_DIR" "$(dirname "$CSV_FILE")"

if [ ! -f "$CSV_FILE" ]; then
  echo "run_id,timestamp_utc,iteration,path,result,exit_code,elapsed_ms,raw" > "$CSV_FILE"
fi

json_escape() {
  python3 -c 'import json, sys; print(json.dumps(sys.stdin.read()))'
}

run_check() {
  local path="$1"
  local script="$2"
  local iteration="$3"

  local timestamp
  local start_ms
  local end_ms
  local elapsed_ms
  local raw
  local exit_code
  local result
  local raw_json
  local raw_csv

  timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  start_ms="$(date +%s%3N)"

  if [ -x "$script" ]; then
    raw="$("$script" 2>&1)"
    exit_code=$?
  else
    raw="missing executable: $script"
    exit_code=127
  fi

  end_ms="$(date +%s%3N)"
  elapsed_ms=$((end_ms - start_ms))

  if [ "$exit_code" -eq 0 ]; then
    result="completed"
  else
    result="failed"
  fi

  raw_json="$(printf "%s" "$raw" | json_escape)"
  raw_csv="$(printf "%s" "$raw" | tr '\n' ' ' | sed 's/"/""/g')"

  printf '{"run_id":"%s","timestamp_utc":"%s","iteration":%s,"path":"%s","result":"%s","exit_code":%s,"elapsed_ms":%s,"raw":%s}\n' \
    "$RUN_ID" "$timestamp" "$iteration" "$path" "$result" "$exit_code" "$elapsed_ms" "$raw_json" >> "$JSONL_FILE"

  printf '%s,%s,%s,%s,%s,%s,%s,"%s"\n' \
    "$RUN_ID" "$timestamp" "$iteration" "$path" "$result" "$exit_code" "$elapsed_ms" "$raw_csv" >> "$CSV_FILE"

  if [ "$exit_code" -ne 0 ]; then
    echo "$timestamp $path failed: $raw" >> "$LOG_FILE"
  fi
}

iteration=0

echo "Starting live comparison loop"
echo "RUN_ID=$RUN_ID"
echo "CSV_FILE=$CSV_FILE"
echo "JSONL_FILE=$JSONL_FILE"
echo "SLEEP_SECONDS=$SLEEP_SECONDS"

while true; do
  iteration=$((iteration + 1))

  run_check "conventional" "scripts/test-conventional.sh" "$iteration"
  run_check "provider-first" "scripts/test-provider-first.sh" "$iteration"

  sleep "$SLEEP_SECONDS"
done
