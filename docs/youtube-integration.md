# VidPulse AI - Production YouTube Integration Documentation

## 1. Overview & Architecture
VidPulse AI provides a complete, production-ready integration with the official **Google OAuth 2.0**, **YouTube Data API v3**, and **YouTube Analytics API v2**. 

### Core Features
- **Secure Multi-Channel Google OAuth 2.0**: Allows authenticated users to securely connect one or multiple YouTube channels.
- **Encrypted Credential Storage**: All access and refresh tokens are encrypted at rest using Fernet / AES key derivation.
- **Automated Data Synchronization**: Dual-layer sync pipeline (synchronous on-demand + background Celery tasks with Redis) for channel metadata, uploads, statistics, playlists, comments, and official analytics.
- **Quota-Aware Architecture**: Built-in exponential backoff, request batching, and Redis caching to prevent quota depletion.
- **Public Competitor Tracking**: Public channel analysis using official public API endpoints without requiring competitor private access.

---

## 2. Google Cloud Setup Step-by-Step Guide

### Step 1: Create a Google Cloud Project
1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click on the project dropdown at the top bar and select **New Project**.
3. Name your project (e.g. `vidpulse-ai-prod`) and click **Create**.

### Step 2: Enable Required APIs
1. In the left navigation menu, select **APIs & Services > Library**.
2. Search for **YouTube Data API v3** and click **Enable**.
3. Search for **YouTube Analytics API** and click **Enable**.

### Step 3: Configure OAuth Consent Screen
1. Go to **APIs & Services > OAuth consent screen**.
2. Select User Type (**External** or **Internal** for Workspace organizations).
3. Fill in App Details:
   - **App name**: `VidPulse AI`
   - **User support email**: `support@vidpulse.ai`
   - **Developer contact information**: `admin@vidpulse.ai`
4. Add Authorized Scopes:
   - `https://www.googleapis.com/auth/youtube.readonly`
   - `https://www.googleapis.com/auth/yt-analytics.readonly`
   - `https://www.googleapis.com/auth/yt-analytics-monetary.readonly`
   - `https://www.googleapis.com/auth/youtube.force-ssl`
5. Save and proceed to Summary.

### Step 4: Create OAuth 2.0 Credentials
1. Go to **APIs & Services > Credentials**.
2. Click **Create Credentials > OAuth client ID**.
3. Select **Web application** as Application type.
4. Set Name: `VidPulse Web Client`.
5. Add **Authorized JavaScript origins**:
   - `http://localhost:3000`
   - `https://your-production-domain.com`
6. Add **Authorized redirect URIs**:
   - `http://localhost:3000/api/v1/youtube/oauth/callback`
   - `https://your-production-domain.com/api/v1/youtube/oauth/callback`
7. Click **Create** and safely copy your `Client ID` and `Client Secret`.

### Step 5: Configure Environment Variables
Copy these values into your `.env` configuration file:

```env
GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your-client-secret"
GOOGLE_REDIRECT_URI="http://localhost:3000/api/v1/youtube/oauth/callback"
YOUTUBE_API_KEY="your-api-key"
GOOGLE_PROJECT_ID="your-google-cloud-project-id"
```

---

## 3. Security Architecture

### Token Encryption at Rest
OAuth access tokens and refresh tokens are encrypted using 256-bit Fernet encryption derived from `SECRET_KEY` before storing in `youtube_channel_credentials`:

```python
from app.core.encryption import encrypt_token, decrypt_token

# Encrypt before saving:
encrypted_token = encrypt_token(plain_token)

# Decrypt when calling API:
plain_token = decrypt_token(encrypted_token)
```

### CSRF Protection & State Parameter
The OAuth flow generates a signed JWT state token containing a user ID, timestamp, and random nonce:
- **Lifetime**: 15 minutes
- **Validation**: Strict verification on `/api/v1/youtube/oauth/callback` prevents state replay and CSRF attacks.

---

## 4. API Endpoints Reference

All endpoints return responses in standard JSON format:

```json
{
  "success": true,
  "data": {},
  "meta": {},
  "error": null
}
```

### Endpoints List
- `GET /api/v1/youtube/connect`: Initiate Google OAuth connection URL.
- `GET /api/v1/youtube/oauth/callback`: OAuth callback handler.
- `GET /api/v1/youtube/channels`: List connected YouTube channels.
- `GET /api/v1/youtube/channels/{channel_id}`: Get channel details.
- `POST /api/v1/youtube/channels/{channel_id}/sync`: Trigger manual sync.
- `POST /api/v1/youtube/channels/{channel_id}/refresh`: Refresh OAuth token.
- `DELETE /api/v1/youtube/channels/{channel_id}`: Revoke OAuth token and disconnect.
- `GET /api/v1/youtube/channels/{channel_id}/videos`: List channel videos with pagination.
- `GET /api/v1/youtube/channels/{channel_id}/playlists`: List playlists.
- `GET /api/v1/youtube/channels/{channel_id}/analytics`: Fetch channel analytics.
- `GET /api/v1/youtube/channels/compare`: Channel comparison.
- `GET /api/v1/youtube/videos/{video_id}`: Video details & SEO score.
- `GET /api/v1/youtube/videos/{video_id}/analytics`: Video performance analytics.
- `GET /api/v1/youtube/videos/{video_id}/comments`: Video comments list.
- `GET /api/v1/youtube/search`: Public YouTube search.
- `GET /api/v1/youtube/competitors`: List tracked competitor channels.
- `POST /api/v1/youtube/competitors`: Add public competitor channel.
- `DELETE /api/v1/youtube/competitors/{id}`: Remove competitor channel.

---

## 5. Background Jobs (Celery + Redis)

Background synchronization tasks are handled via Celery workers in `app.tasks.youtube_tasks`:
1. `sync_channel(channel_id, user_id)`: Complete sync of metadata, videos, and analytics.
2. `refresh_expired_oauth_tokens()`: Scheduled cron job that automatically refreshes OAuth tokens expiring in the next 10 minutes.
3. `sync_competitors(user_id)`: Periodic update of public competitor statistics.

---

## 6. Troubleshooting & Common Issues

| Issue | Cause | Resolution |
|---|---|---|
| `redirect_uri_mismatch` | Google OAuth Client settings do not match `GOOGLE_REDIRECT_URI` | Ensure `http://localhost:3000/api/v1/youtube/oauth/callback` is added under Authorized redirect URIs in Google Cloud Console. |
| `YOUTUBE_QUOTA_EXCEEDED` | Exceeded 10,000 daily quota units | Enable Redis caching, reduce manual sync frequency, or request quota increase in Google Cloud Console. |
| `UNAUTHORIZED_ACCESS_TOKEN` | Token expired or revoked by user | Call `POST /api/v1/youtube/channels/{channel_id}/refresh` or reconnect the channel. |
