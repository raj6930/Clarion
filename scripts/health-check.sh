#!/bin/bash
# Quick health check for all Clarion services
set -e

API_URL="${1:-http://localhost:8000}"

echo "Clarion Health Check"
echo "═══════════════════════════════════════"

# API
echo -n "API:      "
if curl -sf "${API_URL}/api/v1/health" > /dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Unreachable"
fi

# PostgreSQL
echo -n "Database: "
if docker exec clarion-db pg_isready > /dev/null 2>&1; then
    echo "✅ Connected"
else
    echo "❌ Down"
fi

# Redis
echo -n "Redis:    "
if docker exec clarion-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Connected"
else
    echo "❌ Down"
fi

# Ollama
echo -n "Ollama:   "
if curl -sf "http://localhost:11434/api/tags" > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "⚠️  Not running (local AI unavailable)"
fi

# Frontend
echo -n "Frontend: "
if curl -sf "http://localhost:3000" > /dev/null 2>&1; then
    echo "✅ Serving"
else
    echo "⚠️  Not running"
fi

echo "═══════════════════════════════════════"
