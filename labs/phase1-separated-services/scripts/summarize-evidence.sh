#!/bin/bash

PF_FILE="evidence/provider-first-deny.json"
CONV_FILE="evidence/conventional-deny.json"

echo "=== Provider-First Denial Path ==="
grep -o '"service":"[^"]*"' "$PF_FILE"
echo
echo "Provider-first activated component count:"
grep -o '"service":"[^"]*"' "$PF_FILE" | sort -u | wc -l

echo
echo "=== Conventional Denial Path ==="
grep -o '"service":"[^"]*"' "$CONV_FILE"
echo
echo "Conventional activated component count:"
grep -o '"service":"[^"]*"' "$CONV_FILE" | sort -u | wc -l

echo
echo "=== Execution Contrast ==="
echo "Provider-first: denied before app/data activation."
echo "Conventional: invalid request reached app and data-service."
