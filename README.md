# VidPulse - Production AI Creator SaaS Platform

[![CI Test Suite](https://github.com/vidpulse/vidpulse/actions/workflows/test.yml/badge.svg)](https.github.com/vidpulse/vidpulse/actions)
[![Security Scan](https://github.com/vidpulse/vidpulse/actions/workflows/security.yml/badge.svg)](https.github.com/vidpulse/vidpulse/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

VidPulse is an enterprise-grade YouTube Creator SaaS application featuring real-time YouTube channel synchronization, AI-powered title & script generation, SEO keyword research, competitor tracking, automated billing (Stripe & Razorpay), and a full Platform Super Admin Console.

---

## Architecture Stack

- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons, Recharts
- **Backend:** FastAPI, Python 3.11, Async SQLAlchemy, Pydantic, Gunicorn/Uvicorn
- **Database:** PostgreSQL 15, Alembic Migrations
- **Cache & Workers:** Redis 7, Celery Worker & Beat Scheduler
- **Reverse Proxy:** Nginx with TLS, Rate Limiting, & Security Headers
- **Observability:** Prometheus Metrics, Structured JSON Logging
- **Integrations:** Google/YouTube OAuth2, YouTube Data API v3, Google Gemini, OpenAI, Ollama, Stripe, Razorpay

---

## Quick Start (Production Setup)

### 1. Clone & Configure Environment
```bash
git clone https://github.com/vidpulse/vidpulse.git
cd vidpulse

# Copy production environment template
cp .env.example backend/.env
# Edit backend/.env with your production API keys and database credentials
```

### 2. Launch Stack via Docker Compose
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### 3. Run Database Migrations
```bash
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

## Health Checks & Monitoring

VidPulse exposes granular health probes for container orchestrators and monitoring agents:

- **Liveness Probe:** `GET /api/v1/health/live`
- **Readiness Probe:** `GET /api/v1/health/ready`
- **System Health:** `GET /api/v1/health`
- **Database Status:** `GET /api/v1/health/database`
- **Redis Status:** `GET /api/v1/health/redis`
- **Prometheus Metrics:** `GET /api/v1/health/metrics`

---

## Automated Backups & Disaster Recovery

- **Database Backup:**
  ```bash
  bash scripts/backup-db.sh
  ```
- **Database Restore:**
  ```bash
  bash scripts/restore-db.sh /backups/postgres/vidpulse_backup_YYYYMMDD.sql.gz
  ```
- **Automated Backup Restoration Test:**
  ```bash
  bash scripts/test-restore.sh
  ```
- **Emergency Rollback:**
  ```bash
  bash scripts/rollback.sh
  ```

---

## Documentation Index

- [Production Audit Report](docs/production-audit.md)
- [Disaster Recovery Runbook](docs/disaster-recovery.md)
- [Production Deployment Checklist](docs/production-checklist.md)
- [Billing Architecture](docs/billing.md)
- [YouTube Integration Guide](docs/youtube-integration.md)
- [Database Schema & ERD](docs/database-er.md)
