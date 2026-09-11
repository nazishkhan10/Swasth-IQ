"""
Response Formatter (Phase 7 Medical AI — Architecture Freeze v8.2).
Normalizes units, labels, spacing, evidence order, and follow-up prompts before sending to REST API.
"""

from typing import Dict, Any, List

class ResponseFormatter:
    """Normalizes and cleans AI output dictionaries."""

    @classmethod
    def format_response(cls, raw_data: Dict[str, Any], validated_params: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not isinstance(raw_data, dict):
            raw_data = {"summary": str(raw_data)}

        summary = str(raw_data.get("summary", "")).strip()
        explanation = str(raw_data.get("explanation", "")).strip()
        meaning = str(raw_data.get("meaning", "")).strip()
        disclaimer = str(raw_data.get("disclaimer", "")).strip()

        if not disclaimer:
            disclaimer = "Note: Swasth-IQ provides automated insights based strictly on validated report data for educational reference."

        findings = raw_data.get("findings")
        if not isinstance(findings, list):
            findings = []

        lifestyle = raw_data.get("lifestyle")
        if not isinstance(lifestyle, list):
            lifestyle = []

        evidence = raw_data.get("evidence")
        if not isinstance(evidence, list):
            evidence = []

        follow_up = raw_data.get("follow_up")
        if not isinstance(follow_up, list):
            follow_up = []

        return {
            "summary": summary,
            "findings": findings,
            "explanation": explanation,
            "meaning": meaning,
            "lifestyle": lifestyle,
            "evidence": evidence,
            "follow_up": follow_up,
            "disclaimer": disclaimer
        }
