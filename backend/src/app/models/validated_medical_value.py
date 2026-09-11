"""
Validated Medical Value Database Model (Phase 5 — Clinical Hardening).
Stores clinically validated medical parameters with full unit conversion audit trail,
OCR confidence propagation, per-parameter validation trace, and data quality fields.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.base import Base


class ValidatedMedicalValue(Base):
    """Represents a validated medical measurement — output of Phase 5 Clinical Validation Engine."""

    __tablename__ = "validated_medical_values"

    id = Column(Integer, primary_key=True, index=True)
    medical_value_id = Column(Integer, ForeignKey("medical_values.id", ondelete="SET NULL"), nullable=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)

    # ── Parameter Identity ───────────────────────────────────────────────────
    parameter_name = Column(String(255), nullable=False)
    parameter_code = Column(String(100), nullable=True, index=True)
    category = Column(String(100), nullable=True)

    # ── Raw Values ───────────────────────────────────────────────────────────
    raw_value = Column(String(255), nullable=False)         # Original OCR string
    validated_value = Column(Float, nullable=True)          # Parsed float (pre-conversion)
    raw_unit = Column(String(100), nullable=True)           # OCR unit string
    normalized_unit = Column(String(100), nullable=True)    # Canonicalized unit

    # ── Unit Conversion Audit ────────────────────────────────────────────────
    is_converted = Column(Boolean, nullable=False, default=False)   # True if unit was converted
    converted_value = Column(Float, nullable=True)                  # Value after conversion
    canonical_unit = Column(String(100), nullable=True)             # Post-conversion unit
    conversion_factor = Column(Float, nullable=True)                # Multiplier applied

    # ── Reference Range ──────────────────────────────────────────────────────
    reference_low = Column(Float, nullable=True)
    reference_high = Column(Float, nullable=True)
    reference_text = Column(String(255), nullable=True)
    reference_source = Column(String(50), nullable=False, default="REPORT")
    # REPORT | STANDARD_DATABASE | FALLBACK_FROM_REPORT | UNKNOWN

    # ── Clinical Classification ──────────────────────────────────────────────
    status = Column(String(50), nullable=False, default="UNKNOWN")
    # NORMAL | LOW | HIGH | CRITICAL_LOW | CRITICAL_HIGH
    # INVALID_UNIT | INVALID_VALUE | QUALITATIVE | MISSING_REFERENCE | UNKNOWN | INVALID

    severity = Column(String(50), nullable=False, default="UNKNOWN")
    # NORMAL | MILD | MODERATE | SEVERE | CRITICAL | QUALITATIVE | UNKNOWN

    critical = Column(Boolean, nullable=False, default=False)

    # ── Confidence ───────────────────────────────────────────────────────────
    ocr_confidence = Column(Float, nullable=True)           # Raw OCR engine confidence
    validation_confidence = Column(Float, nullable=False, default=1.0)  # Always ≤ ocr_confidence

    # ── Audit Trail ──────────────────────────────────────────────────────────
    validation_notes = Column(Text, nullable=True)          # Human-readable summary
    validation_trace = Column(Text, nullable=True)          # S1 | S2 | ... stage-by-stage log

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # ── Relationships ────────────────────────────────────────────────────────
    report = relationship("Report", backref="validated_medical_values")
    medical_value = relationship("MedicalValue", backref="validated_records")

    def __repr__(self):
        conv = f" (conv→{self.converted_value} {self.canonical_unit})" if self.is_converted else ""
        return (
            f"<ValidatedMedicalValue {self.parameter_code}: "
            f"{self.raw_value} {self.normalized_unit}{conv} ({self.status})>"
        )
