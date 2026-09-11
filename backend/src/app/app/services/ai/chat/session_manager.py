"""
Session Manager Engine (Phase 7 AI Chat - Architecture Freeze v8.0).
Manages Report-Scoped Temporary Chat Sessions.
Ensures zero cross-report conversation leakage by purging sessions on report close or new upload.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.chat import ChatSession, ChatMessage, ChatExecution

logger = logging.getLogger("medical_report_analyzer")


class SessionManager:
    """Manages report-scoped temporary chat sessions."""

    SESSION_TTL_MINUTES = 120

    @classmethod
    def create_session(cls, db: Session, report_id: int, user_id: Optional[int] = None) -> ChatSession:
        """Purges any existing chat session for this report and initializes a fresh temporary session."""
        cls.delete_report_sessions(db, report_id)

        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=cls.SESSION_TTL_MINUTES)
        
        session = ChatSession(
            report_id=report_id,
            user_id=user_id,
            active=True,
            created_at=now,
            expires_at=expires
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"[SessionManager] Initialized fresh ChatSession #{session.id} for Report #{report_id}")
        return session

    @classmethod
    def get_active_session(cls, db: Session, report_id: int, user_id: Optional[int] = None) -> ChatSession:
        """Fetches active chat session for report or creates a fresh one."""
        session = db.query(ChatSession).filter(
            ChatSession.report_id == report_id,
            ChatSession.active == True
        ).order_by(ChatSession.id.desc()).first()

        if not session:
            session = cls.create_session(db, report_id, user_id)
        return session

    @classmethod
    def delete_report_sessions(cls, db: Session, report_id: int):
        """Purges all sessions and messages belonging to a report."""
        try:
            sessions = db.query(ChatSession).filter(ChatSession.report_id == report_id).all()
            for s in sessions:
                db.delete(s)
            
            # Also purge any dangling orphan messages
            orphan_msgs = db.query(ChatMessage).filter(ChatMessage.report_id == report_id).all()
            for m in orphan_msgs:
                db.delete(m)

            db.commit()
            logger.info(f"[SessionManager] Purged all temporary chat sessions and messages for Report #{report_id}")
        except Exception as e:
            db.rollback()
            logger.error(f"[SessionManager] Error purging sessions for Report #{report_id}: {e}")

    @classmethod
    def close_session(cls, db: Session, report_id: int):
        """Deactivates and deletes chat session when user closes a report."""
        cls.delete_report_sessions(db, report_id)
