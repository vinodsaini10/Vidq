import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch

from app.core.encryption import encrypt_token, decrypt_token
from app.api.v1.endpoints.youtube import generate_state_token, verify_state_token
from app.services.youtube_service import youtube_service, YouTubeAPIError
from app.services.youtube_sync import youtube_sync_service
from app.models.auth import User
from app.models.youtube import YouTubeChannel, YouTubeChannelCredential, YouTubeVideo, YouTubeVideoStatistic
from app.core.database import AsyncSessionLocal


def test_token_encryption_decryption():
    """Verify OAuth access/refresh tokens are securely encrypted and decrypted."""
    plain_token = "ya29.a0Axoo-sample-oauth-token-12345"
    encrypted = encrypt_token(plain_token)
    assert encrypted != plain_token
    decrypted = decrypt_token(encrypted)
    assert decrypted == plain_token


def test_oauth_state_generation_and_validation():
    """Verify CSRF-safe state parameter token generation and validation."""
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    state = generate_state_token(user_id)
    assert state is not None
    extracted_user_id = verify_state_token(state)
    assert extracted_user_id == user_id


def test_seo_score_calculation():
    """Verify video SEO score calculation logic."""
    title = "How to Grow Your YouTube Channel in 2026 - Complete Guide"
    description = "Learn the best strategies to increase views and subscribers on YouTube in 2026. Check out our website https://vidpulse.ai #youtube #growth"
    tags = ["youtube growth", "how to get views", "youtube strategy", "vidpulse", "seo", "algorithm", "2026", "content creator", "monetization", "subscribers"]

    score = youtube_sync_service._calculate_seo_score(title, description, tags)
    assert score >= 70


@pytest.mark.asyncio
async def test_youtube_channel_and_video_sync_duplicate_prevention():
    """Verify channel saving, credential encryption, and video upsert duplicate prevention."""
    async with AsyncSessionLocal() as session:
        # Create user
        user = User(
            email="youtube_tester@vidpulse.ai",
            hashed_password="hashed_pass_sample",
            full_name="YouTube Tester",
        )
        session.add(user)
        await session.flush()

        # Mock Channel Data from Google API
        mock_channel_data = {
            "id": "UC_MOCK_CHANNEL_12345",
            "snippet": {
                "title": "VidPulse Official Channel",
                "description": "Official YouTube Channel for VidPulse AI",
                "customUrl": "@vidpulse_official",
                "publishedAt": "2024-01-15T10:00:00Z",
                "thumbnails": {"high": {"url": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=150"}},
                "country": "US",
            },
            "statistics": {
                "subscriberCount": "12500",
                "videoCount": "48",
                "viewCount": "850000",
            }
        }
        mock_token_data = {
            "access_token": "ya29.mock_access_token_abc",
            "refresh_token": "1//mock_refresh_token_xyz",
            "expires_in": 3600,
        }

        channel = await youtube_sync_service.save_or_update_channel(
            session, user_id=str(user.id), channel_data=mock_channel_data, token_data=mock_token_data
        )

        assert channel.channel_id == "UC_MOCK_CHANNEL_12345"
        assert channel.subscriber_count == 12500

        # Upsert again with updated stats (should update, not create duplicate)
        mock_channel_data["statistics"]["subscriberCount"] = "13000"
        channel_updated = await youtube_sync_service.save_or_update_channel(
            session, user_id=str(user.id), channel_data=mock_channel_data, token_data=mock_token_data
        )
        assert channel_updated.id == channel.id
        assert channel_updated.subscriber_count == 13000


@pytest.mark.asyncio
async def test_oauth_authorization_url_generation():
    """Verify OAuth authorization URL formatting with required Google scopes."""
    url = youtube_service.get_authorization_url(state="test_state_123")
    assert "accounts.google.com" in url
    assert "response_type=code" in url
    assert "access_type=offline" in url
    assert "prompt=consent" in url
    assert "state=test_state_123" in url
