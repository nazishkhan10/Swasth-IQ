"""
Risk Assessment Engine (Phase 6).
Evaluates current and projected clinical risks across 5 domains:
Diabetes, Renal, Cardiovascular, Thyroid, and Metabolic Syndrome.
"""

from typing import Dict, Any, List
from app.services.analysis.context import MedicalAnalysisContext


class RiskEngine:

    @classmethod
    def evaluate_risks(cls, ctx: MedicalAnalysisContext, conditions: List[Any], organ_data: Dict[str, Any]) -> Dict[str, Any]:
        cond_ids = set()
        for c in conditions:
            cid = getattr(c, "condition_id", None) if hasattr(c, "condition_id") else c.get("condition_id")
            if cid:
                cond_ids.add(cid)

        risks = {
            "Diabetes Progression": {
                "current_risk": "HIGH" if "COND_DM2" in cond_ids else ("MODERATE" if "COND_PREDM" in cond_ids else "LOW"),
                "future_risk": "VERY HIGH" if "COND_DM2" in cond_ids else ("HIGH" if "COND_PREDM" in cond_ids else "LOW"),
                "trend": "Worsening" if "COND_DM2" in cond_ids else "Stable",
                "confidence": 0.92
            },
            "Renal Disease / CKD": {
                "current_risk": "CRITICAL" if any("Stage 4" in str(getattr(c, "condition_name", "")) or "Stage 5" in str(getattr(c, "condition_name", "")) for c in conditions) else ("HIGH" if "COND_CKD" in cond_ids else "LOW"),
                "future_risk": "HIGH" if "COND_CKD" in cond_ids else "LOW",
                "trend": "Escalating" if "COND_CKD" in cond_ids else "Stable",
                "confidence": 0.90
            },
            "Cardiovascular Disease": {
                "current_risk": "HIGH" if "COND_DYSLIPIDEMIA" in cond_ids else "LOW",
                "future_risk": "HIGH" if ("COND_DYSLIPIDEMIA" in cond_ids or "COND_DM2" in cond_ids) else "LOW",
                "trend": "Stable",
                "confidence": 0.88
            },
            "Thyroid Dysfunction": {
                "current_risk": "MODERATE" if ("COND_HYPOTHYROID" in cond_ids or "COND_HYPERTHYROID" in cond_ids) else "LOW",
                "future_risk": "MODERATE" if ("COND_HYPOTHYROID" in cond_ids or "COND_HYPERTHYROID" in cond_ids) else "LOW",
                "trend": "Stable",
                "confidence": 0.85
            },
            "Metabolic Syndrome": {
                "current_risk": "HIGH" if (len(cond_ids.intersection({"COND_DM2", "COND_DYSLIPIDEMIA", "COND_CKD"})) >= 2) else "LOW",
                "future_risk": "HIGH" if (len(cond_ids) > 1) else "LOW",
                "trend": "Multi-system Involvement",
                "confidence": 0.90
            }
        }

        return risks
