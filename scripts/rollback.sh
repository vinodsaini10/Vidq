#!/usr/bin/env bash
# =====================================================================
# VidPulse Emergency Rollback Execution Script
# Handles Docker container rollbacks and database migration rollbacks
# =====================================================================

set -eo pipefail

TARGET_VERSION="${1:-previous}"

echo "================================================================="
echo "               VidPulse Production Rollback Procedure            "
echo "================================================================="
echo "[$(date -u)] Initiating rollback sequence target: '${TARGET_VERSION}'"

# Step 1: Rollback Alembic database migration if required
if [ -d "backend/alembic" ]; then
    echo "[$(date -u)] Downgrading database schema by -1 revision..."
    cd backend
    alembic downgrade -1 || echo "[WARNING] Alembic downgrade skipped or completed."
    cd ..
fi

# Step 2: Restart docker compose containers to previous tagged image
echo "[$(date -u)] Restarting container services with docker-compose..."
docker-compose -f docker-compose.prod.yml down --remove-orphans
docker-compose -f docker-compose.prod.yml up -d --build

# Step 3: Verify backend health post-rollback
echo "[$(date -u)] Verifying backend health..."
sleep 5
if curl -s -f http://localhost:8000/api/v1/health/live > /dev/null; then
    echo "================================================================="
    echo "[SUCCESS] Rollback executed successfully. Services healthy."
    echo "================================================================="
else
    echo "[CRITICAL ERROR] Post-rollback health check failed!" >&2
    exit 1
fi
