"""
Parameter Influence Score Engine (Phase 6).
Quantifies the relative influence % of each validated parameter across
detected conditions, organ panel scores, and recommendations.
"""

from typing import Dict, Any, List
from app.services.analysis.context import MedicalAnalysisContext


class ParameterInfluenceEngine:

    @classmethod
    def compute_influence(cls, ctx: MedicalAnalysisContext, conditions: List[Any], organ_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        param_counts: Dict[str, Dict[str, Any]] = {}

        for p in ctx.validated_parameters:
            name = p.get("parameter_name") or p.get("parameter_code") or "Unknown"
            param_counts[name] = {
                "parameter_name": name,
                "code": p.get("parameter_code"),
                "status": p.get("status"),
                "conditions_count": 0,
                "organs_count": 0,
                "score_weight": 0
            }

        # Count condition references
        for c in conditions:
            if not c:
                continue
            supp = getattr(c, "supporting_parameters", []) if hasattr(c, "supporting_parameters") else (c.get("supporting_parameters", []) if isinstance(c, dict) else [])
            for p_name in (supp or []):
                for key in param_counts:
                    if p_name.lower() in key.lower() or key.lower() in p_name.lower():
                        param_counts[key]["conditions_count"] += 1
                        param_counts[key]["score_weight"] += 20


        # Count organ references
        panels = organ_data.get("panels", {})
        for organ_name, panel in panels.items():
            affected = panel.get("affected_parameters", [])
            for aff_str in affected:
                for key in param_counts:
                    if key.lower() in aff_str.lower():
                        param_counts[key]["organs_count"] += 1
                        param_counts[key]["score_weight"] += 10

        total_weight = sum(item["score_weight"] for item in param_counts.values()) or 1.0

        results = []
        for name, item in param_counts.items():
            influence_pct = round((item["score_weight"] / total_weight) * 100.0, 1)
            results.append({
                "parameter_name": name,
                "parameter_code": item["code"],
                "status": item["status"],
                "influence_percentage": influence_pct,
                "conditions_linked": item["conditions_count"],
                "organs_linked": item["organs_count"]
            })

        results.sort(key=lambda x: x["influence_percentage"], reverse=True)
        return results
