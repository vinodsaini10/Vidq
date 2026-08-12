#!/usr/bin/env bash
# =====================================================================
# VidPulse Automated Production Database Backup Script
# Performs compressed pg_dump with backup retention enforcement
# =====================================================================

set -eo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_USER="${POSTGRES_USER:-vidpulse_user}"
DB_NAME="${POSTGRES_DB:-vidpulse_db}"
DB_HOST="${POSTGRES_HOST:-postgres}"
DB_PORT="${POSTGRES_PORT:-5432}"

mkdir -p "$BACKUP_DIR"

BACKUP_FILE="${BACKUP_DIR}/vidpulse_backup_${TIMESTAMP}.sql.gz"

echo "[$(date -u)] Starting database backup for database '${DB_NAME}'..."

if PGPASSWORD="${POSTGRES_PASSWORD}" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -F c | gzip > "$BACKUP_FILE"; then
    echo "[$(date -u)] Database backup successfully created: ${BACKUP_FILE}"
    echo "[$(date -u)] Backup file size: $(du -sh "$BACKUP_FILE" | cut -f1)"
else
    echo "[ERROR] Database backup failed!" >&2
    exit 1
fi

# Cleanup old backups past retention threshold
echo "[$(date -u)] Cleaning up backups older than ${RETENTION_DAYS} days..."
find "$BACKUP_DIR" -type f -name "vidpulse_backup_*.sql.gz" -mtime +"$RETENTION_DAYS" -exec rm -f {} \;

echo "[$(date -u)] Database backup pipeline completed successfully."
