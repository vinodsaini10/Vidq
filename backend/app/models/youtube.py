import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Integer, BigInteger, Float, ForeignKey, JSON, DateTime, Text, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel
from app.models.enums import VideoStatus


class YouTubeChannel(BaseModel):
    __tablename__ = "youtube_channels"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    channel_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    custom_url = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    thumbnail_url = Column(String, nullable=True)
    country = Column(String(2), nullable=True)

    subscriber_count = Column(BigInteger, default=0, nullable=False)
    video_count = Column(Integer, default=0, nullable=False)
    view_count = Column(BigInteger, default=0, nullable=False)

    videos = relationship("YouTubeVideo", back_populates="channel", cascade="all, delete-orphan")
    statistics = relationship("YouTubeChannelStatistic", back_populates="channel", cascade="all, delete-orphan")
    credentials = relationship("YouTubeChannelCredential", back_populates="channel", uselist=False, cascade="all, delete-orphan")


class YouTubeChannelCredential(BaseModel):
    __tablename__ = "youtube_channel_credentials"

    channel_id = Column(UUID(as_uuid=True), ForeignKey("youtube_channels.id", ondelete="CASCADE"), unique=True, nullable=False)
    encrypted_access_token = Column(Text, nullable=False)
    encrypted_refresh_token = Column(Text, nullable=False)
    token_uri = Column(String, default="https://oauth2.googleapis.com/token", nullable=False)
    client_id = Column(String, nullable=True)
    scopes = Column(JSON, default=[], nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    channel = relationship("YouTubeChannel", back_populates="credentials")


class YouTubeVideo(BaseModel):
    __tablename__ = "youtube_videos"

    channel_id = Column(UUID(as_uuid=True), ForeignKey("youtube_channels.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(String, nullable=True, index=True)  # YouTube internal ID if published
    title = Column(String, nullable=False)
    status = Column(SQLEnum(VideoStatus), default=VideoStatus.IDEA, nullable=False, index=True)
    niche = Column(String, nullable=True)
    scheduled_date = Column(String, nullable=True)

    predicted_ctr = Column(String, nullable=True)
    estimated_views = Column(String, nullable=True)
    seo_score = Column(Integer, default=0, nullable=False)

    script_body = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    generated_titles = Column(JSON, default=[], nullable=False)
    generated_tags = Column(JSON, default=[], nullable=False)
    thumbnail_prompts = Column(JSON, default=[], nullable=False)

    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    duration = Column(String, nullable=True)  # ISO 8601 duration
    privacy_status = Column(String, default="public", nullable=False)

    channel = relationship("YouTubeChannel", back_populates="videos")
    statistics = relationship("YouTubeVideoStatistic", back_populates="video", cascade="all, delete-orphan")


class YouTubeVideoStatistic(BaseModel):
    __tablename__ = "youtube_video_statistics"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False, index=True)
    views = Column(BigInteger, default=0, nullable=False)
    likes = Column(BigInteger, default=0, nullable=False)
    comments = Column(BigInteger, default=0, nullable=False)
    shares = Column(BigInteger, default=0, nullable=False)
    impressions = Column(BigInteger, default=0, nullable=False)
    ctr_percent = Column(Float, default=0.0, nullable=False)
    avg_view_duration_seconds = Column(Float, default=0.0, nullable=False)

    video = relationship("YouTubeVideo", back_populates="statistics")


class YouTubeChannelStatistic(BaseModel):
    __tablename__ = "youtube_channel_statistics"

    channel_id = Column(UUID(as_uuid=True), ForeignKey("youtube_channels.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    subscribers_gained = Column(Integer, default=0, nullable=False)
    subscribers_lost = Column(Integer, default=0, nullable=False)
    views = Column(BigInteger, default=0, nullable=False)
    estimated_revenue = Column(Float, default=0.0, nullable=False)

    channel = relationship("YouTubeChannel", back_populates="statistics")


class YouTubePlaylist(BaseModel):
    __tablename__ = "youtube_playlists"

    channel_id = Column(UUID(as_uuid=True), ForeignKey("youtube_channels.id", ondelete="CASCADE"), nullable=False)
    playlist_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    item_count = Column(Integer, default=0, nullable=False)


class YouTubeComment(BaseModel):
    __tablename__ = "youtube_comments"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False, index=True)
    comment_id = Column(String, unique=True, nullable=False)
    author_name = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    like_count = Column(Integer, default=0, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=False)


class YouTubeCommentAnalysis(BaseModel):
    __tablename__ = "youtube_comment_analysis"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False, index=True)
    positive_sentiment_percent = Column(Float, default=0.0, nullable=False)
    negative_sentiment_percent = Column(Float, default=0.0, nullable=False)
    neutral_sentiment_percent = Column(Float, default=0.0, nullable=False)
    key_themes = Column(JSON, default=[], nullable=False)


class YouTubeCategory(BaseModel):
    __tablename__ = "youtube_categories"

    category_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)


class YouTubeTag(BaseModel):
    __tablename__ = "youtube_tags"

    tag = Column(String, unique=True, nullable=False, index=True)
    use_count = Column(Integer, default=1, nullable=False)


class YouTubeThumbnail(BaseModel):
    __tablename__ = "youtube_thumbnails"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False)
    url = Column(String, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    variant = Column(String, default="default", nullable=False)


class YouTubeLiveStream(BaseModel):
    __tablename__ = "youtube_live_streams"

    channel_id = Column(UUID(as_uuid=True), ForeignKey("youtube_channels.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    scheduled_start_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, default="upcoming", nullable=False)
