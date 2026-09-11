"""
Explain Condition Tool (Phase 7 AI Medical Tools).
Extracts detailed detected condition context from Phase 6 MedicalAnalysis.
"""

from typing import Dict, Any


class ExplainConditionTool:
    """Provides structured condition rationale context."""

    @classmethod
    def execute(cls, condition_name: str, detected_conditions: list) -> Dict[str, Any]:
        c_name = condition_name.strip().lower()
        matched = None
        for c in detected_conditions:
            if c_name in c.get("condition_name", "").lower():
                matched = c
                break

        if not matched:
            return {"found": False, "message": f"Condition '{condition_name}' not detected in analysis."}

        return {
            "found": True,
            "condition_name": matched.get("condition_name"),
            "severity": matched.get("severity"),
            "confidence": matched.get("confidence"),
            "explanation": matched.get("explanation"),
            "supporting_parameters": matched.get("supporting_parameters")
        }
