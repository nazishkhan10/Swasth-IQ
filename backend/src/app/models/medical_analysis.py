"""
MedicalAnalysis Model (Phase 6 Clinical Intelligence).
Stores complete deterministic clinical intelligence, disease detections,
organ system scores, evidence traceability, longitudinal timelines,
prompt packages for Phase 7 RAG, and layered confidence metrics.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from datetime import datetime, timezone
from app.database.base import Base


class MedicalAnalysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False, index=True)
    determinism_hash = Column(String(64), nullable=True, index=True)  # SHA256 of validated dataset
    overall_health_score = Column(Integer, nullable=False, default=100)
    overall_risk = Column(String(20), nullable=False, default="LOW")  # LOW, MODERATE, HIGH, CRITICAL
    analysis_version = Column(String(20), nullable=False, default="3.0.0")
    versioning_json = Column(Text, nullable=True)  # Detailed version breakdown

    summary = Column(Text, nullable=True)
    doctor_summary = Column(Text, nullable=True)
    patient_summary = Column(Text, nullable=True)

    recommendations_json = Column(Text, nullable=True)
    evidence_json = Column(Text, nullable=True)
    missing_evidence_json = Column(Text, nullable=True)
    conflicts_json = Column(Text, nullable=True)
    organ_json = Column(Text, nullable=True)
    organ_dependency_json = Column(Text, nullable=True)
    timeline_json = Column(Text, nullable=True)
    timeline_deltas_json = Column(Text, nullable=True)
    graph_json = Column(Text, nullable=True)
    risk_json = Column(Text, nullable=True)
    conditions_json = Column(Text, nullable=True)
    confidence_json = Column(Text, nullable=True)
    parameter_influence_json = Column(Text, nullable=True)
    coverage_checklist_json = Column(Text, nullable=True)
    prompt_packages_json = Column(Text, nullable=True)

    quality_gate_status = Column(String(20), nullable=False, default="FULL")  # FULL, WARNING, LIMITED, BLOCKED
    confidence = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
