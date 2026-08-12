#!/usr/bin/env bash
# =====================================================================
# VidPulse Production Database Restore Script
# Restores compressed pg_dump snapshot to PostgreSQL instance
# =====================================================================

set -eo pipefail

if [ -z "$1" ]; then
    echo "Usage: $0 <path_to_backup_file.sql.gz>"
    exit 1
fi

BACKUP_FILE="$1"
DB_USER="${POSTGRES_USER:-vidpulse_user}"
DB_NAME="${POSTGRES_DB:-vidpulse_db}"
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "[ERROR] Backup file '$BACKUP_FILE' does not exist." >&2
    exit 1
fi

echo "[WARNING] Re-creating database '${DB_NAME}' from backup '${BACKUP_FILE}'."
read -p "Are you sure you want to proceed with database restore? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Database restore cancelled."
    exit 0
fi

echo "[$(date -u)] Terminating active connections to '${DB_NAME}'..."
PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();" || true

echo "[$(date -u)] Dropping and re-creating database '${DB_NAME}'..."
PGPASSWORD="${POSTGRES_PASSWORD}" dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" --if-exists "$DB_NAME"
PGPASSWORD="${POSTGRES_PASSWORD}" createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME"

echo "[$(date -u)] Restoring database from archive..."
gunzip -c "$BACKUP_FILE" | PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME"

echo "[$(date -u)] Database restore completed successfully."
