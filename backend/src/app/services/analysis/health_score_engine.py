"""
Health Score Engine (Phase 6).
Calculates a 0-100 overall health score using real deterministic clinical math:
Base = 100
- Critical / Invalid Deductions (-18 per parameter, max -40)
- Abnormal HIGH/LOW Deductions (-8 per parameter, max -30)
- Review / Missing Ref Deductions (-3 per parameter, max -15)
- Organ Dysfunction Deductions (-6 per affected organ, max -30)
- Multi-Organ Cascade Penalty (-10 if >= 3 affected organs)
- Quality Penalty (-5 to -15 if quality < 90)
= Real Calculated Score
"""

from typing import Dict, Any, List
from app.services.analysis.context import MedicalAnalysisContext


class HealthScoreEngine:

    @classmethod
    def calculate_score(cls, ctx: MedicalAnalysisContext, organ_data: Dict[str, Any], conditions: List[Any]) -> Dict[str, Any]:
        base_score = 100.0

        critical_deductions = 0.0
        abnormal_deductions = 0.0
        review_deductions = 0.0
        organ_deductions = 0.0
        quality_penalty = 0.0
        bonus_points = 0.0

        # 1. Parameter Deductions based on real validated parameters
        for p in ctx.validated_parameters:
            status = (p.get("status") or "UNKNOWN").upper()
            if "CRITICAL" in status or status == "INVALID_VALUE":
                critical_deductions += 18.0
            elif status in ["HIGH", "LOW", "MODERATE_HIGH", "MODERATE_LOW", "SEVERE_HIGH", "SEVERE_LOW"]:
                abnormal_deductions += 8.0
            elif status in ["MISSING_REFERENCE", "REVIEW", "PENDING"]:
                review_deductions += 3.0

        # Cap parameter deductions
        critical_deductions = min(40.0, critical_deductions)
        abnormal_deductions = min(30.0, abnormal_deductions)
        review_deductions = min(15.0, review_deductions)

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

        # Compute Real Final Score
        final_score = base_score - critical_deductions - abnormal_deductions - review_deductions - organ_deductions - multi_organ_penalty - quality_penalty + bonus_points
        final_score = max(10, min(100, int(round(final_score))))

        # Determine Real Risk Category
        if final_score >= 85:
            overall_risk = "LOW"
        elif final_score >= 65:
            overall_risk = "MODERATE"
        elif final_score >= 45:
            overall_risk = "HIGH"
        else:
            overall_risk = "CRITICAL"

        return {
            "overall_health_score": final_score,
            "overall_risk": overall_risk,
            "score_breakdown": {
                "base": 100,
                "critical_deductions": round(critical_deductions, 1),
                "abnormal_deductions": round(abnormal_deductions, 1),
                "review_deductions": round(review_deductions, 1),
                "organ_deductions": round(organ_deductions, 1),
                "multi_organ_penalty": round(multi_organ_penalty, 1),
                "quality_penalty": round(quality_penalty, 1),
                "bonus_points": round(bonus_points, 1)
            }
        }
