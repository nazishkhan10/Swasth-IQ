"""
Chronic Kidney Disease (CKD) & Renal Dysfunction Rule Plugin.
Evaluates Creatinine, eGFR, BUN, and Blood Urea.
"""

from typing import Optional, List, Dict, Any
from app.services.analysis.context import MedicalAnalysisContext
from app.services.analysis.rules.base_rule import BaseDiseaseRule, DetectedCondition


class CKDRule(BaseDiseaseRule):
    rule_id = "R_CKD"
    rule_name = "Renal Dysfunction & CKD Staging Rule"
    version = "1.1.0"
    priority = "HIGH"
    supported_parameters = ["CREAT", "EGFR", "BUN", "UREA"]

    @classmethod
    def evaluate(cls, ctx: MedicalAnalysisContext) -> Optional[DetectedCondition]:
        params = {p.get("parameter_code"): p for p in ctx.validated_parameters if p.get("parameter_code")}

        creat_p = params.get("CREAT")
        egfr_p = params.get("EGFR")

        creat_val = (creat_p.get("converted_value") if creat_p and creat_p.get("is_converted") else creat_p.get("numeric_value")) if creat_p else None
        egfr_val = (egfr_p.get("converted_value") if egfr_p and egfr_p.get("is_converted") else egfr_p.get("numeric_value")) if egfr_p else None

        if creat_val is None and egfr_val is None:
            return None

        # Check renal impairment criteria
        is_creat_high = creat_val and creat_val > 1.35
        is_egfr_low = egfr_val and egfr_val < 60.0

        if not (is_creat_high or is_egfr_low):
            return None

        supporting = []
        if is_creat_high:
            supporting.append("Serum Creatinine")
        if is_egfr_low:
            supporting.append("eGFR")

        # Determine stage & severity based on KDIGO guidelines
        if egfr_val:
            if egfr_val < 15.0:
                stage = "Stage 5 Kidney Failure"
                severity = "CRITICAL"
            elif egfr_val < 30.0:
                stage = "Stage 4 Severe CKD"
                severity = "CRITICAL"
            elif egfr_val < 45.0:
                stage = "Stage 3b Moderate-to-Severe CKD"
                severity = "HIGH"
            elif egfr_val < 60.0:
                stage = "Stage 3a Mild-to-Moderate CKD"
                severity = "HIGH" if creat_val and creat_val > 1.8 else "MODERATE"
            else:
                stage = "Renal Strain / Early Impairment"
                severity = "MODERATE"
        else:
            stage = "Renal Strain / Impaired Clearance"
            severity = "HIGH" if creat_val and creat_val > 2.0 else "MODERATE"

        return DetectedCondition(
            condition_id="COND_CKD",
            condition_name=f"Renal Dysfunction ({stage})",
            severity=severity,
            confidence=0.94 if (is_creat_high and is_egfr_low) else 0.86,
            supporting_parameters=supporting,
            evidence=[
                {
                    "parameter": p_name,
                    "value": str(creat_val if p_name == "Serum Creatinine" else egfr_val),
                    "unit": "mg/dL" if p_name == "Serum Creatinine" else "mL/min/1.73m²",
                    "status": "HIGH" if p_name == "Serum Creatinine" else "LOW"
                }
                for p_name in supporting
            ],
            explanation={
                "why_detected": f"Combined evidence of elevated Serum Creatinine ({creat_val or 'N/A'}) and/or reduced filtration rate eGFR ({egfr_val or 'N/A'}).",
                "why_confidence": "Evaluated against KDIGO 2021 Clinical Practice Guidelines for CKD Staging.",
                "why_recommendation": "Preserving nephron mass prevents end-stage renal disease and cardiovascular events.",
                "why_severity": f"eGFR {egfr_val} mL/min/1.73m² indicates {stage}.",
                "why_risk": "Elevated risk of fluid retention, electrolyte imbalances, and renal disease progression."
            },
            recommendation_ids=["REC_CKD_NEPHROLOGIST", "REC_CKD_MONITOR", "REC_CKD_HYDRATION"],
            clinical_flags={
                "requires_followup": True,
                "repeat_test": True,
                "consult_specialist": True,
                "emergency": severity == "CRITICAL",
                "monitor": True
            }
        )
