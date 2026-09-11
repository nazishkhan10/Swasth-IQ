"""
Report Context Resolver (Phase 7 Chat Engine).
Resolves multi-report query ambiguity (Latest, Historical, Specific Visit).
"""

from typing import Dict, Any, List


class ReportContextResolver:
    """Disambiguates query context across patient reports."""

    @classmethod
    def resolve(cls, report_id: int, question: str) -> Dict[str, Any]:
        q_lower = question.lower()
        is_comparison = any(kw in q_lower for kw in ["compare", "previous", "earlier", "past visit", "trend", "improved", "worsened"])
        return {
            "primary_report_id": report_id,
            "is_comparison": is_comparison,
            "target": "comparison" if is_comparison else "current"
        }
