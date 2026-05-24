#!/usr/bin/env bash
set -u

# Thin compatibility wrapper.
# This script must NEVER own a loop.
# It simply delegates to the single loop owner:
# run-continuous-comparison.sh

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
exec "$BASE_DIR/scripts/run-continuous-comparison.sh"
