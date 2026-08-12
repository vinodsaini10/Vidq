from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.models.base import BaseModel


class VideoStatus(str, enum.Enum):
    IDEA = "Idea"
    SCRIPTING = "Scripting"
    FILMING = "Filming"
    EDITING = "Editing"
    SCHEDULED = "Scheduled"
    PUBLISHED = "Published"


class Video(BaseModel):
    __tablename__ = "videos"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    status = Column(SQLEnum(VideoStatus), default=VideoStatus.IDEA, nullable=False)
    niche = Column(String, nullable=True)
    scheduled_date = Column(String, nullable=True)
    
    predicted_ctr = Column(String, nullable=True)
    estimated_views = Column(String, nullable=True)
    seo_score = Column(Integer, default=0)
    
    script_body = Column(Text, nullable=True)
    generated_titles = Column(JSON, default=[], nullable=False)
    generated_tags = Column(JSON, default=[], nullable=False)
    description = Column(Text, nullable=True)
    thumbnail_prompts = Column(JSON, default=[], nullable=False)
