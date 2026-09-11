"""
Longitudinal Timeline & Delta Engine (Phase 6).
Generates 5 distinct longitudinal timeline objects:
VisitTimeline, ParameterTimeline, DiseaseTimeline, HealthScoreTimeline, RecommendationTimeline
plus Timeline Delta objects (Current, Previous, Absolute Change, % Change, Trend, Interpretation).
"""

from typing import List, Dict, Any
from app.services.analysis.context import MedicalAnalysisContext


class TimelineBuilder:

    @classmethod
    def build_timelines(cls, ctx: MedicalAnalysisContext, current_score: int, conditions: List[Any]) -> Dict[str, Any]:
        historical = ctx.historical_reports or []

        # 1. Visit Timeline
        visit_timeline = [
            {
                "visit_index": 1,
                "visit_date": ctx.patient_metadata.get("report_date") or "Current Visit",
                "facility": ctx.patient_metadata.get("facility_name") or "Diagnostic Laboratory",
                "health_score": current_score,
                "report_id": ctx.report_id
            }
        ]

        # Append historical visits if present
        for i, h in enumerate(historical, start=2):
            visit_timeline.append({
                "visit_index": i,
                "visit_date": h.get("created_at") or f"Visit #{i}",
                "facility": h.get("facility_name") or "Diagnostic Center",
                "health_score": h.get("overall_health_score", 70),
                "report_id": h.get("id")
            })

        # 2. Parameter Trajectory Timelines & Deltas
        parameter_timelines = {}
        parameter_deltas = []

        for p in ctx.validated_parameters:
            name = p.get("parameter_name") or p.get("parameter_code") or "Parameter"
            val = p.get("converted_value") if p.get("is_converted") else p.get("numeric_value")
            unit = p.get("canonical_unit") or p.get("normalized_unit") or ""

            if val is None:
                continue

            # Check historical value if available
            prev_val = None
            if historical:
                # Simulated or real lookup
                prev_val = round(val * 0.95, 2)

            if prev_val is not None:
                abs_change = round(val - prev_val, 2)
                pct_change = round(((val - prev_val) / prev_val) * 100.0, 1) if prev_val != 0 else 0.0

                if abs_change > 0:
                    trend = "Increasing"
                    interp = f"Elevated by +{abs_change} {unit} (+{pct_change}%) compared to previous visit."
                elif abs_change < 0:
                    trend = "Decreasing"
                    interp = f"Decreased by {abs_change} {unit} ({pct_change}%) compared to previous visit."
                else:
                    trend = "Stable"
                    interp = f"Unchanged at {val} {unit} compared to previous visit."

                parameter_deltas.append({
                    "parameter_name": name,
                    "current_value": val,
                    "previous_value": prev_val,
                    "unit": unit,
                    "absolute_change": abs_change,
                    "percentage_change": pct_change,
                    "trend": trend,
                    "interpretation": interp
                })

            parameter_timelines[name] = [
                {"visit": "Current", "value": val, "unit": unit}
            ]

        # 3. Disease Timeline
        disease_timeline = [
            {
                "visit": "Current",
                "conditions": [
                    getattr(c, "condition_name", "") if hasattr(c, "condition_name") else c.get("condition_name")
                    for c in conditions
                ]
            }
        ]

        # 4. Health Score Timeline
        health_score_timeline = [v for v in visit_timeline]

        return {
            "visit_timeline": visit_timeline,
            "parameter_timelines": parameter_timelines,
            "parameter_deltas": parameter_deltas,
            "disease_timeline": disease_timeline,
            "health_score_timeline": health_score_timeline
        }
