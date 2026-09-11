from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.models.report import Report, ReportStatus
from app.models.ocr_block import OCRBlock
from app.api.v1.auth import get_current_user
from app.services.ocr_service import OCRService
from app.logs.logger import logger

router = APIRouter(prefix="/ocr", tags=["OCR & Document Intelligence"])


@router.post("/{report_id}", status_code=status.HTTP_200_OK)
def start_ocr_process(
    report_id: int,
    force_retry: bool = Query(False, description="Force re-execution of OCR bypassing cache"),
    engine: Optional[str] = Query(None, description="Custom OCR engine override (PyMuPDF, SarvamDoc, SarvamVision, Tesseract, PlainText)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start or fetch OCR extraction for specified report.
    Returns Unified OCR JSON Schema output.
    """
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report #{report_id} not found"
        )

    logger.info(f"[API] User '{current_user.email}' requested OCR for Report #{report_id}")
    
    try:
        results = OCRService.process_report_ocr(
            db=db,
            report=report,
            force_retry=force_retry,
            requested_engine=engine
        )
        return results
    except Exception as e:
        logger.error(f"[API] OCR processing failed for Report #{report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}"
        )


@router.get("/{report_id}", status_code=status.HTTP_200_OK)
def get_ocr_result(
    report_id: int,
    version: Optional[int] = Query(None, description="Specific OCR version to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get completed OCR result for report."""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report #{report_id} not found"
        )

    if report.ocr_status == "pending" or report.ocr_version == 0:
        return {
            "status": "pending",
            "message": "OCR has not been executed for this report yet.",
            "pages": []
        }

    results = OCRService.get_report_ocr_results(db=db, report=report, version=version)
    return results


@router.post("/{report_id}/retry", status_code=status.HTTP_200_OK)
def retry_ocr_process(
    report_id: int,
    engine: Optional[str] = Query(None, description="Alternative engine for retry"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retry OCR extraction with forced cache bypass and optional engine override."""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report #{report_id} not found"
        )

    logger.info(f"[API] Retry requested for Report #{report_id} with engine '{engine}'")

    results = OCRService.process_report_ocr(
        db=db,
        report=report,
        force_retry=True,
        requested_engine=engine
    )
    return results


@router.get("/{report_id}/blocks", status_code=status.HTTP_200_OK)
def get_ocr_blocks(
    report_id: int,
    version: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns normalized list of OCRBlocks for direct downstream processing."""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report #{report_id} not found"
        )

    target_ver = version or report.ocr_version or 1
    blocks = db.query(OCRBlock).filter(
        OCRBlock.report_id == report_id,
        OCRBlock.version == target_ver
    ).order_by(OCRBlock.page_number, OCRBlock.block_index).all()

    return {
        "report_id": report_id,
        "version": target_ver,
        "total_blocks": len(blocks),
        "blocks": [
            {
                "id": b.id,
                "page_number": b.page_number,
                "block_index": b.block_index,
                "type": b.type,
                "text": b.text,
                "bbox": b.bbox_json,
                "confidence": b.confidence
            }
            for b in blocks
        ]
    }
