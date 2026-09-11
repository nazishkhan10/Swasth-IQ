"""
Exercise Insight Engine (Phase 7 Medical AI).
Explains why Phase 6 exercise recommendation templates apply to the patient.
"""

from typing import Dict, Any, List

class ExerciseInsightEngine:
    @classmethod
    def explain_exercise(cls, exercise_templates: List[Dict[str, Any]], provider_mgr) -> Dict[str, Any]:
        prompt = [
            {
                "role": "system",
                "content": "You are Swasth-IQ. Explain the exercise guidance provided by Phase 6 templates strictly and reassuringly."
            },
            {
                "role": "user",
                "content": f"Exercise Guidance Templates: {exercise_templates}"
            }
        ]
        return provider_mgr.generate(prompt, temperature=0.2)
