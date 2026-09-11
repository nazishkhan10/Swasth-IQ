"""
Hybrid RAG Retriever (Phase 7 RAG Engine).
Executes 2-layer Intent-Aware Retrieval:
Fast Multi-Collection Candidate Search (100) -> Metadata Priority Filter ->
Cross-Encoder Reranker (Top 25) -> Deduplication & Compression (Top 5).
Tracks Funnel Metrics: (Retrieved -> Filtered -> Reranked -> Used).
"""

from typing import List, Dict, Any, Optional
from app.services.rag.vector_store import VectorStore
from app.services.rag.reranker import Reranker
from app.services.rag.deduplicator import ContextDeduplicator

from app.services.rag.cache.retrieval_cache import RetrievalCache
from app.core.config import settings


class HybridRetriever:
    """Master Hybrid RAG Retriever."""

    # Intent to collection mapping
    INTENT_COLLECTIONS = {
        "Explain Parameter": ["lab_reference", "medical_terms"],
        "Disease Explanation": ["diseases", "medical_guidelines"],
        "Trend Analysis": ["medical_guidelines", "lab_reference"],
        "Comparison": ["medical_guidelines", "lab_reference"],
        "Lifestyle": ["nutrition", "exercise", "medical_guidelines"],
        "Nutrition": ["nutrition", "medical_guidelines"],
        "Exercise": ["exercise", "medical_guidelines"],
        "Medication Information": ["drug_information", "medical_guidelines"],
        "Risk Explanation": ["diseases", "medical_guidelines", "emergency"],
        "Recommendation Explanation": ["medical_guidelines", "nutrition", "exercise"],
        "Organ Health": ["diseases", "lab_reference", "medical_guidelines"],
        "Emergency Advice": ["emergency", "medical_guidelines"],
        "General Medical QA": ["medical_guidelines", "lab_reference", "diseases"]
    }

    @classmethod
    def retrieve(
        cls,
        report_id: int,
        question: str,
        intent: str = "General Medical QA",
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Executes multi-stage intent-aware retrieval:
        Returns context passages and detailed funnel metrics.
        """
        if not force_refresh:
            cached = RetrievalCache.get(report_id, question)
            if cached:
                cached["cache_hit"] = True
                return cached

        # 1. Collection Target Selection
        target_collections = cls.INTENT_COLLECTIONS.get(intent, ["medical_guidelines", "lab_reference"])

        # 2. Layer 1: Fast Candidate Retrieval (up to RETRIEVAL_CANDIDATES)
        store = VectorStore.get_instance()
        candidates = store.search(
            query=question,
            collections=target_collections,
            top_k=settings.RETRIEVAL_CANDIDATES
        )
        count_retrieved = len(candidates)

        # Priority 1-4 filter
        filtered_candidates = [c for c in candidates if c.get("metadata", {}).get("priority", 3) <= 4]
        count_filtered = len(filtered_candidates)

        # 3. Layer 2: Cross-Encoder Reranking (top RERANK_TOP_K)
        reranked = Reranker.rerank(
            query=question,
            candidates=filtered_candidates if filtered_candidates else candidates,
            top_k=settings.RERANK_TOP_K
        )
        count_reranked = len(reranked)

        # 4. Context Compression & Deduplication (top FINAL_CONTEXT)
        deduped = ContextDeduplicator.deduplicate(reranked)
        final_passages = deduped[:settings.FINAL_CONTEXT]

        # 5. Live Internet Medical Knowledge Search
        from app.services.rag.retrieval.web_search_engine import MedicalWebSearchEngine
        web_passages = MedicalWebSearchEngine.search_medical_web(question, max_results=3)
        if web_passages:
            final_passages = web_passages + final_passages

        count_used = len(final_passages)

        funnel_metrics = {
            "retrieved": count_retrieved + len(web_passages),
            "filtered": count_filtered,
            "reranked": count_reranked,
            "used": count_used
        }


        result = {
            "passages": final_passages,
            "funnel": funnel_metrics,
            "cache_hit": False,
            "intent": intent,
            "collections_searched": target_collections,
            "knowledge_version": "2026.1"
        }

        # Cache result
        RetrievalCache.set(report_id, question, result)
        return result
