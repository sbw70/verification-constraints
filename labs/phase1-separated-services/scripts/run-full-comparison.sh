#!/bin/bash

echo
echo "========================================="
echo " PROVIDER-FIRST vs CONVENTIONAL TEST"
echo "========================================="

echo
echo "[1] Running comparative evidence generation..."
./scripts/run-evidence-pair.sh

echo
echo "[2] Extracting metrics..."
./scripts/extract-metrics.sh

echo
echo "[3] Evidence files generated:"
ls evidence

echo
echo "========================================="
echo " TEST COMPLETE"
echo "========================================="
