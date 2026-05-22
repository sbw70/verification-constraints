#!/bin/bash

mkdir -p evidence/csv

OUTFILE="evidence/csv/500-comparison.csv"

echo "run,pf_gateway_ms,conv_gateway_ms,conv_app_ms,conv_data_ms" > "$OUTFILE"

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

  echo "$i,$PF_GATEWAY,$CONV_GATEWAY,$CONV_APP,$CONV_DATA" >> "$OUTFILE"

done

echo
echo "CSV export complete:"
echo "$OUTFILE"
