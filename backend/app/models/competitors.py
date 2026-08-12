import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, Float, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class Competitor(BaseModel):
    __tablename__ = "competitors"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    channel_id = Column(String, nullable=False, index=True)
    channel_name = Column(String, nullable=False)
    subscribers = Column(BigInteger, default=0, nullable=False)
    avg_views_per_hour = Column(Float, default=0.0, nullable=False)


class CompetitorChannel(BaseModel):
    __tablename__ = "competitor_channels"

    channel_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    subscriber_count = Column(BigInteger, default=0, nullable=False)
    video_count = Column(Integer, default=0, nullable=False)


class CompetitorVideo(BaseModel):
    __tablename__ = "competitor_videos"

    competitor_channel_id = Column(String, nullable=False, index=True)
    video_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    views = Column(BigInteger, default=0, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=False)
    outlier_score = Column(Float, default=1.0, nullable=False)  # e.g., 4.2x channel avg


class CompetitorSnapshot(BaseModel):
    __tablename__ = "competitor_snapshots"

    competitor_id = Column(UUID(as_uuid=True), ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_date = Column(DateTime(timezone=True), nullable=False)
    subscriber_count = Column(BigInteger, default=0, nullable=False)
    total_views = Column(BigInteger, default=0, nullable=False)


class CompetitorMetric(BaseModel):
    __tablename__ = "competitor_metrics"

    competitor_id = Column(UUID(as_uuid=True), ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, default=0.0, nullable=False)


class CompetitorAlert(BaseModel):
    __tablename__ = "competitor_alerts"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String, nullable=False)  # viral_outlier, upload_frequency, title_change
    message = Column(String, nullable=False)
    is_dismissed = Column(Integer, default=0, nullable=False)
