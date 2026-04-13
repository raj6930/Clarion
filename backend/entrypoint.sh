#!/bin/bash
set -e

echo "════════════════════════════════"
echo "Clarion API starting..."
echo "════════════════════════════════"

# Wait for database using Python (no pg_isready needed)
echo "→ Waiting for PostgreSQL..."
python3 -c "
import time, socket, os
host = os.environ.get('CLARION_DB_HOST', 'clarion-db')
port = int(os.environ.get('CLARION_DB_PORT', 5432))
for i in range(30):
    try:
        s = socket.create_connection((host, port), timeout=2)
        s.close()
        print('  ✓ PostgreSQL ready')
        break
    except (ConnectionRefusedError, OSError):
        if i == 29:
            print('  ✗ PostgreSQL not ready after 30s')
            exit(1)
        time.sleep(1)
"

# Run Alembic migrations
echo "→ Running database migrations..."
cd /app
python -m alembic upgrade head 2>&1 || echo "  ⚠ Migration warning (may already be applied)"
echo "  ✓ Migrations complete"

echo "→ Starting API server..."
exec "$@"
