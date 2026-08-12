#!/usr/bin/env bash
# =====================================================================
# VidPulse Automated Backup Integrity & Restoration Test
# Restores backup to a temporary test DB and verifies schema/counts
# =====================================================================

set -eo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"
TEST_DB_NAME="vidpulse_restore_test_$(date +"%s")"
DB_USER="${POSTGRES_USER:-vidpulse_user}"
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"

LATEST_BACKUP=$(find "$BACKUP_DIR" -type f -name "vidpulse_backup_*.sql.gz" | sort -r | head -n 1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "[INFO] No compressed backups found in '$BACKUP_DIR'. Generating an on-demand test backup..."
    bash scripts/backup-db.sh
    LATEST_BACKUP=$(find "$BACKUP_DIR" -type f -name "vidpulse_backup_*.sql.gz" | sort -r | head -n 1)
fi

echo "[$(date -u)] Validating latest backup file: ${LATEST_BACKUP}"

# Step 1: Check gzip archive integrity
if ! gzip -t "$LATEST_BACKUP"; then
    echo "[FATAL] Backup file corrupt! gzip test failed." >&2
    exit 1
fi
echo "[SUCCESS] Archive structure verified."

# Step 2: Create temporary test DB
echo "[$(date -u)] Provisioning temporary test database '${TEST_DB_NAME}'..."
PGPASSWORD="${POSTGRES_PASSWORD}" createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$TEST_DB_NAME"

cleanup() {
    echo "[$(date -u)] Cleaning up test database '${TEST_DB_NAME}'..."
    PGPASSWORD="${POSTGRES_PASSWORD}" dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" --if-exists "$TEST_DB_NAME" || true
}
trap cleanup EXIT

# Step 3: Restore to test DB
echo "[$(date -u)] Restoring backup to test database..."
gunzip -c "$LATEST_BACKUP" | PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB_NAME" > /dev/null

# Step 4: Run table count assertion
TABLE_COUNT=$(PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$TEST_DB_NAME" -t -c \
  "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")

echo "[$(date -u)] Test database contains ${TABLE_COUNT//[[:space:]]/} public tables."

if [ "${TABLE_COUNT//[[:space:]]/}" -lt 5 ]; then
    echo "[FATAL] Restored database table count is lower than expected schema baseline!" >&2
    exit 1
fi

echo "================================================================="
echo "[VERIFIED] Backup integrity and restoration test PASSED!"
echo "================================================================="
