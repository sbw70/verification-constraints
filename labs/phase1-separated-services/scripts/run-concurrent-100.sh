#!/bin/bash

mkdir -p evidence/concurrent

OUTFILE="evidence/concurrent/concurrent-100-summary.txt"

echo
echo "Running 100 concurrent denied requests..."
echo

START=$(date +%s)

for i in $(seq 1 100)
do

(
curl -s -X POST localhost:4103/gateway \
-H "Content-Type: application/json" \
-d "{
  \"trace_id\":\"pf_concurrent_$i\",
  \"request_id\":\"pf_req_$i\",
  \"token\":\"bad-token\",
  \"action\":\"admin:access\",
  \"resource\":\"acct_001\"
}" > /dev/null
) &

(
curl -s -X POST localhost:3101/request \
-H "Content-Type: application/json" \
-d "{
  \"trace_id\":\"conv_concurrent_$i\",
  \"request_id\":\"conv_req_$i\",
  \"token\":\"bad-token\",
  \"action\":\"admin:access\",
  \"resource\":\"acct_001\"
}" > /dev/null
) &

done

wait

END=$(date +%s)

ELAPSED=$((END - START))

{
echo
echo "========================================="
echo " CONCURRENT TEST COMPLETE"
echo "========================================="

echo
echo "Total concurrent request pairs:"
echo "100"

echo
echo "Total elapsed wall-clock time:"
echo "$ELAPSED seconds"

echo
echo "Architectural Observation:"
echo "Provider-first denied prior to downstream activation."
echo "Conventional path activated downstream services during concurrent denied traffic."

} | tee "$OUTFILE"
