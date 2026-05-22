#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "Starting phase1 separated-services live comparison"

if [ -f docker-compose.yml ]; then
  docker compose up -d --build
elif [ -f compose.yml ]; then
  docker compose -f compose.yml up -d --build
else
  echo "No docker-compose.yml or compose.yml found"
  exit 1
fi

echo "Waiting for services..."
sleep 5

echo "Docker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo "Starting continuous comparison loop"
exec ./scripts/live-comparison-loop.sh
