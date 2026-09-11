from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime, timezone
from app.database.base import Base

class MedicalValue(Base):
    __tablename__ = "medical_values"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    ocr_result_id = Column(Integer, ForeignKey("ocr_results.id", ondelete="SET NULL"), nullable=True)
    ocr_version = Column(Integer, default=1)
    
    page_number = Column(Integer, default=1)
    block_id = Column(String, nullable=True)

    parameter_name = Column(String, nullable=False)   # Canonical parameter name, e.g. Hemoglobin
    parameter_code = Column(String, nullable=True)    # Code e.g. HGB
    category = Column(String, default="General")      # CBC, LFT, KFT, Lipid, Sugar, Thyroid, Vitamin, Urine

    value = Column(String, nullable=False)           # Raw string value
    numeric_value = Column(Float, nullable=True)      # Extracted float value
    unit = Column(String, nullable=True)             # Normalized unit e.g. g/dL

    reference_range = Column(String, nullable=True)   # Raw range string
    reference_context = Column(String, nullable=True) # e.g. Adult Male, Adult Female, General
    reference_low = Column(Float, nullable=True)     # Lower numeric threshold
    reference_high = Column(Float, nullable=True)    # Upper numeric threshold

    status = Column(String, default="Pending Validation", nullable=False) # Always 'Pending Validation' in Phase 4
    confidence = Column(Float, default=1.0)
    bbox = Column(String, nullable=True)             # JSON string of coordinates [x0, y0, x1, y1]

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
