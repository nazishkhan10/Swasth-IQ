"""
Clinical Coverage Checklist Engine (Phase 6).
Evaluates required vs found parameter coverage per disease panel.
"""

from typing import Dict, Any, List
from app.services.analysis.context import MedicalAnalysisContext

CLINICAL_PANELS = {
    "Diabetes Panel": ["HBA1C", "GLU_FAST"],
    "Renal Panel": ["CREAT", "EGFR", "BUN"],
    "Lipid Panel": ["CHOL", "LDL", "HDL", "TRIG"],
    "Thyroid Panel": ["TSH", "FT4", "FT3"],
    "Hematology CBC Panel": ["HGB", "RBC", "WBC", "PLT"],
    "Inflammatory Panel": ["HS_CRP"],
    "Vitamin Panel": ["VITD"]
}


class CoverageChecklistEngine:

    @classmethod
    def evaluate_coverage(cls, ctx: MedicalAnalysisContext) -> List[Dict[str, Any]]:
        present_codes = set(p.get("parameter_code") for p in ctx.validated_parameters if p.get("parameter_code"))

        checklists = []
        for panel_name, req_codes in CLINICAL_PANELS.items():
            found = [c for c in req_codes if c in present_codes]
            missing = [c for c in req_codes if c not in present_codes]
            total = len(req_codes)
            coverage_pct = round((len(found) / total) * 100.0, 1)

            checklists.append({
                "panel_name": panel_name,
                "total_required": total,
                "found_count": len(found),
                "missing_count": len(missing),
                "coverage_percentage": coverage_pct,
                "found_parameters": found,
                "missing_parameters": missing,
                "status": "COMPLETE" if coverage_pct == 100.0 else ("PARTIAL" if len(found) > 0 else "MISSING")
            })

        return checklists
