"""
Diet & Nutrition Insight Engine (Phase 7 Medical AI).
Explains why Phase 6 nutrition recommendation templates apply to the patient.
"""

from typing import Dict, Any, List

class DietInsightEngine:
    @classmethod
    def explain_diet(cls, nutrition_templates: List[Dict[str, Any]], provider_mgr) -> Dict[str, Any]:
        prompt = [
            {
                "role": "system",
                "content": (
                    "You are Swasth-IQ. Explain WHY the provided Phase 6 nutrition templates apply.\n"
                    "RULES: Do NOT invent custom diet plans from thin air. Explain the evidence behind provided templates."
                )
            },
            {
                "role": "user",
                "content": f"Deterministic Nutrition Templates: {nutrition_templates}"
            }
        ]
        return provider_mgr.generate(prompt, temperature=0.2)
