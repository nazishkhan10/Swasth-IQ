"""
Confidence Explainer Engine (Phase 7 Medical AI).
Explains confidence metrics based on evidence sufficiency.
"""

from typing import Dict, Any

class ConfidenceExplainer:
    @classmethod
    def explain_confidence(cls, confidence_score: float, evidence_count: int, provider_mgr) -> Dict[str, Any]:
        if evidence_count == 0 or confidence_score < 0.4:
            return {
                "explanation": "I do not have enough validated evidence from the report to draw higher-level clinical inferences.",
                "confidence": confidence_score
            }
        
        prompt = [
            {
                "role": "system",
                "content": "You are Swasth-IQ. Explain the confidence metric of this analysis in simple, transparent terms."
            },
            {
                "role": "user",
                "content": f"Confidence Score: {confidence_score} | Evidence Count: {evidence_count}"
            }
        ]
        return provider_mgr.generate(prompt, temperature=0.2)
