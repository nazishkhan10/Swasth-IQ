import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.report import Report, ReportStatus
from app.models.ocr_result import OCRResult
from app.models.ocr_block import OCRBlock
from app.services.ocr.router import DocumentRouter
from app.services.ocr_storage import save_page_json, load_page_json
from app.logs.logger import logger


class OCRService:
    """Master Orchestrator for Document Intelligence & OCR Pipeline."""

    @classmethod
    def process_report_ocr(
        cls,
        db: Session,
        report: Report,
        force_retry: bool = False,
        requested_engine: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes OCR extraction for a report.
        Implements smart caching: Returns existing result if already completed unless force_retry=True.
        """
        logger.info(f"[OCRService] Request to process OCR for Report #{report.id} ({report.original_filename}) | ForceRetry: {force_retry} | CustomEngine: {requested_engine}")

        # Check Cache: return cached result if completed and not forcing retry
        if report.ocr_status == ReportStatus.COMPLETED and not force_retry and report.ocr_version > 0:
            logger.info(f"[OCRService] Returning cached OCR result for Report #{report.id} (Version {report.ocr_version})")
            return cls.get_report_ocr_results(db, report)

        # Prepare for new processing run
        new_version = (report.ocr_version or 0) + 1
        report.ocr_status = ReportStatus.PROCESSING
        report.ocr_version = new_version
        db.commit()
        try:

            # Execute OCR extraction with automatic retries and engine fallback
            max_retries = 3
            ocr_output = None
            last_error = None

            # Fallback engines sequence
            engine_candidates = [
                requested_engine,
                "SarvamVision",
                "PyMuPDF",
                "PlainText"
            ]

            for attempt in range(max_retries):
                try:
                    curr_engine_name = engine_candidates[attempt] if attempt < len(engine_candidates) else None
                    engine, doc_type = DocumentRouter.select_engine(
                        file_path=report.file_path,
                        mime_type=report.mime_type or "",
                        custom_engine_name=curr_engine_name
                    )
                    logger.info(f"[OCRService] Attempt {attempt+1}/{max_retries} for Report #{report.id} v{new_version} -> Engine: {engine.engine_name}")
                    ocr_output = engine.extract(report.file_path)
                    if ocr_output and ocr_output.get("pages"):
                        break
                except Exception as attempt_err:
                    logger.warning(f"[OCRService] Attempt {attempt+1} failed for Report #{report.id}: {attempt_err}")
                    last_error = attempt_err

            if not ocr_output:
                raise last_error or RuntimeError(f"OCR extraction failed after {max_retries} automatic retries.")


            pages_data = ocr_output.get("pages", [])
            avg_confidence = float(ocr_output.get("confidence", 1.0))
            proc_time = float(ocr_output.get("processing_time", 0.0))
            engine_name = ocr_output.get("engine", engine.engine_name)
            report_folder_id = f"{report.user_id}_{report.id}_{report.filename}"

            # Persist Page JSON files & Database records
            for page_info in pages_data:
                page_num = page_info.get("page", 1)
                page_text = page_info.get("text", "")
                page_conf = float(page_info.get("confidence", 1.0))
                blocks = page_info.get("blocks", [])

                # 1. Save page JSON file
                json_rel_path = save_page_json(
                    report_uuid=report_folder_id,
                    version=new_version,
                    page_number=page_num,
                    page_data=page_info
                )


                # 2. Insert OCRResult DB record
                ocr_result_entry = OCRResult(
                    report_id=report.id,
                    version=new_version,
                    page_number=page_num,
                    raw_text=page_text,
                    json_path=json_rel_path,
                    confidence=page_conf,
                    processing_time=proc_time
                )
                db.add(ocr_result_entry)

                # 3. Insert normalized OCRBlock DB records
                for b_idx, block in enumerate(blocks):
                    bbox_str = json.dumps(block.get("bbox", [])) if block.get("bbox") else None
                    ocr_block_entry = OCRBlock(
                        report_id=report.id,
                        version=new_version,
                        page_number=page_num,
                        block_index=b_idx + 1,
                        type=block.get("type", "paragraph"),
                        text=block.get("text", ""),
                        bbox_json=bbox_str,
                        confidence=page_conf
                    )
                    db.add(ocr_block_entry)

            # Update Report status & metrics
            report.ocr_status = ReportStatus.COMPLETED
            report.last_engine = engine_name
            report.last_processed = datetime.now(timezone.utc)
            report.average_confidence = avg_confidence
            report.page_count = len(pages_data)
            report.processing_time = proc_time
            db.commit()

            logger.info(f"[OCRService] Report #{report.id} v{new_version} OCR COMPLETED successfully in {proc_time}s across {len(pages_data)} pages.")

            return cls.get_report_ocr_results(db, report, version=new_version)

        except Exception as e:
            logger.error(f"[OCRService] Failed OCR processing for Report #{report.id}: {e}", exc_info=True)
            report.ocr_status = ReportStatus.FAILED
            db.commit()
            raise e

    @classmethod
    def get_report_ocr_results(cls, db: Session, report: Report, version: Optional[int] = None) -> Dict[str, Any]:
        """Fetches unified OCR results for a given report and version."""
        target_version = version or report.ocr_version or 1

        ocr_results = db.query(OCRResult).filter(
            OCRResult.report_id == report.id,
            OCRResult.version == target_version
        ).order_by(OCRResult.page_number).all()

        pages_payload = []
        for res in ocr_results:
            page_json = load_page_json(res.json_path)
            if page_json:
                pages_payload.append(page_json)
            else:
                # Fallback construct from DB if JSON file unreadable
                blocks_db = db.query(OCRBlock).filter(
                    OCRBlock.report_id == report.id,
                    OCRBlock.version == target_version,
                    OCRBlock.page_number == res.page_number
                ).order_by(OCRBlock.block_index).all()

                blocks = [{
                    "id": f"b{res.page_number}_{b.block_index}",
                    "type": b.type,
                    "text": b.text,
                    "bbox": json.loads(b.bbox_json) if b.bbox_json else []
                } for b in blocks_db]

                pages_payload.append({
                    "page": res.page_number,
                    "confidence": res.confidence,
                    "text": res.raw_text or "",
                    "blocks": blocks,
                    "tables": [],
                    "headers": [b.text for b in blocks_db if b.type == "header"],
                    "lists": [],
                    "images_metadata": []
                })

        return {
            "status": report.ocr_status,
            "engine": report.last_engine or "Unknown",
            "version": target_version,
            "confidence": report.average_confidence or 0.0,
            "page_count": report.page_count or len(pages_payload),
            "processing_time": report.processing_time or 0.0,
            "last_processed": report.last_processed.isoformat() if report.last_processed else None,
            "pages": pages_payload
        }
