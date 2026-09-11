"""
Context Passage Deduplication Engine (Phase 7 RAG Engine).
Eliminates duplicate or highly overlapping passages before context compression.
"""

from typing import List, Dict, Any


class ContextDeduplicator:
    """Removes duplicate or redundant retrieved passages."""

    @classmethod
    def deduplicate(cls, passages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filters out duplicate IDs and content chunks."""
        seen_ids = set()
        seen_snippets = set()
        unique_passages = []

        for p in passages:
            doc_id = p.get("id")
            if doc_id in seen_ids:
                continue

            content_snippet = p.get("content", "")[:60].strip().lower()
            if content_snippet in seen_snippets:
                continue

            seen_ids.add(doc_id)
            seen_snippets.add(content_snippet)
            unique_passages.append(p)

        return unique_passages
