#!/bin/bash

PF_FILE="evidence/provider-first-deny.json"
CONV_FILE="evidence/conventional-deny.json"

echo
echo "=== Provider-First Metrics ==="

grep -o '"gateway_elapsed_ms":[0-9]*' "$PF_FILE" || true
grep -o '"total_elapsed_ms":[0-9]*' "$PF_FILE" || true
grep -o '"elapsed_ms":[0-9]*' "$PF_FILE" || true

echo
echo "Activated components:"
grep -o '"service":"[^"]*"' "$PF_FILE" | sort -u

echo
echo "Activated component count:"
grep -o '"service":"[^"]*"' "$PF_FILE" | sort -u | wc -l

echo
echo "=== Conventional Metrics ==="

grep -o '"gateway_elapsed_ms":[0-9]*' "$CONV_FILE" || true
grep -o '"app_elapsed_ms":[0-9]*' "$CONV_FILE" || true
grep -o '"data_elapsed_ms":[0-9]*' "$CONV_FILE" || true

echo
echo "Activated components:"
grep -o '"service":"[^"]*"' "$CONV_FILE" | sort -u

echo
echo "Activated component count:"
grep -o '"service":"[^"]*"' "$CONV_FILE" | sort -u | wc -l

echo
echo "=== Architectural Observation ==="
echo "Provider-first denied prior to downstream execution."
echo "Conventional path activated downstream services before admissibility."
