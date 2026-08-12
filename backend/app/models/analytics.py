import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, BigInteger, Float, Numeric, ForeignKey, JSON, DateTime
)
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class AnalyticsSnapshot(BaseModel):
    __tablename__ = "analytics_snapshots"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    channel_id = Column(UUID(as_uuid=True), ForeignKey("youtube_channels.id", ondelete="CASCADE"), nullable=True)
    total_views = Column(BigInteger, default=0, nullable=False)
    subscribers = Column(BigInteger, default=0, nullable=False)
    estimated_revenue = Column(Numeric(12, 2), default=0.00, nullable=False)
    avg_ctr = Column(Float, default=0.0, nullable=False)
    channel_health_score = Column(Integer, default=85, nullable=False)
    monthly_impressions = Column(BigInteger, default=0, nullable=False)
    historical_chart_data = Column(JSON, default=[], nullable=False)


class DailyChannelMetric(BaseModel):
    __tablename__ = "daily_channel_metrics"

    channel_id = Column(UUID(as_uuid=True), ForeignKey("youtube_channels.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    views = Column(BigInteger, default=0, nullable=False)
    watch_time_hours = Column(Float, default=0.0, nullable=False)
    subscribers = Column(Integer, default=0, nullable=False)
    estimated_revenue = Column(Numeric(12, 2), default=0.00, nullable=False)


class DailyVideoMetric(BaseModel):
    __tablename__ = "daily_video_metrics"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    views = Column(BigInteger, default=0, nullable=False)
    likes = Column(Integer, default=0, nullable=False)
    shares = Column(Integer, default=0, nullable=False)
    comments = Column(Integer, default=0, nullable=False)


class AudienceMetric(BaseModel):
    __tablename__ = "audience_metrics"

    channel_id = Column(UUID(as_uuid=True), ForeignKey("youtube_channels.id", ondelete="CASCADE"), nullable=False, index=True)
    age_13_17_percent = Column(Float, default=0.0, nullable=False)
    age_18_24_percent = Column(Float, default=0.0, nullable=False)
    age_25_34_percent = Column(Float, default=0.0, nullable=False)
    age_35_44_percent = Column(Float, default=0.0, nullable=False)
    male_percent = Column(Float, default=0.0, nullable=False)
    female_percent = Column(Float, default=0.0, nullable=False)


class TrafficSource(BaseModel):
    __tablename__ = "traffic_sources"

    channel_id = Column(UUID(as_uuid=True), ForeignKey("youtube_channels.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type = Column(String, nullable=False)  # browse_features, suggested_videos, youtube_search
    views_percent = Column(Float, default=0.0, nullable=False)


class DeviceMetric(BaseModel):
    __tablename__ = "device_metrics"

    channel_id = Column(UUID(as_uuid=True), ForeignKey("youtube_channels.id", ondelete="CASCADE"), nullable=False, index=True)
    device_type = Column(String, nullable=False)  # mobile, desktop, tv, tablet
    views_percent = Column(Float, default=0.0, nullable=False)


class GeographyMetric(BaseModel):
    __tablename__ = "geography_metrics"

    channel_id = Column(UUID(as_uuid=True), ForeignKey("youtube_channels.id", ondelete="CASCADE"), nullable=False, index=True)
    country_code = Column(String(2), nullable=False)
    views_percent = Column(Float, default=0.0, nullable=False)


class RetentionMetric(BaseModel):
    __tablename__ = "retention_metrics"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False, index=True)
    avg_view_duration_seconds = Column(Float, default=0.0, nullable=False)
    retention_at_30s_percent = Column(Float, default=0.0, nullable=False)


class EngagementMetric(BaseModel):
    __tablename__ = "engagement_metrics"

    channel_id = Column(UUID(as_uuid=True), ForeignKey("youtube_channels.id", ondelete="CASCADE"), nullable=False, index=True)
    likes_per_100_views = Column(Float, default=0.0, nullable=False)
    comments_per_100_views = Column(Float, default=0.0, nullable=False)


class RevenueMetric(BaseModel):
    __tablename__ = "revenue_metrics"

    channel_id = Column(UUID(as_uuid=True), ForeignKey("youtube_channels.id", ondelete="CASCADE"), nullable=False, index=True)
    rpm = Column(Numeric(12, 2), default=0.00, nullable=False)
    cpm = Column(Numeric(12, 2), default=0.00, nullable=False)
    estimated_earnings = Column(Numeric(12, 2), default=0.00, nullable=False)
