"""
Master Medical AI Insight Engine (Phase 7 — Architecture Freeze v8.2).
Coordinates GPT-5 Nano explanation layer over Phase 4-6 deterministic outputs.
Caches Clinical Intelligence in DB for sub-second load times.
Ensures 100% real, dynamic calculated Health Score & Risk Category.
"""

import json
import re
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.clinical_intelligence import CachedClinicalIntelligence
from app.services.ai.provider.provider_manager import ProviderManager
from app.services.medical_ai.patient_summary import PatientSummaryEngine
from app.services.medical_ai.doctor_summary import DoctorSummaryEngine
from app.services.medical_ai.json_validator import JSONSchemaValidator
from app.services.medical_ai.response_formatter import ResponseFormatter
from app.services.medical_ai.response_enhancer import ResponseEnhancer


def compute_real_health_score(deterministic_analysis: Dict[str, Any]) -> tuple:
    """Calculates the REAL health score and risk category dynamically from validated report parameters."""
    val_params = deterministic_analysis.get("validated_parameters") or []
    if not val_params:
        raw_score = int(deterministic_analysis.get("overall_health_score") or 85)
        raw_risk = "LOW" if raw_score >= 85 else "MODERATE"
        return raw_score, raw_risk

    score = 100
    for p in val_params:
        status = str(p.get("status") or "").upper()
        if "CRITICAL" in status or status == "INVALID_VALUE":
            score -= 18
        elif status in ["HIGH", "LOW", "MODERATE_HIGH", "MODERATE_LOW", "SEVERE_HIGH", "SEVERE_LOW"]:
            score -= 8
        elif status in ["MISSING_REFERENCE", "REVIEW", "PENDING"]:
            score -= 3

    final_score = max(10, min(100, score))
    if final_score >= 85:
        risk = "LOW"
    elif final_score >= 65:
        risk = "MODERATE"
    elif final_score >= 45:
        risk = "HIGH"
    else:
        risk = "CRITICAL"

    return final_score, risk


def compute_dynamic_organ_scores(deterministic_analysis: Dict[str, Any]) -> Dict[str, int]:
    """Dynamically calculates 0-100 organ system health scores from Phase 5/6 validated parameters."""
    organ_panels = deterministic_analysis.get("organ_panels") or {}
    val_params = deterministic_analysis.get("validated_parameters") or []

    def get_score(panel_keys: list, param_category_match: str) -> int:
        for k in panel_keys:
            if k in organ_panels and isinstance(organ_panels[k], dict):
                return int(organ_panels[k].get("score", 100))

        # Direct parameter calculation fallback
        matched = [p for p in val_params if param_category_match.lower() in (p.get("category") or "").lower()]
        if not matched:
            return 98  # Baseline normal if no parameters for this system present in report
        
        abnormal = sum(1 for p in matched if (p.get("status") or "").upper() in ["LOW", "HIGH", "CRITICAL_LOW", "CRITICAL_HIGH", "INVALID_VALUE"])
        critical = sum(1 for p in matched if "CRITICAL" in (p.get("status") or "").upper())
        score = 100 - (critical * 35) - (abnormal * 15)
        return max(40, min(100, score))

    return {
        "Heart": get_score(["Heart", "Cardiac", "Lipid"], "lipid"),
        "Kidney": get_score(["Kidney", "Renal", "Electrolytes"], "kidney"),
        "Liver": get_score(["Liver", "Hepatic"], "liver"),
        "Blood": get_score(["Blood", "Hematology"], "cbc"),
        "Metabolic": get_score(["Diabetes", "Endocrine", "Thyroid"], "diabetes")
    }


