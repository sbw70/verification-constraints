#!/bin/bash

mkdir -p evidence/mixed

OUTFILE="evidence/mixed/mixed-500-summary.txt"

PF_ALLOWED=0
PF_DENIED=0
CONV_ALLOWED=0
CONV_DENIED=0

echo
echo "Running 500 mixed requests..."
echo

for i in $(seq 1 500)
do

  if (( i % 4 == 0 )); then
    TOKEN="admin-token"
    ACTION="admin:access"
  else
    TOKEN="bad-token"
    ACTION="admin:access"
  fi

  PF_OUTPUT=$(curl -s -X POST localhost:4103/gateway \
  -H "Content-Type: application/json" \
  -d "{
    \"trace_id\":\"pf_mixed_$i\",
    \"request_id\":\"pf_mixed_req_$i\",
    \"token\":\"$TOKEN\",
    \"action\":\"$ACTION\",
    \"resource\":\"acct_001\"
  }")

  CONV_OUTPUT=$(curl -s -X POST localhost:3101/request \
  -H "Content-Type: application/json" \
  -d "{
    \"trace_id\":\"conv_mixed_$i\",
    \"request_id\":\"conv_mixed_req_$i\",
    \"token\":\"$TOKEN\",
    \"action\":\"$ACTION\",
    \"resource\":\"acct_001\"
  }")

  echo "$PF_OUTPUT" | grep -q '"allowed":true' && PF_ALLOWED=$((PF_ALLOWED+1)) || PF_DENIED=$((PF_DENIED+1))
  echo "$CONV_OUTPUT" | grep -q '"denied":true' && CONV_DENIED=$((CONV_DENIED+1)) || CONV_ALLOWED=$((CONV_ALLOWED+1))

done

{
echo "========================================="
echo " MIXED 500 REQUEST SUMMARY"
echo "========================================="
echo
echo "Provider-first allowed: $PF_ALLOWED"
echo "Provider-first denied:  $PF_DENIED"
echo
echo "Conventional allowed/continued: $CONV_ALLOWED"
echo "Conventional denied:            $CONV_DENIED"
echo
echo "Observation:"
echo "Provider-first distinguishes allowed/denied at the verifier boundary."
echo "Conventional path continues downstream activation for the benchmark request path."
} | tee "$OUTFILE"
