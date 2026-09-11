"""
Parse Warning Service.
Creates and persists audit warning logs during medical parsing.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.parse_warning import ParseWarning
from app.logs.logger import logger

class ParseWarningService:
    """Logs and persists warnings encountered during the parsing pipeline."""

    @classmethod
    def record_warnings(cls, db: Session, report_id: int, warnings: List[Dict[str, Any]]) -> None:
        # Clear prior warnings for this report
        db.query(ParseWarning).filter(ParseWarning.report_id == report_id).delete()
        db.commit()

        for w in warnings:
            entry = ParseWarning(
                report_id=report_id,
                page_number=w.get("page_number", 1),
                parameter_name=w.get("parameter_name"),
                warning_type=w.get("warning_type", "General Warning"),
                message=w.get("message", "")
            )
            db.add(entry)
            logger.warning(f"[ParseWarning] Report #{report_id} Page {entry.page_number} [{entry.warning_type}]: {entry.message}")

        db.commit()
