# Poke Labs Council — Multi-service container
# Runs all Poke Labs services in a single container
FROM python:3.12-slim

WORKDIR /app

# Install gh CLI for GitHub API calls
RUN apt-get update && apt-get install -y --no-install-recommends curl git && \
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
    dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
    tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install -y gh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy all services
COPY services/ /app/services/
COPY scripts/ /app/scripts/

# Create startup script
RUN cat > /app/start.sh << 'STARTUP'
#!/bin/bash
set -e
echo "🐾 Poke Labs Services Starting..."

# Start health dashboard in background
python3 /app/services/health-dashboard/server.py &
echo "  ✅ Health Dashboard on :8779"

# Start link preview API
python3 /app/services/link-preview/server.py &
echo "  ✅ Link Preview on :8765"

# Start poke bot
python3 /app/services/poke-bot/bot.py &
echo "  ✅ Poke Bot on :8770"

echo "🐾 All services started. Monitoring..."
tail -f /dev/null
STARTUP
RUN chmod +x /app/start.sh

EXPOSE 8765 8766 8770 8775 8777 8779 8780 8799

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8779/api/health || exit 1

CMD ["/app/start.sh"]
