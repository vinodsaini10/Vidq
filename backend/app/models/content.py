import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class ContentIdea(BaseModel):
    __tablename__ = "content_ideas"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    niche = Column(String, nullable=True)
    viral_score = Column(Integer, default=0, nullable=False)
    source = Column(String, default="ai_generated", nullable=False)


class ContentCategory(BaseModel):
    __tablename__ = "content_categories"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    color_hex = Column(String(7), default="#3B82F6", nullable=False)


class ContentCalendarItem(BaseModel):
    __tablename__ = "content_calendar_items"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="SET NULL"), nullable=True)
    title = Column(String, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="scheduled", nullable=False)


class ContentBrief(BaseModel):
    __tablename__ = "content_briefs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String, nullable=False)
    target_audience = Column(String, nullable=True)
    primary_goal = Column(String, nullable=True)
    brief_body = Column(Text, nullable=True)


class VideoProject(BaseModel):
    __tablename__ = "video_projects"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    status = Column(String, default="in_production", nullable=False)


class VideoScript(BaseModel):
    __tablename__ = "video_scripts"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False, index=True)
    hook_text = Column(Text, nullable=True)
    intro_text = Column(Text, nullable=True)
    body_text = Column(Text, nullable=True)
    cta_text = Column(Text, nullable=True)
    full_script = Column(Text, nullable=False)


class VideoHook(BaseModel):
    __tablename__ = "video_hooks"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False)
    hook_variation = Column(Text, nullable=False)
    retention_score_estimate = Column(Integer, default=85, nullable=False)


class VideoTitleOption(BaseModel):
    __tablename__ = "video_title_options"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    predicted_ctr = Column(Float, default=0.0, nullable=False)


class VideoDescriptionOption(BaseModel):
    __tablename__ = "video_description_options"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False)
    description_body = Column(Text, nullable=False)


class VideoTagOption(BaseModel):
    __tablename__ = "video_tag_options"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False)
    tag_list = Column(JSON, default=[], nullable=False)


class Hashtag(BaseModel):
    __tablename__ = "hashtags"

    tag = Column(String, unique=True, nullable=False, index=True)
    search_volume = Column(Integer, default=0, nullable=False)
