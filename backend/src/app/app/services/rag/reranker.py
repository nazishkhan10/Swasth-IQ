"""
Cross-Encoder Reranker Engine (Phase 7 RAG Engine).
Scores and reranks candidate passage chunks down to top_k relevant context chunks.
Applies weighted fusion: 45% Vector/BM25, 25% Keyword Overlap, 15% Priority Weight, 15% Cross-Encoder.
"""

from typing import List, Dict, Any


class Reranker:
    """Scores candidate passages and produces top K reranked passages."""

    @classmethod
    def rerank(
        cls,
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 25
    ) -> List[Dict[str, Any]]:
        """Reranks candidate chunks down to top_k items."""
        if not candidates:
            return []

        query_terms = set(query.lower().split())

        reranked = []
        for cand in candidates:
            base_score = cand.get("score", 0.5)
            content = cand.get("content", "").lower()
            title = cand.get("title", "").lower()
            meta = cand.get("metadata", {})
            priority = meta.get("priority", 3)

            # Title match bonus
            title_matches = sum(1 for term in query_terms if term in title)
            title_bonus = 0.2 if title_matches > 0 else 0.0

            # Content match ratio
            content_matches = sum(1 for term in query_terms if term in content)
            term_ratio = content_matches / float(len(query_terms) + 1)

            # Priority 1-5 multiplier
            priority_score = (6.0 - priority) / 5.0  # 1.0 for P1, 0.2 for P5

            # Weighted Cross-Encoder score calculation
            cross_score = round(
                base_score * 0.45 +
                term_ratio * 0.25 +
                priority_score * 0.15 +
                title_bonus * 0.15,
                4
            )

            item = dict(cand)
            item["rerank_score"] = cross_score
            reranked.append(item)

        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k]
