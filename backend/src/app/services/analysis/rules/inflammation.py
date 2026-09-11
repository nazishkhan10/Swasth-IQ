"""
Systemic Inflammation Rule Plugin.
Evaluates High-Sensitivity CRP (hs-CRP) and ESR.
"""

from typing import Optional, List, Dict, Any
from app.services.analysis.context import MedicalAnalysisContext
from app.services.analysis.rules.base_rule import BaseDiseaseRule, DetectedCondition


class InflammationRule(BaseDiseaseRule):
    rule_id = "R_INFLAM"
    rule_name = "Systemic Inflammation Rule"
    version = "1.0.0"
    priority = "MEDIUM"
    supported_parameters = ["HS_CRP", "ESR"]

    @classmethod
    def evaluate(cls, ctx: MedicalAnalysisContext) -> Optional[DetectedCondition]:
        params = {p.get("parameter_code"): p for p in ctx.validated_parameters if p.get("parameter_code")}

        crp_p = params.get("HS_CRP")
        if not crp_p:
            return None

        crp_val = crp_p.get("converted_value") if crp_p.get("is_converted") else crp_p.get("numeric_value")
        if crp_val is None:
            return None

        if crp_val > 3.0:
            severity = "CRITICAL" if crp_val >= 20.0 else ("HIGH" if crp_val >= 10.0 else "MODERATE")
            return DetectedCondition(
                condition_id="COND_INFLAMMATORY",
                condition_name="Severe Systemic Inflammation" if severity == "CRITICAL" else "Elevated Systemic Inflammatory Response",
                severity=severity,
                confidence=0.89,
                supporting_parameters=["hs-CRP"],
                evidence=[{"parameter": "hs-CRP", "value": str(crp_val), "unit": "mg/L", "status": "HIGH"}],
                explanation={
                    "why_detected": f"High-sensitivity CRP ({crp_val} mg/L) exceeds low-cardiovascular risk threshold (3.0 mg/L).",
                    "why_confidence": "AHA/CDC inflammatory biomarkers risk strata.",
                    "why_recommendation": "Investigating occult infection, autoimmune activity, or metabolic inflammation.",
                    "why_severity": f"hs-CRP {crp_val} mg/L reflects significant systemic inflammatory burden.",
                    "why_risk": "Elevated vascular inflammatory risk and acute phase reactivation."
                },
                recommendation_ids=["REC_INFLAM_INVESTIGATE", "REC_INFLAM_MONITOR"],
                clinical_flags={
                    "requires_followup": True,
                    "repeat_test": True,
                    "consult_specialist": severity in ["HIGH", "CRITICAL"],
                    "emergency": severity == "CRITICAL",
                    "monitor": True
                }
            )

        return None
