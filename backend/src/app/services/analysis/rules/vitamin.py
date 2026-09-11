"""
Vitamin D Deficiency Rule Plugin.
Evaluates 25-OH Vitamin D.
"""

from typing import Optional, List, Dict, Any
from app.services.analysis.context import MedicalAnalysisContext
from app.services.analysis.rules.base_rule import BaseDiseaseRule, DetectedCondition


class VitaminDRule(BaseDiseaseRule):
    rule_id = "R_VITD"
    rule_name = "Vitamin D Insufficiency & Deficiency Rule"
    version = "1.0.0"
    priority = "LOW"
    supported_parameters = ["VITD"]

    @classmethod
    def evaluate(cls, ctx: MedicalAnalysisContext) -> Optional[DetectedCondition]:
        params = {p.get("parameter_code"): p for p in ctx.validated_parameters if p.get("parameter_code")}

        vitd_p = params.get("VITD")
        if not vitd_p:
            return None

        vitd_val = vitd_p.get("converted_value") if vitd_p.get("is_converted") else vitd_p.get("numeric_value")
        if vitd_val is None:
            return None

        if vitd_val < 30.0:
            is_deficiency = vitd_val < 20.0
            cond_name = "Vitamin D Deficiency" if is_deficiency else "Vitamin D Insufficiency"
            severity = "HIGH" if vitd_val < 10.0 else ("MODERATE" if is_deficiency else "LOW")

            return DetectedCondition(
                condition_id="COND_VITD_DEFICIEN" if is_deficiency else "COND_VITD_INSUFF",
                condition_name=cond_name,
                severity=severity,
                confidence=0.90,
                supporting_parameters=["Vitamin D (25-OH)"],
                evidence=[{"parameter": "Vitamin D (25-OH)", "value": str(vitd_val), "unit": "ng/mL", "status": "LOW"}],
                explanation={
                    "why_detected": f"Vitamin D concentration ({vitd_val} ng/mL) is below optimal threshold (30 ng/mL).",
                    "why_confidence": "Endocrine Society clinical reference bounds.",
                    "why_recommendation": "Supplementation supports bone mineralization and immune function.",
                    "why_severity": f"Vitamin D level of {vitd_val} ng/mL constitutes {cond_name.lower()}.",
                    "why_risk": "Risk of osteomalacia, secondary hyperparathyroidism, and impaired bone turnover."
                },
                recommendation_ids=["REC_VITD_SUPPLEMENT", "REC_VITD_SUN", "REC_VITD_RECHECK"],
                clinical_flags={
                    "requires_followup": True,
                    "repeat_test": True,
                    "consult_specialist": False,
                    "emergency": False,
                    "monitor": True
                }
            )

        return None
