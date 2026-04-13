#!/bin/bash
# ═══════════════════════════════════════════════════════
# Clarion — Start Local Development Environment
# ═══════════════════════════════════════════════════════

set -e
cd "$(dirname "$0")/.."

echo "═══════════════════════════════════════════════════════"
echo "  Clarion — Starting Local Environment"
echo "═══════════════════════════════════════════════════════"

# Check Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Start Docker Desktop first."
    exit 1
fi

# Check .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Copy .env.example to .env and configure."
    exit 1
fi

echo ""
echo "→ Building and starting containers..."
docker compose up -d --build

echo ""
echo "→ Waiting for services..."
sleep 5

# Health check
echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Service Status"
echo "═══════════════════════════════════════════════════════"

check() {
    if docker ps --format '{{.Status}}' --filter "name=$1" | grep -q "Up"; then
        echo "  ✅ $1"
    else
        echo "  ❌ $1"
    fi
}

check clarion-db
check clarion-redis
check clarion-api
check clarion-frontend

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  Access Points"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  Frontend:   https://localhost"
echo "              (accept the self-signed certificate warning)"
echo ""
echo "  API Docs:   http://localhost:8000/api/docs"
echo "  API Health: http://localhost:8000/api/v1/health"
echo ""
echo "  Login:      demo@hexagon.com / Clarion2026!"
echo ""
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  Logs:   docker compose logs -f clarion-api"
echo "  Stop:   docker compose down"
echo "  Reset:  docker compose down -v"
echo ""