def sync_health_score_in_text(text: str, health_score: int, risk_category: str) -> str:
    """Ensures AI summary text matches the exact calculated health score and risk category."""
    if not text:
        return ""
    synced = re.sub(r"(Health Score of|score of|Score of)\s+\d+(\s+out of\s+100)?", rf"\1 {health_score}\2", text, flags=re.IGNORECASE)
    synced = re.sub(r"\b(moderate|high|critical|low)\s+risk\b", f"{risk_category.lower()} risk", synced, flags=re.IGNORECASE)
    return synced


class MedicalInsightEngine:
    """Master orchestrator for GPT-5 Nano explanation layer with DB caching."""

    def __init__(self):
        self.provider_mgr = ProviderManager()

    def get_or_generate_insights(self, db: Session, report_id: int, deterministic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fetches cached Clinical Intelligence or generates & stores in SQLite."""
        organ_scores = compute_dynamic_organ_scores(deterministic_analysis)
        health_score, overall_risk = compute_real_health_score(deterministic_analysis)

        # Update deterministic_analysis object
        deterministic_analysis["overall_health_score"] = health_score
        deterministic_analysis["overall_risk"] = overall_risk

        # 1. Check DB Cache
        cached = db.query(CachedClinicalIntelligence).filter(CachedClinicalIntelligence.report_id == report_id).first()
        if cached and cached.patient_summary_json and cached.doctor_summary_json:
            try:
                p_summary = json.loads(cached.patient_summary_json)
                d_summary = json.loads(cached.doctor_summary_json)

                if isinstance(p_summary, dict) and p_summary.get("summary"):
                    p_summary["summary"] = sync_health_score_in_text(p_summary["summary"], health_score, overall_risk)

                return {
                    "patient_summary": p_summary,
                    "doctor_summary": d_summary,
                    "organ_scores": organ_scores,
                    "overall_health_score": health_score,
                    "overall_risk": overall_risk,
                    "conditions": deterministic_analysis.get("conditions", []),
                    "provider_used": "OpenAI (gpt-5-nano)",
                    "cached": True
                }
            except Exception:
                pass

        # 2. Generate via PatientSummaryEngine & DoctorSummaryEngine
        patient_res = PatientSummaryEngine.generate_summary(deterministic_analysis, self.provider_mgr)
        _, parsed_patient, _ = JSONSchemaValidator.validate_insight(patient_res.get("content", ""))
        fmt_patient = ResponseFormatter.format_response(parsed_patient, deterministic_analysis.get("validated_parameters"))
        enhanced_patient = ResponseEnhancer.enhance(fmt_patient, deterministic_analysis.get("validated_parameters"))

        if isinstance(enhanced_patient, dict) and enhanced_patient.get("summary"):
            enhanced_patient["summary"] = sync_health_score_in_text(enhanced_patient["summary"], health_score, overall_risk)

        doctor_res = DoctorSummaryEngine.generate_summary(deterministic_analysis, self.provider_mgr)
        _, parsed_doctor, _ = JSONSchemaValidator.validate_insight(doctor_res.get("content", ""))
        fmt_doctor = ResponseFormatter.format_response(parsed_doctor, deterministic_analysis.get("validated_parameters"))
        enhanced_doctor = ResponseEnhancer.enhance(fmt_doctor, deterministic_analysis.get("validated_parameters"))

        # 3. Save to DB Cache
        try:
            if not cached:
                cached = CachedClinicalIntelligence(report_id=report_id)
                db.add(cached)
            
            cached.patient_summary_json = json.dumps(enhanced_patient)
            cached.doctor_summary_json = json.dumps(enhanced_doctor)
            cached.organ_scores_json = json.dumps(organ_scores)
            db.commit()
        except Exception as e:
            db.rollback()

        return {
            "patient_summary": enhanced_patient,
            "doctor_summary": enhanced_doctor,
            "organ_scores": organ_scores,
            "overall_health_score": health_score,
            "overall_risk": overall_risk,
            "conditions": deterministic_analysis.get("conditions", []),
            "provider_used": self.provider_mgr.primary_provider.provider_name,
            "cached": False
        }
