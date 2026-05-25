#!/usr/bin/env bash
set -u

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE_DIR"

echo "[start] Bringing up Phase‑1 separated-services lab..."
docker compose up -d --build

echo "[start] Waiting for public services to become healthy..."

# Dashboard (public)
until curl -s http://localhost:3000/health >/dev/null; do
  echo "  dashboard not ready..."
  sleep 1
done

# Conventional gateway (public)
until curl -s http://localhost:3201/health >/dev/null; do
  echo "  conventional-gateway not ready..."
  sleep 1
done

# Provider-first gateway (public)
until curl -s http://localhost:4103/health >/dev/null; do
  echo "  provider-first-gateway not ready..."
  sleep 1
done

echo "[start] All public services healthy."
echo "[start] Launching continuous comparison loop..."

exec "$BASE_DIR/scripts/run-continuous-comparison.sh"
