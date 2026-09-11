"""
Chat Database Models (Phase 7 — Architecture Freeze v8.0).
Defines ChatSession (Report-Scoped Temporary Conversations) and ChatMessage models.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base


class ChatSession(Base):
    """Temporary report-scoped chat session created on report open and deleted on close."""

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    messages = relationship("ChatMessage", backref="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession #{self.id} report_id={self.report_id} active={self.active}>"


class ChatMessage(Base):
    """Stores user questions and AI responses scoped to a ChatSession."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    role = Column(String(50), nullable=False)  # user | assistant | system
    content = Column(Text, nullable=False)
    intent = Column(String(100), nullable=True)
    provider_used = Column(String(100), nullable=True, default="OpenAI (gpt-5-nano)")
    
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    executions = relationship("ChatExecution", backref="message", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatMessage #{self.id} [{self.role}]: {self.content[:30]}...>"


class ChatExecution(Base):
    """Stores execution metrics, RAG retrieval funnels, prompt audit hashes, and token costs."""

    __tablename__ = "chat_executions"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)

    prompt_id = Column(String(100), nullable=True)
    prompt_version = Column(String(50), nullable=False, default="1.0.0")
    prompt_hash = Column(String(64), nullable=True)
    knowledge_version = Column(String(50), nullable=False, default="2026.1")

    provider = Column(String(100), nullable=False, default="OpenAI (gpt-5-nano)")
    is_fallback = Column(Boolean, nullable=False, default=False)
    latency_ms = Column(Float, nullable=True)
    tokens_used = Column(Integer, nullable=True, default=0)

    # Funnel Metrics
    candidates_retrieved = Column(Integer, default=0)
    candidates_filtered = Column(Integer, default=0)
    candidates_reranked = Column(Integer, default=0)
    candidates_used = Column(Integer, default=0)

    execution_trace_json = Column(Text, nullable=True)
    citations_json = Column(Text, nullable=True)
    confidence_json = Column(Text, nullable=True)
    analytics_json = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<ChatExecution msg_id={self.message_id} provider={self.provider} latency={self.latency_ms}ms>"
