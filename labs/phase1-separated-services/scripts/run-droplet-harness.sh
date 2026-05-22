#!/usr/bin/env bash
set -euo pipefail

echo "[+] Starting phase1 separated services harness"

cd "$(dirname "$0")/.."

echo "[+] Stopping old containers"
sudo docker compose down --remove-orphans || true

echo "[+] Building containers"
sudo docker compose build

echo "[+] Starting containers"
sudo docker compose up -d

echo "[+] Container status"
sudo docker compose ps

echo "[+] Health checks"
sleep 3

echo "[conventional gateway]"
curl -s localhost:4000/health || true
echo

echo "[provider-first gateway]"
curl -s localhost:4100/health || true
echo

echo "[provider-first boundary]"
curl -s localhost:4101/health || true
echo

echo "[provider-first verifier]"
curl -s localhost:4102/health || true
echo

echo "[+] Done"
