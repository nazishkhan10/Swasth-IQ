from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ReportOut(BaseModel):
    id: int
    user_id: int
    filename: str
    original_filename: str
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    upload_source: str
    status: str
    uploaded_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportListItem(BaseModel):
    id: int
    original_filename: str
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    upload_source: str
    status: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportStats(BaseModel):
    total_reports: int
    total_size_bytes: int
    last_uploaded_at: Optional[datetime] = None
