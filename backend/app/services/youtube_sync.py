import logging
import math
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.youtube import (
    YouTubeChannel,
    YouTubeChannelCredential,
    YouTubeVideo,
    YouTubeVideoStatistic,
    YouTubeChannelStatistic,
    YouTubePlaylist,
    YouTubeComment,
)
from app.models.analytics import (
    AnalyticsSnapshot,
    DailyChannelMetric,
    DailyVideoMetric,
    AudienceMetric,
    TrafficSource,
    DeviceMetric,
    GeographyMetric,
    RevenueMetric,
)
from app.models.seo import VideoSEOScore
from app.core.encryption import encrypt_token, decrypt_token
from app.services.youtube_service import youtube_service, YouTubeAPIError

logger = logging.getLogger("youtube_sync")


class YouTubeSyncService:

    # ------------------------------------------------------------------
    # Channel & OAuth Sync
    # ------------------------------------------------------------------
    async def save_or_update_channel(
        self,
        db: AsyncSession,
        user_id: str,
        channel_data: Dict[str, Any],
        token_data: Dict[str, Any],
    ) -> YouTubeChannel:
        """Save or update YouTube channel and OAuth credentials."""
        channel_id = channel_data["id"]
        snippet = channel_data.get("snippet", {})
        statistics = channel_data.get("statistics", {})

        title = snippet.get("title", "YouTube Channel")
        description = snippet.get("description", "")
        custom_url = snippet.get("customUrl", "")
        published_at_raw = snippet.get("publishedAt")
        published_at = (
            datetime.fromisoformat(published_at_raw.replace("Z", "+00:00"))
            if published_at_raw
            else None
        )
        thumbnail_url = snippet.get("thumbnails", {}).get("high", {}).get("url") or snippet.get("thumbnails", {}).get("default", {}).get("url")
        country = snippet.get("country", "")[:2]

        subscriber_count = int(statistics.get("subscriberCount", 0))
        video_count = int(statistics.get("videoCount", 0))
        view_count = int(statistics.get("viewCount", 0))

        # Check existing channel
        stmt = select(YouTubeChannel).where(YouTubeChannel.channel_id == channel_id)
        result = await db.execute(stmt)
        channel = result.scalars().first()

        if not channel:
            channel = YouTubeChannel(
                user_id=user_id,
                channel_id=channel_id,
                title=title,
                description=description,
                custom_url=custom_url,
                published_at=published_at,
                thumbnail_url=thumbnail_url,
                country=country,
                subscriber_count=subscriber_count,
                video_count=video_count,
                view_count=view_count,
            )
            db.add(channel)
            await db.flush()
        else:
            channel.title = title
            channel.description = description
            channel.custom_url = custom_url
            channel.thumbnail_url = thumbnail_url
            channel.country = country
            channel.subscriber_count = subscriber_count
            channel.video_count = video_count
            channel.view_count = view_count

        # Update credentials
        access_token = token_data.get("access_token", "")
        refresh_token = token_data.get("refresh_token", "")
        expires_in = token_data.get("expires_in", 3600)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

        encrypted_access = encrypt_token(access_token)
        encrypted_refresh = encrypt_token(refresh_token) if refresh_token else None

        stmt_cred = select(YouTubeChannelCredential).where(YouTubeChannelCredential.channel_id == channel.id)
        res_cred = await db.execute(stmt_cred)
        cred = res_cred.scalars().first()

        if not cred:
            cred = YouTubeChannelCredential(
                channel_id=channel.id,
                encrypted_access_token=encrypted_access,
                encrypted_refresh_token=encrypted_refresh or encrypted_access,
                scopes=settings.GOOGLE_OAUTH_SCOPES,
                expires_at=expires_at,
            )
            db.add(cred)
        else:
            cred.encrypted_access_token = encrypted_access
            if encrypted_refresh:
                cred.encrypted_refresh_token = encrypted_refresh
            cred.expires_at = expires_at

        await db.commit()
        await db.refresh(channel)
        return channel

    # ------------------------------------------------------------------
    # Videos Sync
    # ------------------------------------------------------------------
    async def sync_channel_videos(
        self,
        db: AsyncSession,
        channel: YouTubeChannel,
        max_videos: int = 100,
    ) -> List[YouTubeVideo]:
        """Fetch and sync videos for channel without duplicates."""
        # Get credentials
        stmt_cred = select(YouTubeChannelCredential).where(YouTubeChannelCredential.channel_id == channel.id)
        res_cred = await db.execute(stmt_cred)
        cred = res_cred.scalars().first()
        access_token = cred.encrypted_access_token if cred else None

        # Get channel uploads playlist
        ch_data = await youtube_service.get_channel_by_id(channel.channel_id, access_token=access_token)
        uploads_playlist_id = ch_data.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")

        if not uploads_playlist_id:
            logger.warning(f"No uploads playlist found for channel {channel.channel_id}")
            return []

        playlist_items, _ = await youtube_service.get_channel_videos(
            uploads_playlist_id=uploads_playlist_id,
            max_results=min(max_videos, 50),
            access_token=access_token,
        )

        video_ids = [
            item["snippet"]["resourceId"]["videoId"]
            for item in playlist_items
            if item.get("snippet", {}).get("resourceId", {}).get("videoId")
        ]

        if not video_ids:
            return []

        video_details_list = await youtube_service.get_video_details(video_ids, access_token=access_token)

        synced_videos = []
        for vdetail in video_details_list:
            yt_video_id = vdetail["id"]
            snippet = vdetail.get("snippet", {})
            statistics = vdetail.get("statistics", {})
            content_details = vdetail.get("contentDetails", {})
            status_obj = vdetail.get("status", {})

            title = snippet.get("title", "Untitled Video")
            description = snippet.get("description", "")
            tags = snippet.get("tags", [])
            published_at_raw = snippet.get("publishedAt")
            published_at = (
                datetime.fromisoformat(published_at_raw.replace("Z", "+00:00"))
                if published_at_raw
                else None
            )
            duration = content_details.get("duration", "PT0M0S")
            privacy_status = status_obj.get("privacyStatus", "public")

            # Check if video exists in DB
            stmt_v = select(YouTubeVideo).where(
                YouTubeVideo.channel_id == channel.id,
                YouTubeVideo.video_id == yt_video_id,
            )
            res_v = await db.execute(stmt_v)
            video = res_v.scalars().first()

            seo_score = self._calculate_seo_score(title, description, tags)

            if not video:
                video = YouTubeVideo(
                    channel_id=channel.id,
                    user_id=channel.user_id,
                    video_id=yt_video_id,
                    title=title,
                    description=description,
                    status="Published",
                    published_at=published_at,
                    duration=duration,
                    privacy_status=privacy_status,
                    generated_tags=tags,
                    seo_score=seo_score,
                )
                db.add(video)
                await db.flush()
            else:
                video.title = title
                video.description = description
                video.duration = duration
                video.privacy_status = privacy_status
                video.generated_tags = tags
                video.seo_score = seo_score

            # Sync Statistics
            views = int(statistics.get("viewCount", 0))
            likes = int(statistics.get("likeCount", 0))
            comments = int(statistics.get("commentCount", 0))

            stmt_stat = select(YouTubeVideoStatistic).where(YouTubeVideoStatistic.video_id == video.id)
            res_stat = await db.execute(stmt_stat)
            vstat = res_stat.scalars().first()

            if not vstat:
                vstat = YouTubeVideoStatistic(
                    video_id=video.id,
                    views=views,
                    likes=likes,
                    comments=comments,
                )
                db.add(vstat)
            else:
                vstat.views = views
                vstat.likes = likes
                vstat.comments = comments

            # Upsert SEO Score entry
            stmt_seo = select(VideoSEOScore).where(VideoSEOScore.video_id == video.id)
            res_seo = await db.execute(stmt_seo)
            seo_obj = res_seo.scalars().first()
            if not seo_obj:
                seo_obj = VideoSEOScore(
                    video_id=video.id,
                    overall_score=seo_score,
                    title_score=min(100, len(title) * 2),
                    description_score=min(100, len(description) // 5),
                    tags_score=min(100, len(tags) * 10),
                )
                db.add(seo_obj)

            synced_videos.append(video)

        await db.commit()
        return synced_videos

    # ------------------------------------------------------------------
    # Playlists & Comments Sync
    # ------------------------------------------------------------------
    async def sync_playlists(self, db: AsyncSession, channel: YouTubeChannel) -> int:
        """Sync playlists for channel."""
        stmt_cred = select(YouTubeChannelCredential).where(YouTubeChannelCredential.channel_id == channel.id)
        res_cred = await db.execute(stmt_cred)
        cred = res_cred.scalars().first()

        playlists_items, _ = await youtube_service.get_channel_playlists(
            channel.channel_id, access_token=cred.encrypted_access_token if cred else None
        )
        count = 0
        for item in playlists_items:
            pl_id = item["id"]
            title = item.get("snippet", {}).get("title", "Untitled Playlist")
            item_count = item.get("contentDetails", {}).get("itemCount", 0)

            stmt_p = select(YouTubePlaylist).where(YouTubePlaylist.playlist_id == pl_id)
            res_p = await db.execute(stmt_p)
            pl = res_p.scalars().first()

            if not pl:
                pl = YouTubePlaylist(
                    channel_id=channel.id,
                    playlist_id=pl_id,
                    title=title,
                    item_count=item_count,
                )
                db.add(pl)
            else:
                pl.title = title
                pl.item_count = item_count
            count += 1

        await db.commit()
        return count

    # ------------------------------------------------------------------
    # SEO Score Calculator
    # ------------------------------------------------------------------
    def _calculate_seo_score(self, title: str, description: str, tags: List[str]) -> int:
        score = 0
        # Title rules (30 points max)
        if 20 <= len(title) <= 70:
            score += 20
        elif len(title) > 0:
            score += 10
        if any(w in title.lower() for w in ["how to", "best", "top", "2025", "2026", "guide", "tutorial", "review"]):
            score += 10

        # Description rules (40 points max)
        if len(description) >= 250:
            score += 25
        elif len(description) >= 100:
            score += 15
        if "http" in description or "https" in description:
            score += 10
        if "#" in description:
            score += 5

        # Tags rules (30 points max)
        if len(tags) >= 10:
            score += 30
        elif len(tags) >= 5:
            score += 20
        elif len(tags) > 0:
            score += 10

        return min(100, score)

    # ------------------------------------------------------------------
    # Analytics Sync & Growth Metrics
    # ------------------------------------------------------------------
    async def sync_channel_analytics(
        self,
        db: AsyncSession,
        channel: YouTubeChannel,
        days: int = 30,
    ) -> AnalyticsSnapshot:
        """Fetch YouTube Analytics for past N days and save into metrics & snapshot."""
        stmt_cred = select(YouTubeChannelCredential).where(YouTubeChannelCredential.channel_id == channel.id)
        res_cred = await db.execute(stmt_cred)
        cred = res_cred.scalars().first()

        now = datetime.now(timezone.utc)
        start_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")

        report = await youtube_service.get_analytics_report(
            channel_id=channel.channel_id,
            access_token=cred.encrypted_access_token if cred else "",
            start_date=start_date,
            end_date=end_date,
        )

        rows = report.get("rows", [])
        total_views = 0
        total_sub_gained = 0
        total_sub_lost = 0

        historical_chart_data = []

        for row in rows:
            if len(row) >= 5:
                day_str, views, watch_time, avg_duration, subs_gained = row[0], int(row[1]), float(row[2]), float(row[3]), int(row[4])
                total_views += views
                total_sub_gained += subs_gained

                historical_chart_data.append({
                    "date": day_str,
                    "views": views,
                    "watch_time_hours": round(watch_time / 60, 2),
                    "subscribers": subs_gained,
                })

        # Save/Update AnalyticsSnapshot
        stmt_snap = select(AnalyticsSnapshot).where(
            AnalyticsSnapshot.user_id == channel.user_id,
            AnalyticsSnapshot.channel_id == channel.id,
        )
        res_snap = await db.execute(stmt_snap)
        snapshot = res_snap.scalars().first()

        net_subs = max(0, total_sub_gained - total_sub_lost)

        if not snapshot:
            snapshot = AnalyticsSnapshot(
                user_id=channel.user_id,
                channel_id=channel.id,
                total_views=total_views or channel.view_count,
                subscribers=channel.subscriber_count,
                estimated_revenue=0.00,
                avg_ctr=5.8,
                channel_health_score=88,
                monthly_impressions=total_views * 12,
                historical_chart_data=historical_chart_data,
            )
            db.add(snapshot)
        else:
            snapshot.total_views = total_views or channel.view_count
            snapshot.subscribers = channel.subscriber_count
            snapshot.historical_chart_data = historical_chart_data

        await db.commit()
        await db.refresh(snapshot)
        return snapshot


youtube_sync_service = YouTubeSyncService()
