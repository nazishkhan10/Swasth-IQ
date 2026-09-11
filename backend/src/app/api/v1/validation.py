"""
Phase 5 Medical Validation Router (Clinical Hardening).
All new fields exposed: conversion audit trail, OCR confidence, validation trace,
data quality score, and extended CSV export.
"""

import io
import csv
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.models.report import Report
from app.models.validated_medical_value import ValidatedMedicalValue
from app.models.parse_warning import ParseWarning
from app.api.v1.auth import get_current_user
from app.services.validation.validation_engine import ValidationEngine
from app.logs.logger import logger

router = APIRouter(prefix="/validation", tags=["Phase 5 Medical Validation Engine"])


def _get_user_report(report_id: int, db: Session, current_user: User) -> Report:
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report #{report_id} not found or access denied."
        )
    return report


def _serialize_record(r: ValidatedMedicalValue) -> Dict[str, Any]:
    """Full serialization of a ValidatedMedicalValue including all hardening fields."""
    return {
        "id": r.id,
        "medical_value_id": r.medical_value_id,
        "report_id": r.report_id,
        "parameter_name": r.parameter_name,
        "parameter_code": r.parameter_code,
        "category": r.category,
        # Values
        "raw_value": r.raw_value,
        "validated_value": r.validated_value,
        "raw_unit": r.raw_unit,
        "normalized_unit": r.normalized_unit,
        # Conversion audit
        "is_converted": r.is_converted,
        "converted_value": r.converted_value,
        "canonical_unit": r.canonical_unit,
        "conversion_factor": r.conversion_factor,
        # Reference
        "reference_low": r.reference_low,
        "reference_high": r.reference_high,
        "reference_text": r.reference_text,
        "reference_source": r.reference_source,
        # Clinical
        "status": r.status,
        "severity": r.severity,
        "critical": r.critical,
        # Confidence
        "ocr_confidence": r.ocr_confidence,
        "validation_confidence": r.validation_confidence,
        # Audit
        "validation_notes": r.validation_notes,
        "validation_trace": r.validation_trace,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/validate/{report_id}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def run_validation(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Executes Phase 5 Clinical Validation Pipeline on extracted Phase 4 report parameters."""
    report = _get_user_report(report_id, db, current_user)
    logger.info(f"[API] User '{current_user.email}' triggered Phase 5 validation for Report #{report_id}")
    return ValidationEngine.validate_report(db, report)


@router.get("/validate/{report_id}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def get_validation_results(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches validated medical dataset. Auto-runs validation if no data exists."""
    report = _get_user_report(report_id, db, current_user)
    data = ValidationEngine.get_validated_data(db, report)
    if data["status"] == "no_data":
        return ValidationEngine.validate_report(db, report)
    return data


@router.get("/validate/{report_id}/summary", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def get_validation_summary(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches clinical validation summary: Normal/Low/High/Critical/Invalid/Qualitative counts."""
    report = _get_user_report(report_id, db, current_user)
    return ValidationEngine.get_validation_summary(db, report)


@router.get("/validate/{report_id}/critical", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
def get_critical_values(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches critical clinical alert items flagged by the Critical Rules Engine."""
    report = _get_user_report(report_id, db, current_user)
    records = db.query(ValidatedMedicalValue).filter(
        ValidatedMedicalValue.report_id == report.id,
        ValidatedMedicalValue.critical == True
    ).all()
    return [_serialize_record(r) for r in records]


@router.get("/validate/{report_id}/quality", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def get_quality_score(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns the data quality score and breakdown for Phase 6 AI gating."""
    report = _get_user_report(report_id, db, current_user)
    records = db.query(ValidatedMedicalValue).filter(
        ValidatedMedicalValue.report_id == report.id
    ).all()
    warnings = db.query(ParseWarning).filter(ParseWarning.report_id == report.id).all()

    if not records:
        return {"score": 0, "breakdown": {}, "ai_ready": False}

    from app.models.patient_metadata import PatientMetadata
    patient = db.query(PatientMetadata).filter(PatientMetadata.report_id == report.id).first()

    n = len(records)
    invalid = sum(1 for r in records if r.status in ("INVALID_UNIT", "INVALID_VALUE", "INVALID"))
    missing_ref = sum(1 for r in records if r.reference_source == "UNKNOWN")
    missing_unit = sum(1 for r in records if not r.normalized_unit)
    low_ocr = sum(1 for r in records if (r.ocr_confidence or 1.0) < 0.70)
    converted = sum(1 for r in records if r.is_converted)
    avg_conf = sum(r.validation_confidence for r in records) / n
    has_demographics = bool(patient and (patient.age or patient.gender))

    score = 100
    score -= (invalid / n) * 30
    score -= (missing_ref / n) * 15
    score -= (missing_unit / n) * 10
    score -= (low_ocr / n) * 15
    score -= (1 - avg_conf) * 20
    if not has_demographics:
        score -= 5
    score = max(0, min(100, round(score)))

    return {
        "score": score,
        "ai_ready": score >= 60,
        "ai_blocked_reason": None if score >= 60 else f"Data quality score {score}/100 is below threshold (60)",
        "breakdown": {
            "total_parameters": n,
            "valid": n - invalid,
            "invalid": invalid,
            "converted": converted,
            "missing_references": missing_ref,
            "missing_units": missing_unit,
            "low_ocr_confidence_count": low_ocr,
            "average_validation_confidence": round(avg_conf, 2),
            "has_demographics": has_demographics,
            "total_warnings": len(warnings),
        }
    }


@router.post("/validate/{report_id}/retry", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def retry_validation(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Idempotently re-runs the Phase 5 Clinical Validation Engine."""
    report = _get_user_report(report_id, db, current_user)
    return ValidationEngine.validate_report(db, report)


@router.get("/export/{report_id}")
def export_validated_dataset(
    report_id: int,
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Exports validated clinical dataset in JSON or CSV format with full conversion audit trail."""
    report = _get_user_report(report_id, db, current_user)
    data = ValidationEngine.get_validated_data(db, report)
    validated_list = data.get("validated_values", [])

    if format == "json":
        return data

    # ── CSV Export ────────────────────────────────────────────────────────────
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Parameter Name", "Parameter Code", "Category",
        "Raw Value", "Original Unit",
        "Converted", "Converted Value", "Canonical Unit", "Conversion Factor",
        "Validated Value", "Normalized Unit",
        "Reference Low", "Reference High", "Reference Text", "Reference Source",
        "Status", "Severity", "Critical",
        "OCR Confidence", "Validation Confidence",
        "Notes", "Validation Trace"
    ])

    for row in validated_list:
        writer.writerow([
            row["id"], row["parameter_name"], row["parameter_code"], row["category"],
            row["raw_value"], row["raw_unit"],
            row["is_converted"], row.get("converted_value", ""), row.get("canonical_unit", ""), row.get("conversion_factor", ""),
            row["validated_value"], row["normalized_unit"],
            row["reference_low"], row["reference_high"], row["reference_text"], row["reference_source"],
            row["status"], row["severity"], row["critical"],
            row.get("ocr_confidence", ""), row["validation_confidence"],
            row.get("validation_notes", ""), row.get("validation_trace", "")
        ])

    output.seek(0)
    filename = f"validated_report_{report_id}.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
