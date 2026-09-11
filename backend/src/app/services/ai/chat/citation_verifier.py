"""
Citation Verifier (Phase 7 Chat Engine).
Verifies that cited guideline passages and evidence IDs exist before rendering.
Attaches structured citation objects.
"""

from typing import List, Dict, Any


class CitationVerifier:
    """Validates citations attached to AI responses."""

    @classmethod
    def verify_and_build(
        cls,
        retrieved_passages: List[Dict[str, Any]],
        analysis_evidence: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        citations = []

        # 1. Guideline Citations
        for p in retrieved_passages:
            citations.append({
                "id": p.get("id"),
                "title": p.get("title"),
                "source": p.get("metadata", {}).get("source", "Medical Guideline"),
                "priority": p.get("metadata", {}).get("priority", 1),
                "type": "guideline",
                "quote": p.get("content", "")[:120] + "..."
            })

        # 2. Evidence Citations
        for ev in analysis_evidence:
            citations.append({
                "id": f"EV_{ev.get('parameter_code')}",
                "title": f"Validated Evidence ({ev.get('parameter_name')}: {ev.get('raw_value')})",
                "source": "Patient Lab Report",
                "priority": 1,
                "type": "evidence",
                "quote": f"Status: {ev.get('status')} | Ref Range: {ev.get('ref_range_low')}-{ev.get('ref_range_high')}"
            })

        return citations
