"""
Retrieval Cache Engine (Phase 7 RAG Engine).
Caches RAG retrieval results keyed by (report_id, knowledge_version, prompt_version, question_hash).
Default TTL: 15 minutes (900s).
"""

import time
import hashlib
from typing import Dict, Any, Optional


class RetrievalCache:
    """In-memory TTL cache for RAG retrieval results."""

    _cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def _make_key(cls, report_id: int, question: str, knowledge_version: str = "2026.1", prompt_version: str = "1.0.0") -> str:
        q_hash = hashlib.sha256(question.strip().lower().encode("utf-8")).hexdigest()[:16]
        return f"rag_{report_id}_{knowledge_version}_{prompt_version}_{q_hash}"

    @classmethod
    def get(cls, report_id: int, question: str, ttl_sec: int = 900) -> Optional[Dict[str, Any]]:
        key = cls._make_key(report_id, question)
        entry = cls._cache.get(key)
        if not entry:
            return None
        if time.time() - entry["timestamp"] > ttl_sec:
            del cls._cache[key]
            return None
        return entry["data"]

    @classmethod
    def set(cls, report_id: int, question: str, data: Dict[str, Any]) -> None:
        key = cls._make_key(report_id, question)
        cls._cache[key] = {
            "timestamp": time.time(),
            "data": data
        }

    @classmethod
    def clear(cls) -> None:
        cls._cache.clear()
