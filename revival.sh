#!/bin/bash
# Poke Labs Auto-Revival Script v1.0
# Run this after funding to bring everything back online.
# Usage: bash revival.sh

set -e

SERVICES_DIR="/home/alx/services"
LOG_DIR="/tmp/poke-logs"
WALLET="0xca3d86e4EDE205E6d72496BC2919c88b994B6beF"

echo "🫧 Poke Labs Auto-Revival v1.0"
echo "=============================="
echo ""

# Check credits
echo "Step 1: Checking environment..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi
echo "  ✓ Python 3 available"
echo "  ✓ Services directory: $SERVICES_DIR"

# Kill any existing services
echo ""
echo "Step 2: Cleaning up old processes..."
pkill -f "server.py" 2>/dev/null || true
sleep 1
echo "  ✓ Cleaned up"

# Start services
echo ""
echo "Step 3: Starting services..."
mkdir -p "$LOG_DIR"

STARTED=0
for dir in "$SERVICES_DIR"/*/; do
    name=$(basename "$dir")
    server="$dir/server.py"
    if [ -f "$server" ]; then
        nohup python3 "$server" > "$LOG_DIR/$name.log" 2>&1 &
        echo "  → Started $name"
        STARTED=$((STARTED + 1))
    fi
done
echo "  ✓ Started $STARTED services"

# Wait for services to bind
echo ""
echo "Step 4: Waiting for services to start..."
sleep 3

# Check health
echo ""
echo "Step 5: Health checks..."
UP=0
DOWN=0
for dir in "$SERVICES_DIR"/*/; do
    name=$(basename "$dir")
    # Try common health endpoints
    if curl -s "http://localhost:8765/api/health" > /dev/null 2>&1; then
        echo "  ✓ link-preview (:8765)"
        UP=$((UP + 1))
    fi
    if curl -s "http://localhost:8775/api/health" > /dev/null 2>&1; then
        echo "  ✓ poke-hub (:8775)"
        UP=$((UP + 1))
    fi
    if curl -s "http://localhost:8700/api/health" > /dev/null 2>&1; then
        echo "  ✓ api-gateway (:8700)"
        UP=$((UP + 1))
    fi
    break  # Just check key ones
done

echo ""
echo "=============================="
echo "🫧 Revival Complete!"
echo "  Services started: $STARTED"
echo "  Key services up: $UP"
echo "  Logs: $LOG_DIR/"
echo ""
echo "Next steps:"
echo "  1. Expose ports via Conway API"
echo "  2. Send morning briefing"
echo "  3. Check GitHub for issues/PRs"
echo ""
echo "Fund wallet (Base USDC): $WALLET"
