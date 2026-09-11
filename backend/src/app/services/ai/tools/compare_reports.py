"""
Compare Reports Tool (Phase 7 AI Medical Tools).
Computes parameter deltas and trajectory changes across current vs historical report visits.
"""

from typing import Dict, Any, List


class CompareReportsTool:
    """Computes comparative trajectory deltas between visits."""

    @classmethod
    def execute(cls, current_params: List[Dict[str, Any]], previous_params: List[Dict[str, Any]]) -> Dict[str, Any]:
        prev_map = {p.get("parameter_code", p.get("parameter_name")): p for p in previous_params}
        deltas = []

        for curr in current_params:
            code = curr.get("parameter_code", curr.get("parameter_name"))
            curr_val = curr.get("numeric_value", curr.get("validated_value"))
            prev = prev_map.get(code)

            if prev and curr_val is not None:
                prev_val = prev.get("numeric_value", prev.get("validated_value"))
                if prev_val is not None:
                    abs_change = round(curr_val - prev_val, 2)
                    pct_change = round((abs_change / prev_val) * 100, 1) if prev_val != 0 else 0
                    trend = "STABLE"
                    if abs_change > 0:
                        trend = "INCREASED"
                    elif abs_change < 0:
                        trend = "DECREASED"

                    deltas.append({
                        "parameter": curr.get("parameter_name"),
                        "current": curr_val,
                        "previous": prev_val,
                        "unit": curr.get("normalized_unit", curr.get("unit")),
                        "abs_change": abs_change,
                        "pct_change": pct_change,
                        "trend": trend
                    })

        return {"deltas": deltas, "compared_count": len(deltas)}
