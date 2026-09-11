from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime, timezone
from app.database.base import Base

class ParseWarning(Base):
    __tablename__ = "parse_warnings"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    page_number = Column(Integer, default=1)
    parameter_name = Column(String, nullable=True)
    warning_type = Column(String, nullable=False)  # Missing Unit, Unknown Parameter, Duplicate Value, Unreadable Range, etc.
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
