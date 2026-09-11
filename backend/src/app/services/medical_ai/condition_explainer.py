"""
Condition Explainer Engine (Phase 7 Medical AI).
Explains Phase 6 deterministic conditions referencing evidence matrices.
"""

from typing import Dict, Any

class ConditionExplainer:
    @classmethod
    def explain(cls, condition_name: str, evidence_data: Dict[str, Any], provider_mgr) -> Dict[str, Any]:
        prompt = [
            {
                "role": "system",
                "content": "You are Swasth-IQ. Explain the detected condition using provided deterministic evidence without inventing diagnostic criteria."
            },
            {
                "role": "user",
                "content": f"Condition: {condition_name} | Evidence: {evidence_data}"
            }
        ]
        return provider_mgr.generate(prompt, temperature=0.2)
