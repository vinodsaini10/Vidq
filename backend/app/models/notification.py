from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, default="system")  # milestone, alert, ai, system
    is_read = Column(Boolean, default=False, nullable=False)
