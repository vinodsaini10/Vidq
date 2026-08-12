from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class VideoBase(BaseModel):
    title: str
    status: str = "Idea"
    niche: Optional[str] = None
    scheduled_date: Optional[str] = None


class VideoCreate(VideoBase):
    script_body: Optional[str] = None


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    niche: Optional[str] = None
    scheduled_date: Optional[str] = None
    script_body: Optional[str] = None


class VideoResponse(VideoBase):
    id: UUID
    user_id: UUID
    predicted_ctr: Optional[str] = None
    estimated_views: Optional[str] = None
    seo_score: int
    script_body: Optional[str] = None
    generated_titles: List[Any] = []
    generated_tags: List[str] = []
    description: Optional[str] = None
    thumbnail_prompts: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True
