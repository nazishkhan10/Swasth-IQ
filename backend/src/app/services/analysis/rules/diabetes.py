"""
Diabetes Mellitus & Prediabetes Rule Plugin.
Evaluates HbA1c, Fasting Glucose, Random Glucose, and Post-prandial Glucose.
"""

from typing import Optional, List, Dict, Any
from app.services.analysis.context import MedicalAnalysisContext
from app.services.analysis.rules.base_rule import BaseDiseaseRule, DetectedCondition


class DiabetesRule(BaseDiseaseRule):
    rule_id = "R_DIABETES"
    rule_name = "Diabetes Mellitus & Impaired Glycemia Rule"
    version = "1.1.0"
    priority = "HIGH"
    supported_parameters = ["HBA1C", "GLU_FAST", "GLU_RAND", "GLU_PP"]

    @classmethod
    def evaluate(cls, ctx: MedicalAnalysisContext) -> Optional[DetectedCondition]:
        params = {p.get("parameter_code"): p for p in ctx.validated_parameters if p.get("parameter_code")}

        hba1c_p = params.get("HBA1C")
        glu_fast_p = params.get("GLU_FAST") or params.get("GLU_RAND")

        hba1c_val = (hba1c_p.get("converted_value") if hba1c_p and hba1c_p.get("is_converted") else hba1c_p.get("numeric_value")) if hba1c_p else None
        glu_val = (glu_fast_p.get("converted_value") if glu_fast_p and glu_fast_p.get("is_converted") else glu_fast_p.get("numeric_value")) if glu_fast_p else None

        if hba1c_val is None and glu_val is None:
            return None

        # Overt Diabetes Mellitus
        if (hba1c_val and hba1c_val >= 6.5) or (glu_val and glu_val >= 126.0):
            supporting = []
            if hba1c_val and hba1c_val >= 6.5:
                supporting.append("HbA1c")
            if glu_val and glu_val >= 126.0:
                supporting.append("Fasting Blood Glucose")

            severity = "CRITICAL" if ((hba1c_val and hba1c_val >= 9.0) or (glu_val and glu_val >= 300.0)) else "HIGH"

            return DetectedCondition(
                condition_id="COND_DM2",
                condition_name="Uncontrolled Diabetes Mellitus" if severity == "CRITICAL" else "Diabetes Mellitus (Type 2)",
                severity=severity,
                confidence=0.95 if len(supporting) > 1 else 0.90,
                supporting_parameters=supporting,
                contradicting_parameters=[],
                evidence=[
                    {
                        "parameter": p_name,
                        "value": str(hba1c_val if p_name == "HbA1c" else glu_val),
                        "unit": "%" if p_name == "HbA1c" else "mg/dL",
                        "status": "HIGH"
                    }
                    for p_name in supporting
                ],
                explanation={
                    "why_detected": f"Elevated glycemic indicators: {', '.join([f'{s}' for s in supporting])}.",
                    "why_confidence": "Validated laboratory thresholds based on American Diabetes Association (ADA) criteria.",
                    "why_recommendation": "Glycemic control reduces long-term microvascular and macrovascular complications.",
                    "why_severity": "HbA1c >= 9.0% represents severe glycemic crisis risk." if severity == "CRITICAL" else "HbA1c >= 6.5% indicates diabetes mellitus.",
                    "why_risk": "High risk of progressive nephropathy, retinopathy, and cardiovascular disease."
                },
                recommendation_ids=["REC_DM_ENDOCRINE", "REC_DM_DIET", "REC_DM_MONITOR"],
                clinical_flags={
                    "requires_followup": True,
                    "repeat_test": True,
                    "consult_specialist": True,
                    "emergency": severity == "CRITICAL",
                    "monitor": True
                }
            )

        # Prediabetes
        if (hba1c_val and 5.7 <= hba1c_val < 6.5) or (glu_val and 100.0 <= glu_val < 126.0):
            supporting = []
            if hba1c_val and 5.7 <= hba1c_val < 6.5:
                supporting.append("HbA1c")
            if glu_val and 100.0 <= glu_val < 126.0:
                supporting.append("Fasting Blood Glucose")

            return DetectedCondition(
                condition_id="COND_PREDM",
                condition_name="Impaired Glycemia / Prediabetes",
                severity="MODERATE",
                confidence=0.88,
                supporting_parameters=supporting,
                evidence=[
                    {
                        "parameter": p_name,
                        "value": str(hba1c_val if p_name == "HbA1c" else glu_val),
                        "unit": "%" if p_name == "HbA1c" else "mg/dL",
                        "status": "HIGH"
                    }
                    for p_name in supporting
                ],
                explanation={
                    "why_detected": "Glycemic levels exceed normal ranges but are below overt diabetes thresholds.",
                    "why_confidence": "Conforms to ADA prediabetes reference intervals.",
                    "why_recommendation": "Early lifestyle intervention can prevent or delay progression to Type 2 Diabetes.",
                    "why_severity": "Moderate metabolic risk.",
                    "why_risk": "Elevated risk of progression to overt diabetes within 3-5 years without lifestyle changes."
                },
                recommendation_ids=["REC_PREDM_LIFESTYLE", "REC_PREDM_MONITOR"],
                clinical_flags={
                    "requires_followup": True,
                    "repeat_test": True,
                    "consult_specialist": False,
                    "emergency": False,
                    "monitor": True
                }
            )

        return None
