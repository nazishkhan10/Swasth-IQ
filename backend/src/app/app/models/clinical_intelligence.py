"""
Clinical Intelligence Database Model (Phase 7 — Architecture Freeze v8.2).
Caches generated Patient & Doctor summaries, organ panel scores, and educational insights per report.
Ensures sub-second load times and prevents redundant token consumption.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.database.base import Base


class CachedClinicalIntelligence(Base):
    """DB Cache for Phase 6/7 Clinical Intelligence & Explanations."""

    __tablename__ = "report_clinical_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    patient_summary_json = Column(Text, nullable=True)
    doctor_summary_json = Column(Text, nullable=True)
    organ_scores_json = Column(Text, nullable=True)
    education_insights_json = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<CachedClinicalIntelligence for Report #{self.report_id}>"
