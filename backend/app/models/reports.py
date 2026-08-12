import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import BaseModel
from app.models.enums import ReportStatus


class Report(BaseModel):
    __tablename__ = "reports"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    report_type = Column(String, nullable=False)  # PDF, CSV
    file_size = Column(String, nullable=False)
    download_url = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.COMPLETED, nullable=False)


class ReportTemplate(BaseModel):
    __tablename__ = "report_templates"

    name = Column(String, nullable=False)
    layout_config = Column(JSON, default={}, nullable=False)


class ReportSchedule(BaseModel):
    __tablename__ = "report_schedules"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    frequency = Column(String, default="weekly", nullable=False)  # daily, weekly, monthly
    next_run_at = Column(DateTime(timezone=True), nullable=True)


class ReportDelivery(BaseModel):
    __tablename__ = "report_deliveries"

    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    recipient_email = Column(String, nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=False)


class ReportExport(BaseModel):
    __tablename__ = "report_exports"

    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    export_format = Column(String, default="pdf", nullable=False)
