import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel
from app.models.enums import NotificationType, NotificationStatus


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(SQLEnum(NotificationType), default=NotificationType.SYSTEM, nullable=False)
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.UNREAD, nullable=False, index=True)
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True, index=True)

    user = relationship("User", back_populates="notifications")


class NotificationTemplate(BaseModel):
    __tablename__ = "notification_templates"

    code = Column(String, unique=True, nullable=False)
    title_template = Column(String, nullable=False)
    body_template = Column(String, nullable=False)


class NotificationDelivery(BaseModel):
    __tablename__ = "notification_deliveries"

    notification_id = Column(UUID(as_uuid=True), ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False)
    channel = Column(String, default="in_app", nullable=False)  # in_app, email, push
    delivered_at = Column(DateTime(timezone=True), nullable=False)


class NotificationPreference(BaseModel):
    __tablename__ = "notification_preferences"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    email_milestones = Column(Boolean, default=True, nullable=False)
    email_alerts = Column(Boolean, default=True, nullable=False)
    push_enabled = Column(Boolean, default=True, nullable=False)
