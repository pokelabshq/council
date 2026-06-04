#!/bin/bash
# Health Check Monitor — checks all Council services, logs failures
# Usage: ./scripts/health-monitor.sh [--telegram]

SERVICES=(
  "gateway:8700"
  "sentiment:8764"
  "link-preview:8765"
  "keyword-extractor:8766"
  "qr-generator:8767"
  "dns-lookup:8768"
  "color-palette:8769"
  "text-summary:8770"
  "url-shortener:8771"
  "password-generator:8772"
  "timestamp-converter:8773"
  "json-formatter:8774"
  "base64-tool:8775"
  "markdown-render:8776"
  "webhook-relay:8779"
  "rate-limiter:8780"
  "status-dashboard:8778"
)

LOG_FILE="/tmp/council-health.log"
FAILURES=0
FAILED_SERVICES=""

echo "=== Council Health Check $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" >> "$LOG_FILE"

for svc in "${SERVICES[@]}"; do
  name="${svc%%:*}"
  port="${svc##*:}"
  if curl -sf "http://localhost:${port}/api/health" > /dev/null 2>&1; then
    echo "✅ ${name} (:${port}) — OK"
  else
    echo "❌ ${name} (:${port}) — DOWN"
    FAILURES=$((FAILURES + 1))
    FAILED_SERVICES="${FAILED_SERVICES} ${name}"
  fi
done

echo "--- ${FAILURES} failures ---" >> "$LOG_FILE"

if [ "$FAILURES" -gt 0 ]; then
  echo "⚠️  ${FAILURES} service(s) down:${FAILED_SERVICES}"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) FAILURES:${FAILED_SERVICES}" >> "$LOG_FILE"
  
  if [ "$1" = "--telegram" ]; then
    # Send Telegram alert (requires TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID)
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
      MSG="⚠️ Council Alert: ${FAILURES} service(s) down:${FAILED_SERVICES}"
      curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "text=${MSG}" > /dev/null
    fi
  fi
else
  echo "✅ All services healthy"
fi

exit $FAILURES
