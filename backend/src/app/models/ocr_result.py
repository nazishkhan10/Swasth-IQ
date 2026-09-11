from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from datetime import datetime, timezone
from app.database.base import Base


class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False, index=True)

    page_number = Column(Integer, nullable=False, default=1)
    raw_text = Column(Text, nullable=True)
    json_path = Column(String, nullable=False)   # Relative path to page JSON file
    confidence = Column(Float, nullable=False, default=1.0)
    processing_time = Column(Float, nullable=True, default=0.0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
