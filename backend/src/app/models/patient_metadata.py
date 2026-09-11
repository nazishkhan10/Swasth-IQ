from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime, timezone
from app.database.base import Base

class PatientMetadata(Base):
    __tablename__ = "patient_metadata"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    patient_name = Column(String, nullable=True)
    age = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    lab_name = Column(String, nullable=True)
    doctor_name = Column(String, nullable=True)
    report_date = Column(String, nullable=True)
    sample_date = Column(String, nullable=True)
    accession_number = Column(String, nullable=True)
    detected_report_type = Column(String, default="General")

    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
