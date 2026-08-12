import asyncio
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.youtube import YouTubeChannel, YouTubeChannelCredential, YouTubeVideo
from app.models.competitors import Competitor
from app.services.youtube_service import youtube_service
from app.services.youtube_sync import youtube_sync_service

logger = logging.getLogger("youtube_tasks")


def run_async(coro):
    """Utility to execute async functions inside synchronous Celery task workers."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.ensure_future(coro)
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


@celery_app.task(name="app.tasks.youtube_tasks.sync_channel", bind=True, max_retries=3, default_retry_delay=60)
def sync_channel_task(self, channel_id: str, user_id: str):
    """Celery task to sync channel profile, statistics, videos, and analytics."""
    async def _async_sync():
        async with AsyncSessionLocal() as db:
            stmt = select(YouTubeChannel).where(
                YouTubeChannel.channel_id == channel_id,
                YouTubeChannel.user_id == user_id,
            )
            res = await db.execute(stmt)
            channel = res.scalars().first()
            if not channel:
                logger.error(f"Task error: Channel {channel_id} for user {user_id} not found.")
                return False

            # Get credential
            stmt_c = select(YouTubeChannelCredential).where(YouTubeChannelCredential.channel_id == channel.id)
            res_c = await db.execute(stmt_c)
            cred = res_c.scalars().first()
            access_token = cred.encrypted_access_token if cred else None

            # Fetch fresh channel stats from Data API
            ch_data = await youtube_service.get_channel_by_id(channel.channel_id, access_token=access_token)
            stats = ch_data.get("statistics", {})
            channel.subscriber_count = int(stats.get("subscriberCount", channel.subscriber_count))
            channel.view_count = int(stats.get("viewCount", channel.view_count))
            channel.video_count = int(stats.get("videoCount", channel.video_count))
            await db.commit()

            # Sync videos & analytics
            await youtube_sync_service.sync_channel_videos(db, channel)
            await youtube_sync_service.sync_playlists(db, channel)
            await youtube_sync_service.sync_channel_analytics(db, channel, days=30)
            logger.info(f"Successfully synced channel {channel_id}")
            return True

    try:
        return run_async(_async_sync())
    except Exception as exc:
        logger.error(f"sync_channel_task failed: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(name="app.tasks.youtube_tasks.sync_channel_videos", bind=True)
def sync_channel_videos_task(self, channel_id: str):
    """Task to sync channel videos."""
    async def _async_sync():
        async with AsyncSessionLocal() as db:
            stmt = select(YouTubeChannel).where(YouTubeChannel.channel_id == channel_id)
            res = await db.execute(stmt)
            channel = res.scalars().first()
            if channel:
                return await youtube_sync_service.sync_channel_videos(db, channel)
    return run_async(_async_sync())


@celery_app.task(name="app.tasks.youtube_tasks.sync_comments", bind=True)
def sync_comments_task(self, video_id: str):
    """Task to sync comments for a video."""
    async def _async_sync():
        async with AsyncSessionLocal() as db:
            stmt = select(YouTubeVideo).where(YouTubeVideo.video_id == video_id)
            res = await db.execute(stmt)
            video = res.scalars().first()
            if video:
                # Fetch comments
                pass
    return run_async(_async_sync())


@celery_app.task(name="app.tasks.youtube_tasks.sync_analytics", bind=True)
def sync_analytics_task(self, channel_id: str, days: int = 30):
    """Task to sync channel analytics."""
    async def _async_sync():
        async with AsyncSessionLocal() as db:
            stmt = select(YouTubeChannel).where(YouTubeChannel.channel_id == channel_id)
            res = await db.execute(stmt)
            channel = res.scalars().first()
            if channel:
                return await youtube_sync_service.sync_channel_analytics(db, channel, days=days)
    return run_async(_async_sync())


@celery_app.task(name="app.tasks.youtube_tasks.sync_competitors", bind=True)
def sync_competitors_task(self, user_id: str):
    """Task to update competitor public channel metrics."""
    async def _async_sync():
        async with AsyncSessionLocal() as db:
            stmt = select(Competitor).where(Competitor.user_id == user_id)
            res = await db.execute(stmt)
            competitors = res.scalars().all()
            for comp in competitors:
                try:
                    ch_data = await youtube_service.get_channel_by_id(comp.channel_id)
                    stats = ch_data.get("statistics", {})
                    comp.subscribers = int(stats.get("subscriberCount", comp.subscribers))
                except Exception as e:
                    logger.warning(f"Could not update competitor {comp.channel_id}: {e}")
            await db.commit()
    return run_async(_async_sync())


@celery_app.task(name="app.tasks.youtube_tasks.refresh_expired_oauth_tokens")
def refresh_expired_oauth_tokens_task():
    """Background cron job to refresh OAuth access tokens expiring in the next 10 minutes."""
    async def _async_refresh():
        async with AsyncSessionLocal() as db:
            threshold = datetime.now(timezone.utc) + timedelta(minutes=10)
            stmt = select(YouTubeChannelCredential).where(YouTubeChannelCredential.expires_at <= threshold)
            res = await db.execute(stmt)
            credentials = res.scalars().all()

            for cred in credentials:
                try:
                    token_res = await youtube_service.refresh_access_token(cred.encrypted_refresh_token)
                    new_access = token_res.get("access_token")
                    expires_in = token_res.get("expires_in", 3600)
                    if new_access:
                        from app.core.encryption import encrypt_token
                        cred.encrypted_access_token = encrypt_token(new_access)
                        cred.expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
                except Exception as e:
                    logger.error(f"Failed to refresh credential ID {cred.id}: {e}")
            await db.commit()

    return run_async(_async_refresh())
