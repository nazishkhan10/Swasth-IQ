"""
Health Score Engine (Phase 6).
Calculates a 0-100 overall health score using deterministic clinical math:
Base = 100
- Critical Deductions (-20 to -40)
- Organ Dysfunction Deductions (-10 to -30)
- Multi-Organ Cascade Penalty (-10)
- Data Quality / Warning Penalty (-5 to -15)
+ Recovery / Longitudinal Improvement Bonus (+5 to +10)
= Final Score
"""

from typing import Dict, Any, List
from app.services.analysis.context import MedicalAnalysisContext


class HealthScoreEngine:

    @classmethod
    def calculate_score(cls, ctx: MedicalAnalysisContext, organ_data: Dict[str, Any], conditions: List[Any]) -> Dict[str, Any]:
        base_score = 100.0

        critical_deductions = 0.0
        abnormal_deductions = 0.0
        organ_deductions = 0.0
        quality_penalty = 0.0
        bonus_points = 0.0

        # 1. Critical and Abnormal Parameter Deductions
        for p in ctx.validated_parameters:
            status = (p.get("status") or "UNKNOWN").upper()
            if "CRITICAL" in status or status == "INVALID_VALUE":
                critical_deductions += 18.0
            elif status in ["HIGH", "LOW", "MODERATE_HIGH", "MODERATE_LOW", "SEVERE_HIGH", "SEVERE_LOW"]:
                abnormal_deductions += 5.0

        # Cap parameter deductions
        critical_deductions = min(40.0, critical_deductions)
        abnormal_deductions = min(25.0, abnormal_deductions)

        # 2. Organ Panel Dysfunction Deductions
        affected_organs = organ_data.get("affected_organs", [])
        organ_deductions = len(affected_organs) * 6.0
        organ_deductions = min(30.0, organ_deductions)

        # 3. Multi-organ Penalty
        multi_organ_penalty = 10.0 if len(affected_organs) >= 3 else 0.0

        # 4. Data Quality / Warning Penalty
        if ctx.quality_score < 70:
            quality_penalty = 15.0
        elif ctx.quality_score < 90:
            quality_penalty = 5.0

        # 5. Longitudinal Improvement Bonus (if past visits demonstrate positive trend)
        if len(ctx.historical_reports) > 1:
            bonus_points += 5.0

        # Compute Final Score
        final_score = base_score - critical_deductions - abnormal_deductions - organ_deductions - multi_organ_penalty + bonus_points

        # If zero pathological conditions were detected and zero critical parameters exist, ensure score is optimal (>=90) and risk is LOW
        if not conditions and critical_deductions == 0.0:
            final_score = max(90.0, final_score)
            overall_risk = "LOW"
        elif final_score >= 85:
            overall_risk = "LOW"
        elif final_score >= 65:
            overall_risk = "MODERATE"
        elif final_score >= 45:
            overall_risk = "HIGH"
        else:
            overall_risk = "CRITICAL"

        final_score = max(0, min(100, int(round(final_score))))

        return {
            "overall_health_score": final_score,
            "overall_risk": overall_risk,
            "score_breakdown": {
                "base": 100,
                "critical_deductions": round(critical_deductions, 1),
                "abnormal_deductions": round(abnormal_deductions, 1),
                "organ_deductions": round(organ_deductions, 1),
                "multi_organ_penalty": round(multi_organ_penalty, 1),
                "bonus_points": round(bonus_points, 1)
            }
        }

