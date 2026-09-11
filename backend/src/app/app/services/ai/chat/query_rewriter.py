"""
Query Rewriter Engine (Phase 7 Chat Engine).
Translates colloquial user queries into clinical search terms & intent classifications.
"""

import re
from typing import Dict, Any


class QueryRewriter:
    """Translates user query to medical intent and clinical query."""

    @classmethod
    def rewrite_and_classify(cls, question: str) -> Dict[str, Any]:
        q_lower = question.strip().lower()

        intent = "General Medical QA"
        rewritten = question.strip()

        if any(w in q_lower for w in ["hba1c", "glucose", "creatinine", "egfr", "tsh", "cholesterol", "ldl", "level", "parameter", "what is"]):
            intent = "Explain Parameter"
            rewritten = f"Explain laboratory parameter and reference range in question: {question}"
        elif any(w in q_lower for w in ["diabetes", "ckd", "kidney", "thyroid", "hypothyroidism", "disease", "condition", "why did ai detect"]):
            intent = "Disease Explanation"
            rewritten = f"Explain detected clinical condition and rationale in question: {question}"
        elif any(w in q_lower for w in ["food", "diet", "eat", "avoid", "nutrition"]):
            intent = "Nutrition"
            rewritten = f"Provide evidence-backed clinical nutrition guidelines for question: {question}"
        elif any(w in q_lower for w in ["exercise", "workout", "activity", "walk"]):
            intent = "Exercise"
            rewritten = f"Provide physical activity and exercise prescription for question: {question}"
        elif any(w in q_lower for w in ["doctor", "consult", "specialist", "nephrologist", "endocrinologist"]):
            intent = "Recommendation Explanation"
            rewritten = f"Provide specialist consultation and follow-up guidance for question: {question}"
        elif any(w in q_lower for w in ["compare", "previous", "trend", "improved", "worsened"]):
            intent = "Comparison"
            rewritten = f"Compare multi-visit laboratory parameter trends for question: {question}"
        elif any(w in q_lower for w in ["dangerous", "emergency", "hospital", "red flag"]):
            intent = "Emergency Advice"
            rewritten = f"Check emergency red flags and clinical safety protocol for question: {question}"

        return {
            "intent": intent,
            "original_query": question,
            "rewritten_query": rewritten
        }
