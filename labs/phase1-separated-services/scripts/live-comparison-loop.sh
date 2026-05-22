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

echo "run_id,timestamp_utc,iteration,path,result,raw" >> "$CSV_FILE"

iteration=0

echo "Starting live comparison loop"
echo "RUN_ID=$RUN_ID"
echo "CSV_FILE=$CSV_FILE"
echo "JSONL_FILE=$JSONL_FILE"
echo "SLEEP_SECONDS=$SLEEP_SECONDS"

while true; do
  iteration=$((iteration + 1))
  timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

  if [ -x scripts/test-conventional.sh ]; then
    conv_raw="$(scripts/test-conventional.sh 2>&1 | tr '\n' ' ' | sed 's/"/""/g')"
    echo "{\"run_id\":\"$RUN_ID\",\"timestamp\":\"$timestamp\",\"iteration\":$iteration,\"path\":\"conventional\",\"raw\":\"$conv_raw\"}" >> "$JSONL_FILE"
    echo "$RUN_ID,$timestamp,$iteration,conventional,completed,\"$conv_raw\"" >> "$CSV_FILE"
  else
    echo "$timestamp missing scripts/test-conventional.sh" | tee -a "$LOG_FILE"
  fi

  if [ -x scripts/test-provider-first.sh ]; then
    pf_raw="$(scripts/test-provider-first.sh 2>&1 | tr '\n' ' ' | sed 's/"/""/g')"
    echo "{\"run_id\":\"$RUN_ID\",\"timestamp\":\"$timestamp\",\"iteration\":$iteration,\"path\":\"provider-first\",\"raw\":\"$pf_raw\"}" >> "$JSONL_FILE"
    echo "$RUN_ID,$timestamp,$iteration,provider-first,completed,\"$pf_raw\"" >> "$CSV_FILE"
  else
    echo "$timestamp missing scripts/test-provider-first.sh" | tee -a "$LOG_FILE"
  fi

  sleep "$SLEEP_SECONDS"
done
