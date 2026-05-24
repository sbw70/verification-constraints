#!/usr/bin/env bash
set -u

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE_DIR"

echo "[start] Bringing up Phase‑1 separated-services lab..."
docker compose up -d --build

echo "[start] Waiting for required services to become healthy..."

# Dashboard (passive telemetry receiver)
until curl -s http://localhost:3000/health >/dev/null; do
  echo "  dashboard not ready..."
  sleep 1
done

# Shared identity (internal service, not a request entrypoint)
until curl -s http://localhost:3101/health >/dev/null; do
  echo "  shared-identity not ready..."
  sleep 1
done

# Conventional gateway (public entrypoint)
until curl -s http://localhost:3201/health >/dev/null; do
  echo "  conventional-gateway not ready..."
  sleep 1
done

# Provider-first verifier (internal)
until curl -s http://localhost:4102/health >/dev/null; do
  echo "  provider-first-verifier not ready..."
  sleep 1
done

# Provider-first gateway (public entrypoint)
until curl -s http://localhost:4103/health >/dev/null; do
  echo "  provider-first-gateway not ready..."
  sleep 1
done

echo "[start] All services healthy."
echo "[start] Launching continuous comparison loop..."

exec "$BASE_DIR/scripts/run-continuous-comparison.sh"
