from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class KeywordSearch(BaseModel):
    __tablename__ = "keyword_searches"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    keyword = Column(String, nullable=False, index=True)
    search_volume = Column(Integer, default=0)
    competition_score = Column(Float, default=0.0)
    opportunity_score = Column(Integer, default=0)
    related_keywords = Column(JSON, default=[], nullable=False)
