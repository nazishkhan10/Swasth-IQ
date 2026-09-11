from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Float, ForeignKey
from datetime import datetime, timezone
from app.database.base import Base


class ReportStatus:
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    DELETED = "deleted"


class UploadSource:
    UPLOAD = "upload"
    CAMERA = "camera"


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # File identity
    filename = Column(String, nullable=False)            # UUID-based stored filename
    original_filename = Column(String, nullable=False)   # Original user filename

    # Storage
    file_path = Column(String, nullable=False)           # Absolute path on disk
    file_url = Column(String, nullable=True)             # Relative URL for serving
    file_size = Column(BigInteger, nullable=True)        # Size in bytes
    mime_type = Column(String, nullable=True)            # e.g. application/pdf

    # Metadata
    upload_source = Column(String, default=UploadSource.UPLOAD)  # upload | camera
    status = Column(String, default=ReportStatus.UPLOADED)

    # Phase 3 OCR Metadata
    ocr_status = Column(String, default="pending", nullable=False) # pending | queued | processing | completed | failed | retrying | cancelled
    ocr_version = Column(Integer, default=0, nullable=False)
    last_engine = Column(String, nullable=True)
    last_processed = Column(DateTime, nullable=True)
    average_confidence = Column(Float, nullable=True)
    page_count = Column(Integer, nullable=True)
    processing_time = Column(Float, nullable=True)

    # Timestamps
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

