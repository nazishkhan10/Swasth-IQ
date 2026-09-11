from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.models.report import Report
from app.models.medical_value import MedicalValue
from app.models.patient_metadata import PatientMetadata
from app.models.parse_warning import ParseWarning
from app.api.v1.auth import get_current_user
from app.services.parser.medical_parser import MedicalParser
from app.logs.logger import logger

router = APIRouter(prefix="/parser", tags=["Medical Data Extraction & Parsing"])


@router.post("/{report_id}", status_code=status.HTTP_200_OK)
def run_medical_parser(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run Phase 4 Medical Data Extraction & Parsing pipeline on OCR output.
    Returns structured dataset with patient metadata, parameters, units, ranges, and confidence.
    """
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report #{report_id} not found"
        )

    if report.ocr_status != "completed" or not report.ocr_version:
        logger.info(f"[API] OCR not completed for Report #{report_id}. Auto-executing Phase 3 OCR...")
        from app.services.ocr_service import OCRService
        OCRService.process_report_ocr(db=db, report=report)


    try:
        results = MedicalParser.parse_report(db=db, report=report)
        return results
    except Exception as e:
        logger.error(f"[API] Medical Parser failed for Report #{report_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Medical Parser processing failed: {str(e)}"
        )


@router.get("/{report_id}", status_code=status.HTTP_200_OK)
def get_parsed_data(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch complete structured medical dataset for report."""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report #{report_id} not found"
        )

    return MedicalParser.get_parsed_data(db=db, report=report)


@router.get("/{report_id}/patient", status_code=status.HTTP_200_OK)
def get_patient_metadata(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch patient demographics and laboratory header metadata."""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report #{report_id} not found"
        )

    patient = db.query(PatientMetadata).filter(PatientMetadata.report_id == report_id).first()
    if not patient:
        return {"report_id": report_id, "patient": None}

    return {
        "report_id": report_id,
        "patient": {
            "patient_name": patient.patient_name,
            "age": patient.age,
            "gender": patient.gender,
            "lab_name": patient.lab_name,
            "doctor_name": patient.doctor_name,
            "report_date": patient.report_date,
            "sample_date": patient.sample_date,
            "accession_number": patient.accession_number,
            "detected_report_type": patient.detected_report_type,
            "confidence": patient.confidence
        }
    }


@router.get("/{report_id}/parameters", status_code=status.HTTP_200_OK)
def get_medical_parameters(
    report_id: int,
    search: Optional[str] = Query(None, description="Search across parameter name, code, value, unit, page"),
    category: Optional[str] = Query(None, description="Filter by panel category: CBC, LFT, KFT, Lipid, Sugar, Thyroid, Vitamin, Urine"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch medical parameters with live multi-field search and panel category filters."""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report #{report_id} not found"
        )

    query = db.query(MedicalValue).filter(MedicalValue.report_id == report_id)

    if category and category.lower() != "all":
        query = query.filter(MedicalValue.category.ilike(f"%{category}%"))

    recs = query.order_by(MedicalValue.page_number, MedicalValue.id).all()

    if search:
        s_lower = search.lower().strip()
        filtered = []
        for r in recs:
            searchable = f"{r.parameter_name} {r.parameter_code or ''} {r.value} {r.unit or ''} {r.category or ''} page{r.page_number}".lower()
            if s_lower in searchable:
                filtered.append(r)
        recs = filtered

    return {
        "report_id": report_id,
        "total_parameters": len(recs),
        "parameters": [
            {
                "id": v.id,
                "page_number": v.page_number,
                "block_id": v.block_id,
                "parameter_name": v.parameter_name,
                "parameter_code": v.parameter_code,
                "category": v.category,
                "value": v.value,
                "numeric_value": v.numeric_value,
                "unit": v.unit,
                "reference_range": v.reference_range,
                "reference_context": v.reference_context,
                "reference_low": v.reference_low,
                "reference_high": v.reference_high,
                "status": v.status, # Pending Validation
                "confidence": v.confidence,
                "bbox": v.bbox
            }
            for v in recs
        ]
    }


@router.get("/{report_id}/warnings", status_code=status.HTTP_200_OK)
def get_parse_warnings(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch audit log warnings generated during medical parsing."""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report #{report_id} not found"
        )

    warnings = db.query(ParseWarning).filter(ParseWarning.report_id == report_id).order_by(ParseWarning.id).all()
    return {
        "report_id": report_id,
        "total_warnings": len(warnings),
        "warnings": [
            {
                "id": w.id,
                "page_number": w.page_number,
                "parameter_name": w.parameter_name,
                "warning_type": w.warning_type,
                "message": w.message,
                "created_at": w.created_at.isoformat() if w.created_at else None
            }
            for w in warnings
        ]
    }


@router.post("/{report_id}/retry", status_code=status.HTTP_200_OK)
def retry_medical_parser(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Force re-parse OCR data for specified report."""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report #{report_id} not found"
        )

    results = MedicalParser.parse_report(db=db, report=report)
    return results
