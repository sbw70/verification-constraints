#!/bin/bash

mkdir -p evidence

echo "Running provider-first denied request..."
./scripts/test-provider-first.sh > evidence/provider-first-deny.json

echo "Running conventional denied request..."
./scripts/test-conventional.sh > evidence/conventional-deny.json

echo
echo "Evidence written:"
echo "  evidence/provider-first-deny.json"
echo "  evidence/conventional-deny.json"

echo
echo "Provider-first denial path:"
grep -o '"service":"[^"]*"' evidence/provider-first-deny.json

echo
echo "Conventional activation path:"
grep -o '"service":"[^"]*"' evidence/conventional-deny.json
