import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, Integer, ForeignKey, JSON, DateTime, Text, Enum as SQLEnum, Table
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel
from app.models.enums import UserRole, UserStatus


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)

    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")


class Permission(BaseModel):
    __tablename__ = "permissions"

    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)

    role = Column(SQLEnum(UserRole), default=UserRole.FREE_USER, nullable=False, index=True)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # YouTube Integration fields for quick access
    youtube_channel_id = Column(String, nullable=True, index=True)
    youtube_channel_title = Column(String, nullable=True)
    youtube_handle = Column(String, nullable=True)
    youtube_subscriber_count = Column(Integer, default=0)

    # AI Credits
    ai_credits_used = Column(Integer, default=0, nullable=False)
    ai_credits_max = Column(Integer, default=50, nullable=False)

    # Preferences & JSON
    preferences = Column(JSON, default={
        "theme": "dark",
        "language": "en",
        "email_notifications": True,
        "weekly_reports": True
    }, nullable=False)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    devices = relationship("UserDevice", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")


class UserProfile(BaseModel):
    __tablename__ = "user_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    company = Column(String, nullable=True)
    website = Column(String, nullable=True)
    timezone = Column(String, default="UTC", nullable=False)
    language = Column(String, default="en", nullable=False)

    user = relationship("User", back_populates="profile")


class UserSession(BaseModel):
    __tablename__ = "user_sessions"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = Column(String, unique=True, nullable=False, index=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="sessions")


class UserDevice(BaseModel):
    __tablename__ = "user_devices"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    device_name = Column(String, nullable=False)
    device_type = Column(String, nullable=True)  # mobile, desktop, tablet
    fcm_push_token = Column(String, nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="devices")


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    details = Column(JSON, default={}, nullable=False)


class SecurityEvent(BaseModel):
    __tablename__ = "security_events"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String, nullable=False)  # failed_login, password_reset, token_revoked
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)


class EmailVerification(BaseModel):
    __tablename__ = "email_verifications"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)


class PasswordResetToken(BaseModel):
    __tablename__ = "password_reset_tokens"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)


class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_blacklisted = Column(Boolean, default=False, nullable=False)


class OAuthAccount(BaseModel):
    __tablename__ = "oauth_accounts"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String, nullable=False)  # google, github, etc.
    provider_user_id = Column(String, nullable=False)
    access_token = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="oauth_accounts")


class TwoFactorSetting(BaseModel):
    __tablename__ = "two_factor_settings"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    is_enabled = Column(Boolean, default=False, nullable=False)
    secret = Column(String, nullable=True)


class LoginAttempt(BaseModel):
    __tablename__ = "login_attempts"

    email = Column(String, nullable=False, index=True)
    ip_address = Column(String, nullable=False)
    successful = Column(Boolean, nullable=False)
    attempt_time = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
