"""
Doctor Summary Generator (Phase 7 Medical AI - Architecture v8.0).
Generates concise clinician summaries with evidence matrix references.
"""

from typing import Dict, Any

class DoctorSummaryEngine:
    """Generates concise, professional clinician summaries."""

    @classmethod
    def generate_summary(cls, deterministic_analysis: Dict[str, Any], provider_mgr) -> Dict[str, Any]:
        health_score = deterministic_analysis.get("overall_health_score", 85)
        overall_risk = deterministic_analysis.get("overall_risk", "LOW")
        conditions = deterministic_analysis.get("conditions") or []
        evidence_matrix = deterministic_analysis.get("evidence_matrix") or []

        prompt_messages = [
            {
                "role": "system",
                "content": (
                    "You are Swasth-IQ, a clinical decision support explanation layer.\n"
                    "RULES:\n"
                    "1. DO NOT calculate, diagnose, or infer unverified lab values.\n"
                    "2. Format clinical findings cleanly for physician review referencing evidence matrix IDs.\n"
                    "3. Return ONLY a valid JSON object with keys: 'summary', 'explanation', 'evidence', 'confidence', 'disclaimer'."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Health Score: {health_score}/100 | Risk: {overall_risk}\n"
                    f"Conditions: {conditions}\n"
                    f"Evidence Items Count: {len(evidence_matrix)}\n"
                    "Please generate a structured physician summary."
                )
            }
        ]

        res = provider_mgr.generate(prompt_messages, temperature=0.2, json_mode=True)
        return res
