import uuid
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.models.report import Report, ReportStatus, UploadSource
from app.logs.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)

# ─── Constants ────────────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/jpg",
    "text/plain",
}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB

UPLOADS_ROOT = Path(__file__).resolve().parents[2] / "uploads"


# ─── Path Builder ─────────────────────────────────────────────────────────────
def build_storage_path(user_id: int, report_uuid: str, original_filename: str) -> Path:
    """
    Structure: uploads/{user_id}/{YYYY}/{MM}/{report_uuid}/{original_filename}
    """
    now = datetime.now(timezone.utc)
    year = now.strftime("%Y")
    month = now.strftime("%m")
    target_dir = UPLOADS_ROOT / str(user_id) / year / month / report_uuid
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / original_filename


def file_url_from_path(file_path: Path) -> str:
    """Convert absolute path to a relative URL for serving via /uploads static mount."""
    relative = file_path.relative_to(UPLOADS_ROOT)
    return f"/uploads/{relative.as_posix()}"


# ─── Validation ───────────────────────────────────────────────────────────────
def validate_upload(file: UploadFile, file_bytes: bytes) -> None:
    """
    Validate: extension → mime type → size.
    Raises HTTPException on failure.
    """
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{suffix}' is not supported. Allowed: PDF, PNG, JPG, JPEG, TXT",
        )

    declared_mime = (file.content_type or "").split(";")[0].lower().strip()
    if declared_mime and declared_mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MIME type '{declared_mime}' is not allowed.",
        )

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        size_mb = len(file_bytes) / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size {size_mb:.1f} MB exceeds the 20 MB limit.",
        )

    logger.info(f"File validated: {file.filename} ({len(file_bytes)} bytes, {declared_mime})")


# ─── Save File ────────────────────────────────────────────────────────────────
def save_uploaded_file(
    db: Session,
    file: UploadFile,
    file_bytes: bytes,
    user_id: int,
    upload_source: str = UploadSource.UPLOAD,
) -> Report:
    """
    Validate, store file on disk, create Report record.
    """
    logger.info(f"Upload started: user={user_id} file={file.filename} source={upload_source}")

    validate_upload(file, file_bytes)

    report_uuid = str(uuid.uuid4())
    original_filename = file.filename or f"upload_{report_uuid}"
    file_path = build_storage_path(user_id, report_uuid, original_filename)

    try:
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        logger.info(f"File stored at: {file_path}")
    except OSError as e:
        logger.error(f"Storage error for user={user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store file. Please try again.",
        )

    file_url = file_url_from_path(file_path)
    mime_type = (file.content_type or "").split(";")[0].lower().strip() or None

    report = Report(
        user_id=user_id,
        filename=report_uuid,
        original_filename=original_filename,
        file_path=str(file_path),
        file_url=file_url,
        file_size=len(file_bytes),
        mime_type=mime_type,
        upload_source=upload_source,
        status=ReportStatus.UPLOADED,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    logger.info(f"Upload successful: report_id={report.id} user={user_id} file={original_filename}")
    return report


# ─── List Files ───────────────────────────────────────────────────────────────
def get_user_reports(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[Report]:
    return (
        db.query(Report)
        .filter(Report.user_id == user_id, Report.status != ReportStatus.DELETED)
        .order_by(Report.uploaded_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_report_by_id(db: Session, report_id: int, user_id: int) -> Optional[Report]:
    return (
        db.query(Report)
        .filter(Report.id == report_id, Report.user_id == user_id)
        .first()
    )


# ─── Get Stats ────────────────────────────────────────────────────────────────
def get_user_stats(db: Session, user_id: int) -> dict:
    reports = get_user_reports(db, user_id, limit=10000)
    total_size = sum(r.file_size or 0 for r in reports)
    last_upload = reports[0].uploaded_at if reports else None
    return {
        "total_reports": len(reports),
        "total_size_bytes": total_size,
        "last_uploaded_at": last_upload,
    }


# ─── Delete File ──────────────────────────────────────────────────────────────
def delete_report(db: Session, report_id: int, user_id: int) -> bool:
    report = get_report_by_id(db, report_id, user_id)
    if not report:
        return False

    # Delete file from disk
    file_path = Path(report.file_path)
    if file_path.exists():
        try:
            file_path.unlink()
            # Remove empty parent directories
            parent = file_path.parent
            if parent.exists() and not any(parent.iterdir()):
                shutil.rmtree(parent, ignore_errors=True)
            logger.info(f"File deleted from disk: {file_path}")
        except OSError as e:
            logger.warning(f"Could not delete file from disk: {e}")

    # Mark as deleted in DB (soft-delete)
    report.status = ReportStatus.DELETED
    db.commit()
    logger.info(f"Report soft-deleted: report_id={report_id} user={user_id}")
    return True
