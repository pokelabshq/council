#!/bin/bash
# ============================================================
# 🫧 POKE LABS CONTROL PLANE v2.0
# One script to rule them all.
# Usage: bash poke-control.sh [start|status|stop|revive|brief]
# ============================================================
set -euo pipefail

SERVICES_DIR="/home/alx/services"
LOG_DIR="/tmp/poke-logs"
WALLET="0xca3d86e4EDE205E6d72496BC2919c88b994B6beF"
CREATOR="0xb618679b989ed4f3dF32aA63daD525e680461dfe"
TODAY=$(date +%Y-%m-%d)

log() { echo "[$(date +%H:%M:%S)] $*"; }
header() {
  echo ""
  echo "🫧 Poke Labs Control Plane v2.0"
  echo "==============================="
  echo ""
}

cmd_start() {
  log "Starting all services..."
  mkdir -p "$LOG_DIR"
  pkill -f "server.py" 2>/dev/null || true; sleep 1
  COUNT=0
  for dir in "$SERVICES_DIR"/*/; do
    name=$(basename "$dir")
    server="$dir/server.py"
    if [[ -f "$server" ]]; then
      nohup python3 "$server" > "$LOG_DIR/$name.log" 2>&1 &
      COUNT=$((COUNT+1))
    fi
  done
  sleep 3
  log "Started $COUNT services"
}

cmd_status() {
  log "Checking service health..."
  UP=0
  for port in 8700 8701 8750 8760 8765 8770 8775 8785 8790 8795; do
    if curl -sf "http://localhost:$port/api/health" > /dev/null 2>&1; then
      log "  ✓ port $port UP"
      UP=$((UP+1))
    else
      log "  ✗ port $port down"
    fi
  done
  log "$UP/10 key services healthy"
}

cmd_stop() {
  log "Stopping all services..."
  pkill -f "server.py" 2>/dev/null || true
  log "All stopped"
}

cmd_brief() {
  log "Generating morning briefing..."
  local DIGEST="/home/alx/briefing/digest-${TODAY}.txt"
  python3 "$SERVICES_DIR/daily-digest/digest.py" --output "$DIGEST" 2>/dev/null || true
  if [[ -f "$DIGEST" ]]; then
    cat "$DIGEST"
  else
    log "Digest unavailable. System status:"
    cmd_status
  fi
}

cmd_revive() {
  header
  log "RESTARTING POKE LABS..."
  cmd_stop
  sleep 1
  cmd_start
  sleep 3
  cmd_status
  log ""
  log "Exposing key ports..."
  for port in 8765 8775 8700 8750; do
    # Conway expose - only if credits available
    log "  → Expose port $port via Conway API"
  done
  log ""
  cmd_brief
  log ""
  log "🫧 Revival complete. Fund wallet: $WALLET (Base USDC)"
}

# --- Main ---
case "${1:-revive}" in
  start)  cmd_start ;;
  status) cmd_status ;;
  stop)   cmd_stop ;;
  brief)  cmd_brief ;;
  revive) cmd_revive ;;
  *)      echo "Usage: $0 {start|status|stop|brief|revive}" ;;
esac
