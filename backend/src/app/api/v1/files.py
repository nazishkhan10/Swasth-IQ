from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.auth.jwt import get_current_user
from app.models.user import User
from app.schemas.report import ReportListItem, ReportOut, ReportStats
from app.services import file_service
from app.logs.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("", response_model=List[ReportListItem])
def list_files(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all uploaded reports for the authenticated user (excluding deleted)."""
    reports = file_service.get_user_reports(db, user_id=current_user.id, skip=skip, limit=limit)
    return [ReportListItem.model_validate(r) for r in reports]


@router.get("/stats", response_model=ReportStats)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return aggregate stats: total reports, total storage, last upload."""
    stats = file_service.get_user_stats(db, user_id=current_user.id)
    return ReportStats(**stats)


@router.get("/{report_id}", response_model=ReportOut)
def get_file(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a single report by ID (must belong to authenticated user)."""
    report = file_service.get_report_by_id(db, report_id=report_id, user_id=current_user.id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return ReportOut.model_validate(report)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a report and its file from disk (soft-delete in DB)."""
    deleted = file_service.delete_report(db, report_id=report_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    logger.info(f"Report {report_id} deleted by user {current_user.id}")
