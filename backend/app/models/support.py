import uuid
from sqlalchemy import Column, String, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel
from app.models.enums import TicketStatus


class SupportTicket(BaseModel):
    __tablename__ = "support_tickets"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_number = Column(String, unique=True, nullable=False)
    subject = Column(String, nullable=False)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.OPEN, nullable=False)
    priority = Column(String, default="medium", nullable=False)  # low, medium, high, urgent

    messages = relationship("SupportMessage", back_populates="ticket", cascade="all, delete-orphan")


class SupportMessage(BaseModel):
    __tablename__ = "support_messages"

    ticket_id = Column(UUID(as_uuid=True), ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_type = Column(String, nullable=False)  # user, support_agent
    message_text = Column(Text, nullable=False)

    ticket = relationship("SupportTicket", back_populates="messages")
    attachments = relationship("SupportAttachment", back_populates="message", cascade="all, delete-orphan")


class SupportAttachment(BaseModel):
    __tablename__ = "support_attachments"

    message_id = Column(UUID(as_uuid=True), ForeignKey("support_messages.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String, nullable=False)
    file_url = Column(String, nullable=False)

    message = relationship("SupportMessage", back_populates="attachments")
