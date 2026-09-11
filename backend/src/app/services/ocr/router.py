import os
import fitz  # PyMuPDF
from typing import Dict, Any, Tuple
from app.services.ocr.base import BaseOCREngine
from app.services.ocr.pymupdf_engine import PyMuPDFEngine
from app.services.ocr.sarvam_doc_engine import SarvamDocEngine
from app.services.ocr.sarvam_vision_engine import SarvamVisionEngine
from app.services.ocr.tesseract_engine import TesseractEngine
from app.services.ocr.plaintext_engine import PlainTextEngine
from app.logs.logger import logger


class DocumentRouter:
    """Detects document type and routes to optimal OCR extraction engine."""

    @staticmethod
    def is_digital_pdf(file_path: str) -> bool:
        """
        Determines if a PDF is a Digital PDF (has searchable vector text layer)
        vs a Scanned PDF (image scans wrapped in PDF).
        """
        try:
            doc = fitz.open(file_path)
            page_cnt = len(doc)
            if page_cnt == 0:
                doc.close()
                return False
                
            total_chars = 0
            for page in doc:
                text = page.get_text("text") or ""
                total_chars += len(text.strip())
            
            doc.close()
            avg_chars_per_page = total_chars / max(page_cnt, 1)
            logger.info(f"[DocumentRouter] PDF inspection: {total_chars} total characters across {page_cnt} pages (Avg: {avg_chars_per_page:.1f})")
            
            # If average text density is >= 30 chars per page, it's a Digital PDF
            return avg_chars_per_page >= 30
        except Exception as e:
            logger.warning(f"[DocumentRouter] Could not inspect PDF structure: {e}")
            return False

    @classmethod
    def select_engine(cls, file_path: str, mime_type: str = "", custom_engine_name: str = None) -> Tuple[BaseOCREngine, str]:
        """
        Selects primary extraction engine based on file format and custom requested engine override.
        Returns Tuple[BaseOCREngine, detected_document_type]
        """
        ext = os.path.splitext(file_path)[1].lower()

        # Handle custom override request
        if custom_engine_name:
            c_name = custom_engine_name.lower()
            if "pymupdf" in c_name:
                return PyMuPDFEngine(), "digital_pdf"
            elif "sarvam_doc" in c_name or "sarvam doc" in c_name:
                return SarvamDocEngine(), "scanned_pdf"
            elif "sarvam_vision" in c_name or "sarvam vision" in c_name:
                return SarvamVisionEngine(), "image"
            elif "tesseract" in c_name:
                return TesseractEngine(), "scanned_pdf"
            elif "plaintext" in c_name or "txt" in c_name:
                return PlainTextEngine(), "txt"

        # Auto-routing logic
        if ext == ".txt" or "text/plain" in mime_type:
            logger.info(f"[DocumentRouter] Routing '{file_path}' -> PlainTextEngine")
            return PlainTextEngine(), "txt"

        elif ext in [".jpg", ".jpeg", ".png"] or "image/" in mime_type:
            logger.info(f"[DocumentRouter] Routing '{file_path}' -> SarvamVisionEngine")
            return SarvamVisionEngine(), "image"

        elif ext == ".pdf" or "application/pdf" in mime_type:
            if cls.is_digital_pdf(file_path):
                logger.info(f"[DocumentRouter] Routing Digital PDF '{file_path}' -> PyMuPDFEngine")
                return PyMuPDFEngine(), "digital_pdf"
            else:
                logger.info(f"[DocumentRouter] Routing Scanned PDF '{file_path}' -> SarvamDocEngine")
                return SarvamDocEngine(), "scanned_pdf"

        # Default fallback
        logger.info(f"[DocumentRouter] Fallback routing '{file_path}' -> TesseractEngine")
        return TesseractEngine(), "unknown"
