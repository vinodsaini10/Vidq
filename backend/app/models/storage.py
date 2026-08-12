import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class UploadedFile(BaseModel):
    __tablename__ = "uploaded_files"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)


class MediaAsset(BaseModel):
    __tablename__ = "media_assets"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)  # thumbnail, video_clip, audio_track, overlay
    storage_url = Column(String, nullable=False)
