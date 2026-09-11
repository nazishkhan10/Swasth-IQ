"""
Phase 6 Clinical Intelligence & Explainable AI REST API Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.session import get_db
from app.services.analysis.medical_analysis_engine import MedicalAnalysisEngine

router = APIRouter(prefix="/analysis", tags=["Phase 6 Clinical Intelligence"])


@router.post("/{report_id}", response_model=Dict[str, Any])
def run_analysis(report_id: int, force: bool = Query(False), db: Session = Depends(get_db)):
    """Executes Phase 6 clinical reasoning engine or returns cached result if hash matches."""
    try:
        result = MedicalAnalysisEngine.run_analysis(db, report_id, force_recompute=force)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clinical analysis engine error: {str(e)}")


@router.get("/{report_id}", response_model=Dict[str, Any])
def get_analysis(report_id: int, db: Session = Depends(get_db)):
    """Fetches complete Phase 6 clinical intelligence analysis."""
    try:
        result = MedicalAnalysisEngine.run_analysis(db, report_id, force_recompute=False)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{report_id}/summary", response_model=Dict[str, Any])
def get_analysis_summary(report_id: int, db: Session = Depends(get_db)):
    """Fetches high-level executive summary & Health Score."""
    analysis = MedicalAnalysisEngine.run_analysis(db, report_id)
    return {
        "report_id": report_id,
        "overall_health_score": analysis["overall_health_score"],
        "overall_risk": analysis["overall_risk"],
        "quality_gate_status": analysis["quality_gate_status"],
        "confidence": analysis["confidence"],
        "summary": analysis["summary"]
    }


@router.get("/{report_id}/doctor", response_model=Dict[str, Any])
def get_doctor_summary(report_id: int, db: Session = Depends(get_db)):
    """Fetches formal clinician synthesis view."""
    analysis = MedicalAnalysisEngine.run_analysis(db, report_id)
    return {
        "report_id": report_id,
        "doctor_summary": analysis["doctor_summary"],
        "conditions": analysis["conditions"],
        "organ_panels": analysis["organ_panels"],
        "conflicts": analysis["conflicts"]
    }


@router.get("/{report_id}/patient", response_model=Dict[str, Any])
def get_patient_summary(report_id: int, db: Session = Depends(get_db)):
    """Fetches plain-language patient overview."""
    analysis = MedicalAnalysisEngine.run_analysis(db, report_id)
    return {
        "report_id": report_id,
        "patient_summary": analysis["patient_summary"],
        "recommendations": analysis["recommendations"][:3]
    }


@router.get("/{report_id}/recommendations", response_model=Dict[str, Any])
def get_recommendations(report_id: int, db: Session = Depends(get_db)):
    """Fetches 8-category grouped clinical recommendations."""
    analysis = MedicalAnalysisEngine.run_analysis(db, report_id)
    return {
        "report_id": report_id,
        "total_recommendations": len(analysis["recommendations"]),
        "recommendations": analysis["recommendations"]
    }


@router.get("/{report_id}/timeline", response_model=Dict[str, Any])
def get_timeline(report_id: int, db: Session = Depends(get_db)):
    """Fetches multi-dimensional timelines & parameter deltas."""
    analysis = MedicalAnalysisEngine.run_analysis(db, report_id)
    return {
        "report_id": report_id,
        "visit_timeline": analysis["timelines"],
        "parameter_deltas": analysis["timeline_deltas"]
    }


@router.get("/{report_id}/graph", response_model=Dict[str, Any])
def get_knowledge_graph(report_id: int, db: Session = Depends(get_db)):
    """Fetches 9-node Medical Knowledge Graph schema."""
    analysis = MedicalAnalysisEngine.run_analysis(db, report_id)
    return {
        "report_id": report_id,
        "graph": analysis["graph"]
    }


@router.get("/{report_id}/evidence", response_model=Dict[str, Any])
def get_evidence(report_id: int, db: Session = Depends(get_db)):
    """Fetches line-item evidence traceability matrix."""
    analysis = MedicalAnalysisEngine.run_analysis(db, report_id)
    return {
        "report_id": report_id,
        "total_evidence_items": len(analysis["evidence"]),
        "evidence": analysis["evidence"]
    }


@router.get("/{report_id}/conflicts", response_model=Dict[str, Any])
def get_conflicts(report_id: int, db: Session = Depends(get_db)):
    """Fetches clinical conflict alerts."""
    analysis = MedicalAnalysisEngine.run_analysis(db, report_id)
    return {
        "report_id": report_id,
        "conflicts": analysis["conflicts"]
    }


@router.get("/{report_id}/missing-evidence", response_model=Dict[str, Any])
def get_missing_evidence(report_id: int, db: Session = Depends(get_db)):
    """Fetches missing parameter checklist."""
    analysis = MedicalAnalysisEngine.run_analysis(db, report_id)
    return {
        "report_id": report_id,
        "missing_evidence": analysis["missing_evidence"],
        "coverage_checklist": analysis["coverage_checklist"]
    }


@router.get("/{report_id}/prompt-package/{target}", response_model=Dict[str, Any])
def get_prompt_package(report_id: int, target: str = "chat", db: Session = Depends(get_db)):
    """Fetches structured Phase 7 prompt package payload (doctor, patient, chat, rag, api)."""
    analysis = MedicalAnalysisEngine.run_analysis(db, report_id)
    pkgs = analysis.get("prompt_packages", {})
    if target not in pkgs:
        raise HTTPException(status_code=400, detail=f"Invalid target package '{target}'. Valid targets: doctor, patient, chat, rag, api")
    return pkgs[target]


@router.post("/{report_id}/retry", response_model=Dict[str, Any])
def retry_analysis(report_id: int, db: Session = Depends(get_db)):
    """Forces re-analysis execution bypassing cache."""
    return MedicalAnalysisEngine.run_analysis(db, report_id, force_recompute=True)
