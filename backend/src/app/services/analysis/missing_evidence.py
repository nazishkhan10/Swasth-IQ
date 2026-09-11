"""
Missing Evidence Engine (Phase 6).
Identifies missing parameters required to confirm incomplete conditions
(e.g., Isolated abnormal TSH without Free T4/T3, or Elevated glucose without HbA1c).
Outputs diagnostic testing recommendations.
"""

from typing import List, Dict, Any
from app.services.analysis.context import MedicalAnalysisContext


REQUIRED_DIAGNOSTIC_PANELS = {
    "Thyroid Profile": {
        "primary": ["TSH"],
        "required_confirmation": ["FT4", "FT3"],
        "recommendation": "Order Free T4 and Free T3 to confirm primary vs secondary thyroid gland etiology."
    },
    "Comprehensive Diabetes Panel": {
        "primary": ["GLU_FAST"],
        "required_confirmation": ["HBA1C"],
        "recommendation": "Order Glycated Hemoglobin (HbA1c) to establish 90-day mean glycemic control."
    },
    "Renal Function Panel": {
        "primary": ["CREAT"],
        "required_confirmation": ["EGFR", "BUN"],
        "recommendation": "Calculate eGFR (CKD-EPI 2021) and measure Blood Urea Nitrogen to assess filtration."
    },
    "Complete Lipid Profile": {
        "primary": ["CHOL"],
        "required_confirmation": ["LDL", "HDL", "TRIG"],
        "recommendation": "Order complete lipid fraction panel (LDL, HDL, Triglycerides) for atherogenic risk profiling."
    }
}


class MissingEvidenceEngine:

    @classmethod
    def evaluate_missing_evidence(cls, ctx: MedicalAnalysisContext) -> List[Dict[str, Any]]:
        present_codes = set(p.get("parameter_code") for p in ctx.validated_parameters if p.get("parameter_code"))

        missing_list = []

        for panel_name, reqs in REQUIRED_DIAGNOSTIC_PANELS.items():
            primary_present = any(code in present_codes for code in reqs["primary"])
            if not primary_present:
                continue

            missing_confirmations = [code for code in reqs["required_confirmation"] if code not in present_codes]
            if missing_confirmations:
                found_primaries = [c for c in reqs["primary"] if c in present_codes]
                missing_list.append({
                    "panel_name": panel_name,
                    "found_parameters": found_primaries,
                    "missing_parameters": missing_confirmations,
                    "recommendation": reqs["recommendation"],
                    "impact": f"Diagnostic confidence reduced for {panel_name} without confirmation."
                })

        return missing_list
