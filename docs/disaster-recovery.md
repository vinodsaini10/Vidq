# VidPulse SaaS Platform - Disaster Recovery & Backup Runbook

**Version:** 1.0.0  
**Effective Date:** August 2026  
**RPO Target (Recovery Point Objective):** < 1 Hour  
**RTO Target (Recovery Time Objective):** < 30 Minutes  

---

## 1. Overview & Data Loss Mitigation

VidPulse maintains automated database backups, database replication, state snapshotting, and container image registries to ensure high availability and near-zero data loss during infrastructure outages.

---

## 2. Backup Schedules & Retention Policy

| Backup Type | Frequency | Execution Window | Retention Period | Storage Location |
| :--- | :--- | :--- | :--- | :--- |
| **Full DB Backup** | Daily | 02:00 UTC | 30 Days | Compressed S3/GCS Object Store |
| **Hourly Snapshot** | Hourly | Every 60 Mins | 48 Hours | Local Docker Volume & Cloud Storage |
| **WAL Archiving** | Continuous | Real-time | 7 Days | Cloud Storage WAL Archive |

---

## 3. Disaster Scenarios & Response Procedures

### Scenario A: PostgreSQL Database Corruption or Outage
1. **Isolate Database Traffic:** Direct Nginx to present maintenance mode if necessary.
2. **Retrieve Latest Verified Backup:**
   ```bash
   bash scripts/test-restore.sh
   ```
3. **Restore Database:**
   ```bash
   bash scripts/restore-db.sh /backups/postgres/vidpulse_backup_LATEST.sql.gz
   ```
4. **Apply Unapplied Migrations:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
   ```

### Scenario B: Failed Application Deployment
1. Execute emergency rollback script:
   ```bash
   bash scripts/rollback.sh
   ```
2. Verify system liveness:
   ```bash
   curl -i http://localhost:8000/api/v1/health/live
   ```

---

## 4. Disaster Recovery Testing
Restoration tests run automatically on every Sunday at 03:00 UTC via `scripts/test-restore.sh` to guarantee backup integrity and verify zero data corruption.
