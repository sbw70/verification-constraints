#!/bin/bash

mkdir -p evidence/batch

OUTFILE="evidence/batch/500-run-summary.txt"

PF_TOTAL=0
CONV_GATEWAY_TOTAL=0
CONV_APP_TOTAL=0
CONV_DATA_TOTAL=0

{
echo
echo "Running 500 comparative denied requests..."
echo

for i in $(seq 1 500)
do

  PF_OUTPUT=$(curl -s -X POST localhost:4103/gateway \
  -H "Content-Type: application/json" \
  -d "{
    \"trace_id\":\"pf_trace_$i\",
    \"request_id\":\"pf_req_$i\",
    \"token\":\"bad-token\",
    \"action\":\"admin:access\",
    \"resource\":\"acct_001\"
  }")

  CONV_OUTPUT=$(curl -s -X POST localhost:3101/request \
  -H "Content-Type: application/json" \
  -d "{
    \"trace_id\":\"conv_trace_$i\",
    \"request_id\":\"conv_req_$i\",
    \"token\":\"bad-token\",
    \"action\":\"admin:access\",
    \"resource\":\"acct_001\"
  }")

  PF_GATEWAY=$(echo "$PF_OUTPUT" | grep -o '"gateway_elapsed_ms":[0-9]*' | cut -d: -f2)
  CONV_GATEWAY=$(echo "$CONV_OUTPUT" | grep -o '"gateway_elapsed_ms":[0-9]*' | cut -d: -f2)
  CONV_APP=$(echo "$CONV_OUTPUT" | grep -o '"app_elapsed_ms":[0-9]*' | cut -d: -f2)
  CONV_DATA=$(echo "$CONV_OUTPUT" | grep -o '"data_elapsed_ms":[0-9]*' | cut -d: -f2)

  PF_TOTAL=$((PF_TOTAL + PF_GATEWAY))
  CONV_GATEWAY_TOTAL=$((CONV_GATEWAY_TOTAL + CONV_GATEWAY))
  CONV_APP_TOTAL=$((CONV_APP_TOTAL + CONV_APP))
  CONV_DATA_TOTAL=$((CONV_DATA_TOTAL + CONV_DATA))

done

echo
echo "========================================="
echo " 500 RUN COMPARISON RESULTS"
echo "========================================="

echo
echo "Provider-First Average Gateway Time:"
echo "$((PF_TOTAL / 500)) ms"

echo
echo "Conventional Average Gateway Time:"
echo "$((CONV_GATEWAY_TOTAL / 500)) ms"

echo
echo "Conventional Average App Time:"
echo "$((CONV_APP_TOTAL / 500)) ms"

echo
echo "Conventional Average Data-Service Time:"
echo "$((CONV_DATA_TOTAL / 500)) ms"

echo
echo "Architectural Observation:"
echo "Provider-first denied prior to downstream execution."
echo "Conventional path activated downstream application and data services."

echo
echo "Summary written to:"
echo "$OUTFILE"

} | tee "$OUTFILE"
