# VidPulse AI Platform - Production Database Documentation

## 1. Overview
VidPulse AI supports **Neon Serverless PostgreSQL** and standard **PostgreSQL 17+** with `asyncpg` and **SQLAlchemy 2.x** as the primary async ORM, managed with **Alembic** migrations. All primary keys are UUIDs (`uuid_generate_v4()`), timestamps are UTC ISO-8601 with timezone, money values use fixed-precision `NUMERIC(12,2)`, and sensitive credentials/tokens are encrypted.

### 1.1 Neon Serverless PostgreSQL Configuration
To connect VidPulse AI to Neon Serverless PostgreSQL:
1. Copy your Neon connection string from the Neon Console (e.g. `postgresql://[user]:[password]@[ep-xyz].neon.tech/[dbname]?sslmode=require`).
2. Set `DATABASE_URL` in your `.env` or environment settings.
3. The application automatically normalizes `postgresql://` or `postgres://` to `postgresql+asyncpg://` and configures SSL (`ssl=require`) with pre-ping connection pooling (`pool_pre_ping=True`).

---

## 2. Core Enums
- **UserRole**: `SUPER_ADMIN`, `ADMIN`, `MANAGER`, `MODERATOR`, `SUPPORT`, `PREMIUM_USER`, `FREE_USER`
- **UserStatus**: `ACTIVE`, `INACTIVE`, `SUSPENDED`, `PENDING_VERIFICATION`
- **SubscriptionStatus**: `ACTIVE`, `TRIALING`, `PAST_DUE`, `CANCELED`, `UNPAID`, `INCOMPLETE`
- **PaymentStatus**: `PENDING`, `SUCCEEDED`, `FAILED`, `REFUNDED`
- **InvoiceStatus**: `DRAFT`, `OPEN`, `PAID`, `UNCOLLECTIBLE`, `VOID`
- **VideoStatus**: `Idea`, `Scripting`, `Filming`, `Editing`, `Scheduled`, `Published`
- **NotificationType**: `milestone`, `alert`, `ai`, `system`
- **NotificationStatus**: `UNREAD`, `READ`, `ARCHIVED`
- **AIProvider**: `GEMINI`, `OPENAI`, `CLAUDE`
- **AIRequestStatus**: `PENDING`, `SUCCESS`, `FAILED`
- **ReportStatus**: `PROCESSING`, `COMPLETED`, `FAILED`
- **TicketStatus**: `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`

---

## 3. Database Schema Domains

### 3.1 Authentication & User Management
- `users`: Core account information, role, AI credit quotas, YouTube channel link.
- `user_profiles`: Timezone, bio, company, language.
- `user_sessions` & `user_devices`: Active session tokens, user agents, push tokens.
- `audit_logs` & `security_events`: Compliance, login logs, security audit tracking.
- `oauth_accounts`, `email_verifications`, `password_reset_tokens`, `refresh_tokens`, `two_factor_settings`, `login_attempts`.

### 3.2 Subscriptions & Billing
- `plans` & `plan_features`: Pricing tiers (`Free`, `Starter`, `Pro`, `Business`, `Enterprise`), feature flags.
- `subscriptions`: Stripe customer/subscription mapping, period dates, statuses.
- `invoices`, `invoice_items`, `payments`, `payment_methods`, `refunds`, `coupons`, `coupon_redemptions`.
- `usage_limits` & `usage_records`: Per-feature quota enforcement.

### 3.3 YouTube Domain
- `youtube_channels` & `youtube_channel_credentials`: Encrypted OAuth refresh & access tokens.
- `youtube_videos`: Script body, generated titles, tags, SEO scores, CTR estimates.
- `youtube_video_statistics` & `youtube_channel_statistics`: Views, CTR, watch time, earnings.
- `youtube_comments`, `youtube_comment_analysis`, `youtube_playlists`, `youtube_thumbnails`, `youtube_live_streams`.

### 3.4 Analytics & Keyword Research
- `analytics_snapshots`, `daily_channel_metrics`, `daily_video_metrics`, `audience_metrics`, `traffic_sources`, `device_metrics`, `geography_metrics`, `retention_metrics`, `revenue_metrics`.
- `keywords`, `keyword_metrics`, `keyword_history`, `keyword_rankings`, `keyword_tracking`, `keyword_groups`, `related_keywords`, `keyword_suggestions`.

### 3.5 Video SEO & Competitors
- `seo_audits`, `seo_audit_results`, `video_seo_scores`, `title_scores`, `description_scores`, `tag_scores`, `thumbnail_scores`, `seo_recommendations`.
- `competitors`, `competitor_channels`, `competitor_videos`, `competitor_snapshots`, `competitor_metrics`, `competitor_alerts`.

### 3.6 Content Studio & AI Generation
- `content_ideas`, `content_categories`, `content_calendar_items`, `content_briefs`, `video_projects`, `video_scripts`, `video_hooks`, `video_title_options`, `video_description_options`, `video_tag_options`, `hashtags`.
- `ai_provider_models`, `ai_usage`, `ai_requests`, `ai_responses`, `ai_conversations`, `ai_messages`, `ai_prompt_templates`, `ai_generated_content`, `ai_generation_history`.

### 3.7 Reporting, Support & System Admin
- `reports`, `report_templates`, `report_schedules`, `report_deliveries`, `report_exports`.
- `notifications`, `notification_templates`, `notification_deliveries`, `notification_preferences`.
- `support_tickets`, `support_messages`, `support_attachments`.
- `admin_actions`, `feature_flags`, `system_settings`, `api_keys`, `webhook_events`, `uploaded_files`, `media_assets`.

---

## 4. Key Indexes & Constraints
- `users.email` (Unique Index)
- `subscriptions.user_id` & `subscriptions.status` (Composite Index)
- `youtube_channels.user_id` & `youtube_channels.channel_id` (Unique Index)
- `youtube_videos.channel_id` & `youtube_videos.published_at` (Indexed)
- `keywords.keyword` (Trigram / Unique Index)
- `audit_logs.user_id` & `audit_logs.created_at` (Indexed)

---

## 5. Operations & Workflows

### Running Migrations
```bash
# Upgrade database to latest revision
alembic upgrade head

# Create a new migration revision
alembic revision --autogenerate -m "Add new analytics field"
```

### Seeding Data
```bash
python -m app.database.seed
```

### Database Backup & Restore
```bash
# Backup database
./scripts/backup_db.sh

# Restore database from dump
./scripts/restore_db.sh ./backups/vidpulse_dump_20260811_000000.sql.gz
```
