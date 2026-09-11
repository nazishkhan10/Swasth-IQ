"""
Thyroid Dysfunction Rule Plugin.
Evaluates TSH, Free T3, and Free T4.
"""

from typing import Optional, List, Dict, Any
from app.services.analysis.context import MedicalAnalysisContext
from app.services.analysis.rules.base_rule import BaseDiseaseRule, DetectedCondition


class ThyroidRule(BaseDiseaseRule):
    rule_id = "R_THYROID"
    rule_name = "Thyroid Function Rule"
    version = "1.0.0"
    priority = "MEDIUM"
    supported_parameters = ["TSH", "FT3", "FT4"]

    @classmethod
    def evaluate(cls, ctx: MedicalAnalysisContext) -> Optional[DetectedCondition]:
        params = {p.get("parameter_code"): p for p in ctx.validated_parameters if p.get("parameter_code")}

        tsh_p = params.get("TSH")
        if not tsh_p:
            return None

        tsh_val = tsh_p.get("converted_value") if tsh_p.get("is_converted") else tsh_p.get("numeric_value")
        if tsh_val is None:
            return None

        # Hypothyroidism (High TSH)
        if tsh_val > 4.5:
            severity = "CRITICAL" if tsh_val >= 20.0 else ("HIGH" if tsh_val >= 10.0 else "MODERATE")
            cond_name = "Primary Hypothyroidism" if tsh_val >= 10.0 else "Subclinical Hypothyroidism"

            return DetectedCondition(
                condition_id="COND_HYPOTHYROID",
                condition_name=cond_name,
                severity=severity,
                confidence=0.92 if tsh_val >= 10.0 else 0.85,
                supporting_parameters=["TSH"],
                evidence=[{"parameter": "TSH", "value": str(tsh_val), "unit": "µIU/mL", "status": "HIGH"}],
                explanation={
                    "why_detected": f"TSH level of {tsh_val} µIU/mL exceeds normal physiological ceiling (4.5 µIU/mL).",
                    "why_confidence": "Single elevated TSH with validated reference range; full panel (FT4) recommended.",
                    "why_recommendation": "Thyroid hormone substitution restores metabolic homeostasis.",
                    "why_severity": f"TSH {tsh_val} indicates {cond_name.lower()}.",
                    "why_risk": "Risk of metabolic slowdown, dyslipidemia, and fatigue."
                },
                recommendation_ids=["REC_THYROID_ENDOCRINE", "REC_THYROID_FULL_PANEL"],
                clinical_flags={
                    "requires_followup": True,
                    "repeat_test": True,
                    "consult_specialist": tsh_val >= 10.0,
                    "emergency": severity == "CRITICAL",
                    "monitor": True
                }
            )

        # Hyperthyroidism (Low TSH)
        if tsh_val < 0.4:
            severity = "CRITICAL" if tsh_val < 0.01 else "MODERATE"
            return DetectedCondition(
                condition_id="COND_HYPERTHYROID",
                condition_name="Hyperthyroidism / Suppressed TSH",
                severity=severity,
                confidence=0.88,
                supporting_parameters=["TSH"],
                evidence=[{"parameter": "TSH", "value": str(tsh_val), "unit": "µIU/mL", "status": "LOW"}],
                explanation={
                    "why_detected": f"TSH level of {tsh_val} µIU/mL is below standard reference minimum (0.4 µIU/mL).",
                    "why_confidence": "Suppressed TSH suggests thyroid overactivity or exogenous hormone effect.",
                    "why_recommendation": "Endocrine evaluation prevents cardiac tachyarrhythmias and bone density loss.",
                    "why_severity": "Suppressed TSH requires evaluation.",
                    "why_risk": "Risk of atrial fibrillation, weight loss, and anxiety."
                },
                recommendation_ids=["REC_THYROID_ENDOCRINE", "REC_THYROID_FULL_PANEL"],
                clinical_flags={
                    "requires_followup": True,
                    "repeat_test": True,
                    "consult_specialist": True,
                    "emergency": severity == "CRITICAL",
                    "monitor": True
                }
            )

        return None
