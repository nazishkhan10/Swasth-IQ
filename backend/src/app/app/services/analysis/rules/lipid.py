"""
Dyslipidemia & Lipid Disorder Rule Plugin.
Evaluates Total Cholesterol, LDL, HDL, Triglycerides, and VLDL.
"""

from typing import Optional, List, Dict, Any
from app.services.analysis.context import MedicalAnalysisContext
from app.services.analysis.rules.base_rule import BaseDiseaseRule, DetectedCondition


class LipidRule(BaseDiseaseRule):
    rule_id = "R_LIPID"
    rule_name = "Lipid Disorder Rule"
    version = "1.0.0"
    priority = "MEDIUM"
    supported_parameters = ["CHOL", "LDL", "HDL", "TRIG", "VLDL"]

    @classmethod
    def evaluate(cls, ctx: MedicalAnalysisContext) -> Optional[DetectedCondition]:
        params = {p.get("parameter_code"): p for p in ctx.validated_parameters if p.get("parameter_code")}

        chol_p = params.get("CHOL")
        ldl_p = params.get("LDL")
        hdl_p = params.get("HDL")
        trig_p = params.get("TRIG")

        chol_val = (chol_p.get("converted_value") if chol_p and chol_p.get("is_converted") else chol_p.get("numeric_value")) if chol_p else None
        ldl_val = (ldl_p.get("converted_value") if ldl_p and ldl_p.get("is_converted") else ldl_p.get("numeric_value")) if ldl_p else None
        hdl_val = (hdl_p.get("converted_value") if hdl_p and hdl_p.get("is_converted") else hdl_p.get("numeric_value")) if hdl_p else None
        trig_val = (trig_p.get("converted_value") if trig_p and trig_p.get("is_converted") else trig_p.get("numeric_value")) if trig_p else None

        if chol_val is None and ldl_val is None and trig_val is None:
            return None

        is_chol_high = chol_val and chol_val >= 200.0
        is_ldl_high = ldl_val and ldl_val >= 130.0
        is_trig_high = trig_val and trig_val >= 150.0

        if not (is_chol_high or is_ldl_high or is_trig_high):
            return None

        supporting = []
        evidence = []
        if is_chol_high:
            supporting.append("Total Cholesterol")
            evidence.append({"parameter": "Total Cholesterol", "value": str(chol_val), "unit": "mg/dL", "status": "HIGH"})
        if is_ldl_high:
            supporting.append("LDL-C")
            evidence.append({"parameter": "LDL-C", "value": str(ldl_val), "unit": "mg/dL", "status": "HIGH"})
        if is_trig_high:
            supporting.append("Triglycerides")
            evidence.append({"parameter": "Triglycerides", "value": str(trig_val), "unit": "mg/dL", "status": "HIGH"})

        severity = "HIGH" if (ldl_val and ldl_val >= 160.0) or (chol_val and chol_val >= 240.0) else "MODERATE"

        return DetectedCondition(
            condition_id="COND_DYSLIPIDEMIA",
            condition_name="Mixed Dyslipidemia" if (is_ldl_high and is_trig_high) else "Hypercholesterolemia",
            severity=severity,
            confidence=0.92,
            supporting_parameters=supporting,
            evidence=evidence,
            explanation={
                "why_detected": f"Elevated atherogenic lipid fractions: {', '.join(supporting)}.",
                "why_confidence": "Evaluated against ACC/AHA cholesterol clinical guidelines.",
                "why_recommendation": "Lowering atherogenic apoB lipoproteins reduces coronary artery disease risk.",
                "why_severity": f"Elevated cholesterol ({chol_val or 'N/A'} mg/dL) / LDL ({ldl_val or 'N/A'} mg/dL).",
                "why_risk": "Increased risk of atherosclerosis, myocardial infarction, and cerebrovascular disease."
            },
            recommendation_ids=["REC_LIPID_DIET", "REC_LIPID_EXERCISE", "REC_LIPID_CARDIOLOGY"],
            clinical_flags={
                "requires_followup": True,
                "repeat_test": True,
                "consult_specialist": severity == "HIGH",
                "emergency": False,
                "monitor": True
            }
        )
