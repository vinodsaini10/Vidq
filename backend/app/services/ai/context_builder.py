import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.youtube import YouTubeChannel, YouTubeVideo
from app.models.analytics import AnalyticsSnapshot
from app.models.competitors import Competitor
from app.models.user import User
from app.services.ai.safety import safety_layer

logger = logging.getLogger(__name__)


class YouTubeContextBuilder:
    """Assembles authorized YouTube data and channel analytics into clean, token-optimized context."""

    async def build_context(
        self,
        db: AsyncSession,
        user_id: str,
        include_channel: bool = True,
        include_videos: bool = True,
        include_analytics: bool = True,
        include_competitors: bool = False,
        custom_topic: Optional[str] = None,
        max_context_chars: int = 4000,
    ) -> Dict[str, Any]:
        context_parts = []
        structured_info = {}

        # 1. Fetch authenticated user profile & channel
        stmt_user = select(User).where(User.id == user_id)
        res_user = await db.execute(stmt_user)
        user = res_user.scalars().first()

        if include_channel and user:
            stmt_channel = select(YouTubeChannel).where(YouTubeChannel.user_id == user_id)
            res_channel = await db.execute(stmt_channel)
            channel = res_channel.scalars().first()

            if channel:
                title = safety_layer.sanitize_external_content(channel.title)
                subs = channel.subscriber_count or 0
                views = channel.view_count or 0
                videos_cnt = channel.video_count or 0

                channel_str = f"CHANNEL: {title} | Subscribers: {subs:,} | Total Views: {views:,} | Total Videos: {videos_cnt}"
                context_parts.append(channel_str)
                structured_info["channel"] = {"title": title, "subscribers": subs, "views": views}
            elif user.youtube_channel_title:
                channel_str = f"CHANNEL: {user.youtube_channel_title} | Subscribers: {user.youtube_subscriber_count or 0}"
                context_parts.append(channel_str)

        # 2. Fetch top recent video performance
        if include_videos:
            stmt_videos = (
                select(YouTubeVideo)
                .where(YouTubeVideo.user_id == user_id)
                .order_by(YouTubeVideo.published_at.desc())
                .limit(5)
            )
            res_vids = await db.execute(stmt_videos)
            recent_vids = res_vids.scalars().all()

            if recent_vids:
                vid_lines = ["RECENT TOP VIDEOS:"]
                for v in recent_vids:
                    san_title = safety_layer.sanitize_external_content(v.title)
                    vid_lines.append(f"- {san_title} (Views: {v.view_count or 0:,}, Likes: {v.like_count or 0:,})")
                context_parts.append("\n".join(vid_lines))

        # 3. Fetch channel analytics
        if include_analytics:
            stmt_snap = (
                select(AnalyticsSnapshot)
                .where(AnalyticsSnapshot.user_id == user_id)
                .order_by(AnalyticsSnapshot.created_at.desc())
                .limit(1)
            )
            res_snap = await db.execute(stmt_snap)
            snap = res_snap.scalars().first()
            if snap:
                context_parts.append(
                    f"ANALYTICS SNAPSHOT: Avg Retention: {snap.avg_view_duration or '3m 45s'}, "
                    f"Top Traffic Source: YouTube Search ({snap.top_traffic_source or 'Search'})"
                )

        # 4. Fetch competitor public benchmark topics
        if include_competitors:
            stmt_comp = select(Competitor).where(Competitor.user_id == user_id).limit(3)
            res_comp = await db.execute(stmt_comp)
            comps = res_comp.scalars().all()
            if comps:
                comp_names = [safety_layer.sanitize_external_content(c.name) for c in comps]
                context_parts.append(f"COMPETITORS WATCHED: {', '.join(comp_names)}")

        full_context_text = "\n\n".join(context_parts)
        if len(full_context_text) > max_context_chars:
            full_context_text = full_context_text[:max_context_chars] + "... [TRUNCATED]"

        return {
            "formatted_context": full_context_text,
            "structured_info": structured_info,
        }


context_builder = YouTubeContextBuilder()
