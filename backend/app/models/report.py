from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class GeneratedReport(BaseModel):
    __tablename__ = "generated_reports"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    report_type = Column(String, nullable=False)  # PDF, CSV
    file_size = Column(String, nullable=False)
    download_url = Column(String, nullable=False)
    summary = Column(String, nullable=True)
