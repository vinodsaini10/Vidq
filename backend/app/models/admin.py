import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, JSON, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class AdminAction(BaseModel):
    __tablename__ = "admin_actions"

    admin_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String, nullable=False)
    target_resource = Column(String, nullable=False)
    details = Column(JSON, default={}, nullable=False)


class FeatureFlag(BaseModel):
    __tablename__ = "feature_flags"

    key = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    is_enabled = Column(Boolean, default=False, nullable=False)
    rollout_percent = Column(String, default="100", nullable=False)


class SystemSetting(BaseModel):
    __tablename__ = "system_settings"

    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)


class APIKey(BaseModel):
    __tablename__ = "api_keys"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    key_hash = Column(String, unique=True, nullable=False, index=True)
    prefix = Column(String(8), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)


class WebhookEvent(BaseModel):
    __tablename__ = "webhook_events"

    event_type = Column(String, nullable=False, index=True)
    provider = Column(String, nullable=False)  # stripe, youtube, custom
    payload = Column(JSON, default={}, nullable=False)
    is_processed = Column(Boolean, default=False, nullable=False)


class Announcement(BaseModel):
    __tablename__ = "announcements"

    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    audience = Column(String, default="ALL", nullable=False)  # ALL, FREE_USER, PREMIUM_USER, ADMIN
    is_active = Column(Boolean, default=True, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)


class RolePermission(BaseModel):
    __tablename__ = "role_permissions"

    role = Column(String, nullable=False, index=True)
    permission = Column(String, nullable=False, index=True)

