"""
Lifestyle Insight Engine (Phase 7 Medical AI).
Explains why Phase 6 deterministic lifestyle recommendation templates apply to the patient.
"""

from typing import Dict, Any, List

class LifestyleInsightEngine:
    @classmethod
    def explain_recommendations(cls, rec_templates: List[Dict[str, Any]], provider_mgr) -> Dict[str, Any]:
        prompt = [
            {
                "role": "system",
                "content": (
                    "You are Swasth-IQ. Explain WHY the provided Phase 6 deterministic lifestyle recommendations apply.\n"
                    "RULES: Do NOT invent ungrounded advice. Explain strictly the provided recommendation templates."
                )
            },
            {
                "role": "user",
                "content": f"Deterministic Recommendations: {rec_templates}"
            }
        ]
        return provider_mgr.generate(prompt, temperature=0.2)
