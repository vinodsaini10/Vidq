#!/usr/bin/env bash
set -e

# PostgreSQL Database Restore Script for VidPulse AI Platform
if [ -z "$1" ]; then
  echo "Usage: ./scripts/restore_db.sh <path_to_backup_file.sql.gz>"
  exit 1
fi

BACKUP_FILE=$1
POSTGRES_USER=${POSTGRES_USER:-postgres}
POSTGRES_DB=${POSTGRES_DB:-vidpulse_db}
POSTGRES_HOST=${POSTGRES_SERVER:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5432}

echo "[VidPulse DB Restore] Restoring ${POSTGRES_DB} from ${BACKUP_FILE}..."

PGPASSWORD=${POSTGRES_PASSWORD:-postgres} pg_restore -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -U ${POSTGRES_USER} -d ${POSTGRES_DB} --clean --if-exists -v ${BACKUP_FILE}

echo "[VidPulse DB Restore] Database restoration completed successfully!"
