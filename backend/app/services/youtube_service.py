import logging
import json
import time
import httpx
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlencode

from app.core.config import settings
from app.core.encryption import encrypt_token, decrypt_token
from app.core.redis import get_redis

logger = logging.getLogger("youtube_service")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
YOUTUBE_DATA_API_BASE = "https://www.googleapis.com/youtube/v3"
YOUTUBE_ANALYTICS_API_BASE = "https://youtubeanalytics.googleapis.com/v2/reports"


class YouTubeAPIError(Exception):
    def __init__(self, message: str, code: str = "YOUTUBE_API_ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class YouTubeService:
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.api_key = settings.YOUTUBE_API_KEY
        self.scopes = settings.GOOGLE_OAUTH_SCOPES

    # ------------------------------------------------------------------
    # OAuth 2.0 Flow
    # ------------------------------------------------------------------
    def get_authorization_url(self, state: str) -> str:
        """Generate Google OAuth 2.0 Authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
            "include_granted_scopes": "true",
        }
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens."""
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(GOOGLE_TOKEN_URL, data=data)
            if resp.status_code != 200:
                logger.error(f"Failed to exchange code: {resp.text}")
                err_data = resp.json() if resp.headers.get("content-type") == "application/json" else {}
                err_msg = err_data.get("error_description") or err_data.get("error") or "Failed to exchange OAuth code."
                raise YouTubeAPIError(err_msg, code="OAUTH_EXCHANGE_FAILED", status_code=resp.status_code)
            return resp.json()

    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh expired access token using refresh_token."""
        plain_refresh_token = decrypt_token(refresh_token)
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": plain_refresh_token,
            "grant_type": "refresh_token",
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(GOOGLE_TOKEN_URL, data=data)
            if resp.status_code != 200:
                logger.error(f"Failed to refresh access token: {resp.text}")
                raise YouTubeAPIError("OAuth refresh token is invalid or revoked.", code="TOKEN_REFRESH_FAILED", status_code=401)
            return resp.json()

    async def revoke_token(self, token: str) -> bool:
        """Revoke Google OAuth token."""
        plain_token = decrypt_token(token)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(GOOGLE_REVOKE_URL, params={"token": plain_token})
            return resp.status_code == 200

    # ------------------------------------------------------------------
    # Data API v3 Helpers
    # ------------------------------------------------------------------
    async def _make_api_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        access_token: Optional[str] = None,
        use_api_key_fallback: bool = True,
    ) -> Dict[str, Any]:
        """Helper to make authenticated YouTube Data API requests with caching & error handling."""
        headers = {}
        plain_access_token = decrypt_token(access_token) if access_token else None

        if plain_access_token:
            headers["Authorization"] = f"Bearer {plain_access_token}"
        elif use_api_key_fallback and self.api_key:
            params["key"] = self.api_key

        url = f"{YOUTUBE_DATA_API_BASE}/{endpoint}"

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            
            if resp.status_code == 429 or "quotaExceeded" in resp.text:
                raise YouTubeAPIError("YouTube API quota exceeded. Please try again later.", code="YOUTUBE_QUOTA_EXCEEDED", status_code=429)
            elif resp.status_code == 401:
                raise YouTubeAPIError("Invalid or expired OAuth access token.", code="UNAUTHORIZED_ACCESS_TOKEN", status_code=401)
            elif resp.status_code != 200:
                logger.error(f"YouTube API Error [{resp.status_code}]: {resp.text}")
                err_data = resp.json() if "json" in resp.headers.get("content-type", "") else {}
                err_message = err_data.get("error", {}).get("message", "YouTube API error")
                raise YouTubeAPIError(err_message, code="YOUTUBE_API_ERROR", status_code=resp.status_code)

            return resp.json()

    # ------------------------------------------------------------------
    # Authenticated Channel Info
    # ------------------------------------------------------------------
    async def get_authenticated_channel(self, access_token: str) -> Dict[str, Any]:
        """Fetch primary YouTube channel owned by authenticated user."""
        params = {
            "part": "snippet,contentDetails,statistics,brandingSettings,status",
            "mine": "true",
        }
        data = await self._make_api_request("channels", params, access_token=access_token)
        items = data.get("items", [])
        if not items:
            raise YouTubeAPIError("No YouTube channel found for this Google account.", code="NO_CHANNEL_FOUND", status_code=404)
        return items[0]

    async def get_channel_by_id(self, channel_id: str, access_token: Optional[str] = None) -> Dict[str, Any]:
        """Fetch YouTube channel details by channel ID."""
        params = {
            "part": "snippet,contentDetails,statistics,brandingSettings,status",
            "id": channel_id,
        }
        data = await self._make_api_request("channels", params, access_token=access_token, use_api_key_fallback=True)
        items = data.get("items", [])
        if not items:
            raise YouTubeAPIError(f"Channel {channel_id} not found.", code="CHANNEL_NOT_FOUND", status_code=404)
        return items[0]

    # ------------------------------------------------------------------
    # Videos & Uploads
    # ------------------------------------------------------------------
    async def get_channel_videos(
        self,
        uploads_playlist_id: str,
        max_results: int = 50,
        page_token: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Get video items from channel uploads playlist."""
        params: Dict[str, Any] = {
            "part": "snippet,contentDetails,status",
            "playlistId": uploads_playlist_id,
            "maxResults": min(max_results, 50),
        }
        if page_token:
            params["pageToken"] = page_token

        data = await self._make_api_request("playlistItems", params, access_token=access_token)
        items = data.get("items", [])
        next_page_token = data.get("nextPageToken")
        return items, next_page_token

    async def get_video_details(
        self,
        video_ids: List[str],
        access_token: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch rich details and statistics for video IDs (up to 50 at a time)."""
        if not video_ids:
            return []

        params = {
            "part": "snippet,contentDetails,statistics,status,topicDetails",
            "id": ",".join(video_ids[:50]),
        }
        data = await self._make_api_request("videos", params, access_token=access_token)
        return data.get("items", [])

    # ------------------------------------------------------------------
    # Playlists & Comments
    # ------------------------------------------------------------------
    async def get_channel_playlists(
        self,
        channel_id: str,
        max_results: int = 50,
        page_token: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Fetch playlists for a channel."""
        params: Dict[str, Any] = {
            "part": "snippet,contentDetails,status",
            "channelId": channel_id,
            "maxResults": min(max_results, 50),
        }
        if page_token:
            params["pageToken"] = page_token

        data = await self._make_api_request("playlists", params, access_token=access_token)
        return data.get("items", []), data.get("nextPageToken")

    async def get_video_comments(
        self,
        video_id: str,
        max_results: int = 50,
        page_token: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Fetch comment threads for a video."""
        params: Dict[str, Any] = {
            "part": "snippet,replies",
            "videoId": video_id,
            "maxResults": min(max_results, 100),
            "order": "relevance",
        }
        if page_token:
            params["pageToken"] = page_token

        try:
            data = await self._make_api_request("commentThreads", params, access_token=access_token)
            return data.get("items", []), data.get("nextPageToken")
        except YouTubeAPIError as e:
            if "commentsDisabled" in str(e) or e.status_code == 403:
                return [], None
            raise e

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    async def search(
        self,
        query: str,
        search_type: str = "video",
        max_results: int = 25,
        page_token: Optional[str] = None,
        access_token: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], Optional[str]]:
        """Search YouTube for videos, channels, or playlists."""
        params: Dict[str, Any] = {
            "part": "snippet",
            "q": query,
            "type": search_type,
            "maxResults": min(max_results, 50),
        }
        if page_token:
            params["pageToken"] = page_token

        data = await self._make_api_request("search", params, access_token=access_token)
        return data.get("items", []), data.get("nextPageToken")

    # ------------------------------------------------------------------
    # YouTube Analytics API v2
    # ------------------------------------------------------------------
    async def get_analytics_report(
        self,
        channel_id: str,
        access_token: str,
        start_date: str,  # YYYY-MM-DD
        end_date: str,    # YYYY-MM-DD
        metrics: str = "views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost",
        dimensions: Optional[str] = "day",
        filters: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Query official YouTube Analytics API v2."""
        plain_access_token = decrypt_token(access_token)
        headers = {"Authorization": f"Bearer {plain_access_token}"}

        params: Dict[str, Any] = {
            "ids": f"channel=={channel_id}",
            "startDate": start_date,
            "endDate": end_date,
            "metrics": metrics,
        }
        if dimensions:
            params["dimensions"] = dimensions
        if filters:
            params["filters"] = filters

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(YOUTUBE_ANALYTICS_API_BASE, params=params, headers=headers)
            if resp.status_code != 200:
                logger.warning(f"Analytics API Error [{resp.status_code}]: {resp.text}")
                # Fallback empty analytics payload if scope/monetization missing
                return {"columnHeaders": [], "rows": []}
            return resp.json()


youtube_service = YouTubeService()
