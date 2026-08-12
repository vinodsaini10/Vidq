import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, Float, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class Keyword(BaseModel):
    __tablename__ = "keywords"

    keyword = Column(String, unique=True, nullable=False, index=True)
    search_volume = Column(BigInteger, default=0, nullable=False)
    competition_score = Column(Float, default=0.0, nullable=False)
    opportunity_score = Column(Integer, default=0, nullable=False)


class KeywordMetric(BaseModel):
    __tablename__ = "keyword_metrics"

    keyword_id = Column(UUID(as_uuid=True), ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False, index=True)
    cpm_estimate = Column(Float, default=0.0, nullable=False)
    search_intent = Column(String, default="informational", nullable=False)


class KeywordHistory(BaseModel):
    __tablename__ = "keyword_history"

    keyword_id = Column(UUID(as_uuid=True), ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    search_volume = Column(BigInteger, default=0, nullable=False)


class KeywordRanking(BaseModel):
    __tablename__ = "keyword_rankings"

    video_id = Column(UUID(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False, index=True)
    keyword_id = Column(UUID(as_uuid=True), ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False, index=True)
    rank_position = Column(Integer, nullable=False)


class KeywordTracking(BaseModel):
    __tablename__ = "keyword_tracking"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    keyword_id = Column(UUID(as_uuid=True), ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False, index=True)
    is_active = Column(Integer, default=1, nullable=False)


class KeywordGroup(BaseModel):
    __tablename__ = "keyword_groups"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)


class RelatedKeyword(BaseModel):
    __tablename__ = "related_keywords"

    parent_keyword_id = Column(UUID(as_uuid=True), ForeignKey("keywords.id", ondelete="CASCADE"), nullable=False, index=True)
    related_keyword_text = Column(String, nullable=False)
    relevance_score = Column(Float, default=0.0, nullable=False)


class KeywordSuggestion(BaseModel):
    __tablename__ = "keyword_suggestions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    seed_keyword = Column(String, nullable=False)
    suggested_keyword = Column(String, nullable=False)
    source = Column(String, default="ai_gemini", nullable=False)
