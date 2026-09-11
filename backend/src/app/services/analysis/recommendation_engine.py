"""
Recommendation Engine (Phase 6).
Renders categorized clinical recommendations from templates, grouped into 8 categories
(Immediate, Lifestyle, Nutrition, Exercise, Medication Discussion, Follow-up Tests, Specialists, Monitoring)
across 5 triage levels (Critical, High, Medium, Low, Informational).
"""

from typing import List, Dict, Any
from app.services.analysis.context import MedicalAnalysisContext
from app.services.analysis.templates import RECOMMENDATION_TEMPLATES


class RecommendationEngine:

    @classmethod
    def generate_recommendations(cls, ctx: MedicalAnalysisContext, conditions: List[Any], evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        needed_rec_ids = set()

        for c in conditions:
            rids = getattr(c, "recommendation_ids", []) if hasattr(c, "recommendation_ids") else c.get("recommendation_ids", [])
            for rid in rids:
                needed_rec_ids.add(rid)

        # If no specific disease conditions are triggered, provide routine wellness recommendations
        if not needed_rec_ids:
            needed_rec_ids.add("REC_WELLNESS_ANNUAL")
            needed_rec_ids.add("REC_WELLNESS_HYDRATION")
            needed_rec_ids.add("REC_WELLNESS_EXERCISE")
            # If report has CBC parameters
            if any(e.get("parameter_code") in ["HGB", "WBC", "RBC", "PLT"] for e in evidence):
                needed_rec_ids.add("REC_CBC_MONITOR")

        recs = []
        for rid in needed_rec_ids:
            tmpl = RECOMMENDATION_TEMPLATES.get(rid)
            if not tmpl:
                continue

            linked_ev_ids = [e["evidence_id"] for e in evidence if e.get("parameter_code")]

            recs.append({
                "id": tmpl["id"],
                "title": tmpl["title"],
                "category": tmpl["category"],
                "priority": tmpl["priority"],
                "triage_level": tmpl["triage_level"],
                "action": tmpl["action"],
                "rationale": tmpl["rationale"],
                "confidence": 0.92,
                "evidence_count": len(linked_ev_ids),
                "linked_evidence_ids": linked_ev_ids[:4]
            })

        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFORMATIONAL": 4}
        recs.sort(key=lambda r: priority_order.get(r["priority"], 99))

        return recs

