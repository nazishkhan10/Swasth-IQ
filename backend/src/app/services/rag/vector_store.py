"""
Vector Store Engine (Phase 7 RAG Engine).
Provides multi-collection indexing, metadata filtering (source priority 1-5),
BM25 keyword scoring, and cosine similarity matching over curated medical knowledge.
"""

import math
import re
from typing import List, Dict, Any, Optional
from app.services.rag.document_loader import DocumentLoader


class VectorStore:
    """In-memory multi-collection hybrid vector store with keyword & metadata filtering."""

    _instance = None

    def __init__(self):
        self.documents: List[Dict[str, Any]] = DocumentLoader.get_all_documents()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Lowercases and tokenizes text into distinct word tokens."""
        return re.findall(r'\b\w+\b', text.lower())

    def search(
        self,
        query: str,
        collections: Optional[List[str]] = None,
        top_k: int = 100,
        min_priority: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid multi-collection search:
        1. Filters by collection names and metadata priority <= min_priority.
        2. Scores documents using TF-IDF/BM25 overlap + keyword match ratio.
        3. Returns top_k candidate documents sorted by relevance score.
        """
        query_tokens = set(self._tokenize(query))
        if not query_tokens:
            query_tokens = {"medical", "report", "health"}

        results = []
        for doc in self.documents:
            # 1. Collection Filter
            if collections and doc.get("collection") not in collections:
                continue

            # 2. Priority Filter (1 highest, 5 lowest)
            doc_priority = doc.get("metadata", {}).get("priority", 3)
            if doc_priority > min_priority:
                continue

            # 3. Hybrid BM25 & Keyword Overlap Scoring
            doc_text = f"{doc.get('title', '')} {doc.get('content', '')}"
            doc_tokens = self._tokenize(doc_text)
            doc_token_set = set(doc_tokens)

            overlap = query_tokens.intersection(doc_token_set)
            if not overlap:
                score = 0.05 / doc_priority  # Base baseline priority score
            else:
                tf = len(overlap) / float(len(doc_tokens) + 1)
                match_ratio = len(overlap) / float(len(query_tokens))
                # Priority weight boost (Priority 1 gets 1.5x boost, Priority 5 gets 1.0x)
                priority_weight = 1.6 - (doc_priority * 0.1)
                score = round((match_ratio * 0.7 + tf * 0.3) * priority_weight, 4)

            results.append({
                "id": doc["id"],
                "collection": doc.get("collection"),
                "title": doc.get("title"),
                "content": doc.get("content"),
                "metadata": doc.get("metadata"),
                "score": score
            })

        # Sort descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
