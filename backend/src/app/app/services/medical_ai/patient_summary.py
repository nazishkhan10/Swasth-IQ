"""
Patient Summary Generator (Phase 7 Medical AI - Architecture v8.0).
Generates patient-friendly explanations strictly grounded in Phase 6 deterministic outputs.
"""

from typing import Dict, Any

class PatientSummaryEngine:
    """Generates reassuring, clear patient-oriented report summaries."""

    @classmethod
    def generate_summary(cls, deterministic_analysis: Dict[str, Any], provider_mgr) -> Dict[str, Any]:
        health_score = deterministic_analysis.get("overall_health_score", 85)
        overall_risk = deterministic_analysis.get("overall_risk", "LOW")
        conditions = deterministic_analysis.get("conditions") or []
        validated_params = deterministic_analysis.get("validated_parameters") or []

        cond_list = [c.get("condition_name") if isinstance(c, dict) else str(c) for c in conditions]
        cond_str = ", ".join(cond_list) if cond_list else "Optimal Health (No pathological conditions detected)"

        prompt_messages = [
            {
                "role": "system",
                "content": (
                    "You are Swasth-IQ, an empathetic medical assistant.\n"
                    "RULES:\n"
                    "1. DO NOT calculate, diagnose, or invent numbers.\n"
                    "2. Explain the provided deterministic clinical data in warm, clear patient-friendly prose.\n"
                    "3. Return ONLY a valid JSON object with keys: 'summary', 'explanation', 'evidence', 'confidence', 'disclaimer'."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Deterministic Health Score: {health_score}/100 | Risk Category: {overall_risk}\n"
                    f"Detected Conditions: {cond_str}\n"
                    f"Validated Parameters Count: {len(validated_params)}\n"
                    "Please generate a structured patient summary."
                )
            }
        ]

        res = provider_mgr.generate(prompt_messages, temperature=0.2, json_mode=True)
        return res
