"""
Phase 5 Medical Validation Router.
Exposes endpoints for running medical validation, fetching summary metrics, listing critical alerts,
retrying validation, and exporting validated clinical datasets in JSON and CSV formats.
"""

import io
import csv
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.models.report import Report
from app.models.validated_medical_value import ValidatedMedicalValue
from app.api.deps import get_current_user
from app.services.validation.validation_engine import ValidationEngine
from app.logs.logger import logger

router = APIRouter()


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


@router.post("/validate/{report_id}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def run_validation(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Executes Phase 5 Medical Validation Engine on extracted Phase 4 report parameters."""
    report = _get_user_report(report_id, db, current_user)
    return ValidationEngine.validate_report(db, report)


@router.get("/validate/{report_id}", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def get_validation_results(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches Phase 5 validated medical values for a report."""
    report = _get_user_report(report_id, db, current_user)
    data = ValidationEngine.get_validated_data(db, report)
    if data["status"] == "no_data":
        # Auto-run validation if not yet validated
        return ValidationEngine.validate_report(db, report)
    return data


@router.get("/validate/{report_id}/summary", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def get_validation_summary(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches high-level clinical validation summary metrics (Normal, Low, High, Critical counts)."""
    report = _get_user_report(report_id, db, current_user)
    return ValidationEngine.get_validation_summary(db, report)


@router.get("/validate/{report_id}/critical", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
def get_critical_values(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches critical clinical alert items flagged by Phase 5 Critical Rules Engine."""
    report = _get_user_report(report_id, db, current_user)
    records = db.query(ValidatedMedicalValue).filter(
        ValidatedMedicalValue.report_id == report.id,
        ValidatedMedicalValue.critical == True
    ).all()

    return [{
        "id": r.id,
        "parameter_name": r.parameter_name,
        "parameter_code": r.parameter_code,
        "raw_value": r.raw_value,
        "normalized_unit": r.normalized_unit,
        "reference_text": r.reference_text,
        "status": r.status,
        "severity": r.severity,
        "validation_notes": r.validation_notes
    } for r in records]


@router.post("/validate/{report_id}/retry", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def retry_validation(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Idempotently re-runs Phase 5 Medical Validation Engine."""
    report = _get_user_report(report_id, db, current_user)
    return ValidationEngine.validate_report(db, report)


@router.get("/export/{report_id}")
def export_validated_dataset(
    report_id: int,
    format: str = Query("json", regex="^(json|csv)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Exports validated clinical dataset in JSON or CSV format."""
    report = _get_user_report(report_id, db, current_user)
    data = ValidationEngine.get_validated_data(db, report)
    validated_list = data.get("validated_values", [])

    if format == "json":
        return data

    # CSV Export Stream
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Parameter Name", "Parameter Code", "Category", "Raw Value",
        "Validated Value", "Normalized Unit", "Reference Low", "Reference High",
        "Reference Text", "Reference Source", "Status", "Severity", "Critical", "Notes"
    ])

    for row in validated_list:
        writer.writerow([
            row["id"], row["parameter_name"], row["parameter_code"], row["category"], row["raw_value"],
            row["validated_value"], row["normalized_unit"], row["reference_low"], row["reference_high"],
            row["reference_text"], row["reference_source"], row["status"], row["severity"], row["critical"], row.get("validation_notes", "")
        ])

    output.seek(0)
    filename = f"validated_report_{report_id}.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
