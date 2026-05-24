#!/usr/bin/env bash
set -u

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE_DIR"

echo "[droplet] Rebuilding Phase‑1 separated-services lab..."

# Stop old containers (ignore errors)
docker compose down || true

# Rebuild everything cleanly
docker compose build

# Start services in detached mode
docker compose up -d

echo "[droplet] Waiting for required services to become healthy..."

# Dashboard (passive telemetry receiver)
until curl -s http://localhost:3000/health >/dev/null; do
  echo "  dashboard not ready..."
  sleep 1
done

# Shared identity (internal service)
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

echo "[droplet] All services healthy."
echo "[droplet] Starting live comparison harness..."

# IMPORTANT:
# Droplet harness does NOT own a loop.
# It delegates to start-live-comparison.sh, which delegates to run-continuous-comparison.sh.
exec "$BASE_DIR/scripts/start-live-comparison.sh"
