from typing import Optional, Any
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    youtube_channel_id: Optional[str] = None
    preferences: Optional[dict] = None


class UserResponse(UserBase):
    id: UUID
    role: str
    is_active: bool
    is_verified: bool
    youtube_channel_id: Optional[str] = None
    youtube_channel_title: Optional[str] = None
    youtube_handle: Optional[str] = None
    youtube_subscriber_count: int
    ai_credits_used: int
    ai_credits_max: int
    preferences: dict
    created_at: datetime

    class Config:
        from_attributes = True
