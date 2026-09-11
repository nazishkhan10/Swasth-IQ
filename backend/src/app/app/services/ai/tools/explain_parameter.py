"""
Explain Parameter Tool (Phase 7 AI Medical Tools).
Extracts detailed parameter explanation context from Phase 5 & 6 data.
"""

from typing import Dict, Any, Optional


class ExplainParameterTool:
    """Provides structured parameter lookup & explanation context."""

    @classmethod
    def execute(cls, parameter_name: str, validated_parameters: list) -> Dict[str, Any]:
        p_name = parameter_name.strip().lower()
        matched = None
        for p in validated_parameters:
            if (p.get("parameter_name", "").lower() == p_name or
                p.get("parameter_code", "").lower() == p_name):
                matched = p
                break

        if not matched:
            return {"found": False, "message": f"Parameter '{parameter_name}' not found in report."}

        return {
            "found": True,
            "parameter_name": matched.get("parameter_name"),
            "value": matched.get("numeric_value", matched.get("validated_value")),
            "unit": matched.get("normalized_unit", matched.get("unit")),
            "status": matched.get("status"),
            "ref_range": f"{matched.get('ref_range_low', matched.get('reference_low'))} - {matched.get('ref_range_high', matched.get('reference_high'))}",
            "confidence": matched.get("validation_confidence", 0.95)
        }
