from sqlalchemy import Column, String, Boolean, Integer, Enum as SQLEnum, JSON
import enum
from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    MODERATOR = "MODERATOR"
    SUPPORT = "SUPPORT"
    PREMIUM_USER = "PREMIUM_USER"
    FREE_USER = "FREE_USER"


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    
    role = Column(SQLEnum(UserRole), default=UserRole.FREE_USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # YouTube Integration
    youtube_channel_id = Column(String, nullable=True)
    youtube_channel_title = Column(String, nullable=True)
    youtube_handle = Column(String, nullable=True)
    youtube_subscriber_count = Column(Integer, default=0)
    
    # AI Credits Management
    ai_credits_used = Column(Integer, default=0, nullable=False)
    ai_credits_max = Column(Integer, default=50, nullable=False)
    
    # Preferences & Settings
    preferences = Column(JSON, default={
        "theme": "dark",
        "language": "en",
        "email_notifications": True,
        "weekly_reports": True
    }, nullable=False)
