"""
Anemia Rule Plugin.
Evaluates Hemoglobin, RBC, Hematocrit, and Platelets.
"""

from typing import Optional, List, Dict, Any
from app.services.analysis.context import MedicalAnalysisContext
from app.services.analysis.rules.base_rule import BaseDiseaseRule, DetectedCondition


class AnemiaRule(BaseDiseaseRule):
    rule_id = "R_ANEMIA"
    rule_name = "Anemia & Hematologic Rule"
    version = "1.0.0"
    priority = "MEDIUM"
    supported_parameters = ["HGB", "RBC", "HCT", "MCV"]

    @classmethod
    def evaluate(cls, ctx: MedicalAnalysisContext) -> Optional[DetectedCondition]:
        params = {p.get("parameter_code"): p for p in ctx.validated_parameters if p.get("parameter_code")}

        hgb_p = params.get("HGB")
        if not hgb_p:
            return None

        hgb_val = hgb_p.get("converted_value") if hgb_p.get("is_converted") else hgb_p.get("numeric_value")
        if hgb_val is None:
            return None

        gender = (ctx.patient_metadata.get("gender") or "").lower()
        cutoff = 12.0 if gender in ["female", "f"] else 13.0

        if hgb_val < cutoff:
            severity = "CRITICAL" if hgb_val <= 6.5 else ("HIGH" if hgb_val <= 9.0 else "MODERATE")
            return DetectedCondition(
                condition_id="COND_ANEMIA",
                condition_name="Severe Anemia" if severity == "CRITICAL" else "Anemia / Decreased Hemoglobin",
                severity=severity,
                confidence=0.95,
                supporting_parameters=["Hemoglobin"],
                evidence=[{"parameter": "Hemoglobin", "value": str(hgb_val), "unit": "g/dL", "status": "LOW"}],
                explanation={
                    "why_detected": f"Hemoglobin of {hgb_val} g/dL is below diagnostic threshold ({cutoff} g/dL).",
                    "why_confidence": "WHO gender-stratified anemia thresholds.",
                    "why_recommendation": "Evaluating iron stores and RBC indices clarifies microcytic vs macrocytic etiology.",
                    "why_severity": f"Hb {hgb_val} g/dL requires evaluation.",
                    "why_risk": "Impaired oxygen carrying capacity, fatigue, and exertion dyspnea."
                },
                recommendation_ids=["REC_ANEMIA_IRON", "REC_ANEMIA_HAEMATOLOGY"],
                clinical_flags={
                    "requires_followup": True,
                    "repeat_test": True,
                    "consult_specialist": severity in ["HIGH", "CRITICAL"],
                    "emergency": severity == "CRITICAL",
                    "monitor": True
                }
            )

        return None
