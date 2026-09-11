from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.auth.jwt import get_current_user
from app.models.user import User
from app.models.report import UploadSource
from app.schemas.report import ReportOut
from app.services import file_service
from app.logs.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    upload_source: str = Form(default=UploadSource.UPLOAD),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a medical report file (PDF, image, or TXT).
    Validates extension, MIME type, and file size before storing.
    """
    logger.info(f"Upload request: user={current_user.id} file={file.filename} source={upload_source}")

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file received. Please select a valid file.",
        )

    valid_sources = {UploadSource.UPLOAD, UploadSource.CAMERA}
    if upload_source not in valid_sources:
        upload_source = UploadSource.UPLOAD

    report = file_service.save_uploaded_file(
        db=db,
        file=file,
        file_bytes=file_bytes,
        user_id=current_user.id,
        upload_source=upload_source,
    )
    return ReportOut.model_validate(report)
