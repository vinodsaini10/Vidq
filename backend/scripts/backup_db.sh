#!/usr/bin/env bash
set -e

# PostgreSQL Backup Script for VidPulse AI Platform
POSTGRES_USER=${POSTGRES_USER:-postgres}
POSTGRES_DB=${POSTGRES_DB:-vidpulse_db}
POSTGRES_HOST=${POSTGRES_SERVER:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5432}

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="./backups"
BACKUP_FILE="${BACKUP_DIR}/vidpulse_dump_${TIMESTAMP}.sql.gz"

mkdir -p ${BACKUP_DIR}

echo "[VidPulse DB Backup] Starting database dump for ${POSTGRES_DB} at ${TIMESTAMP}..."

PGPASSWORD=${POSTGRES_PASSWORD:-postgres} pg_dump -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -U ${POSTGRES_USER} -F c -b -v -f ${BACKUP_FILE} ${POSTGRES_DB}

echo "[VidPulse DB Backup] Backup completed successfully: ${BACKUP_FILE}"
