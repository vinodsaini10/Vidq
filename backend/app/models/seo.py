import uuid
from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class SEOAudit(BaseModel):
    __tablename__ = "seo_audits"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=True, index=True)
    target_keyword = Column(String, nullable=False)
    overall_score = Column(Integer, default=0, nullable=False)


class SEOAuditResult(BaseModel):
    __tablename__ = "seo_audit_results"

    audit_id = Column(UUID(as_uuid=True), ForeignKey("seo_audits.id", ondelete="CASCADE"), nullable=False, index=True)
    section = Column(String, nullable=False)  # title, description, tags, thumbnail
    score = Column(Integer, default=0, nullable=False)
    grade = Column(String(2), default="B", nullable=False)
    issues = Column(JSON, default=[], nullable=False)


class VideoSEOScore(BaseModel):
    __tablename__ = "video_seo_scores"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), unique=True, nullable=False)
    title_score = Column(Integer, default=0, nullable=False)
    description_score = Column(Integer, default=0, nullable=False)
    tags_score = Column(Integer, default=0, nullable=False)
    thumbnail_score = Column(Integer, default=0, nullable=False)
    overall_score = Column(Integer, default=0, nullable=False)


class TitleScore(BaseModel):
    __tablename__ = "title_scores"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False)
    title_text = Column(String, nullable=False)
    power_words_count = Column(Integer, default=0, nullable=False)
    char_count = Column(Integer, default=0, nullable=False)
    score = Column(Integer, default=0, nullable=False)


class DescriptionScore(BaseModel):
    __tablename__ = "description_scores"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False)
    word_count = Column(Integer, default=0, nullable=False)
    has_timestamps = Column(Integer, default=0, nullable=False)
    score = Column(Integer, default=0, nullable=False)


class TagScore(BaseModel):
    __tablename__ = "tag_scores"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False)
    tag_count = Column(Integer, default=0, nullable=False)
    relevance_score = Column(Integer, default=0, nullable=False)


class ThumbnailScore(BaseModel):
    __tablename__ = "thumbnail_scores"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False)
    contrast_score = Column(Integer, default=0, nullable=False)
    face_detected = Column(Integer, default=0, nullable=False)
    text_legibility = Column(Integer, default=0, nullable=False)


class SEORecommendation(BaseModel):
    __tablename__ = "seo_recommendations"

    audit_id = Column(UUID(as_uuid=True), ForeignKey("seo_audits.id", ondelete="CASCADE"), nullable=False)
    recommendation_text = Column(Text, nullable=False)
    priority = Column(String, default="high", nullable=False)  # high, medium, low
