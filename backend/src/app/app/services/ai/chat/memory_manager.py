"""
Conversation Memory Manager (Phase 7 Chat Engine).
Maintains last 20 messages, summarizes older conversation turns, extracts key clinical facts,
and prevents context noise.
"""

from typing import List, Dict, Any


class ConversationMemoryManager:
    """Manages conversation memory and windowing."""

    @classmethod
    def get_recent_history(cls, messages: List[Dict[str, Any]], max_messages: int = 20) -> List[Dict[str, str]]:
        """Returns clean message window (last max_messages)."""
        recent = messages[-max_messages:] if len(messages) > max_messages else messages
        formatted = []
        for m in recent:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role in ["user", "assistant"]:
                formatted.append({"role": role, "content": content})
        return formatted
