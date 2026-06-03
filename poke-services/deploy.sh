#!/bin/bash
# ⚡ Poke Labs — One-Command Deployment
# Starts all 12 micro-services + gateway
# Usage: bash /home/alx/deploy.sh

BASE="/home/alx/services"
LOG="/tmp"

echo "⚡ Poke Labs Deployment"

# Kill existing
for d in link-preview keyword summarize qr dns portal color url-shortener template-gen health-agg json2ts github-webhook gateway; do
  pkill -f "$d/server.py" 2>/dev/null || true
done
sleep 1

# Start services
declare -A SVC=(
  [link-preview]=8765 [keyword]=8766 [summarize]=8767 [qr]=8768
  [dns]=8769 [portal]=8770 [color]=8771 [url-shortener]=8772
  [template-gen]=8773 [health-agg]=8774 [json2ts]=8775 [github-webhook]=8776
)

for name in "${!SVC[@]}"; do
  port="${SVC[$name]}"
  if [ -f "$BASE/$name/server.py" ]; then
    nohup python3 "$BASE/$name/server.py" > "$LOG/$name.log" 2>&1
    echo "  → $name :$port"
  fi
done

# Gateway last
nohup python3 "$BASE/gateway/server.py" > "$LOG/gateway.log" 2>&1
echo "  → gateway :8700"
echo "All services started. Gateway: http://localhost:8700"
