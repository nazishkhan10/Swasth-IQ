import time
from typing import Dict, Any
from app.services.ocr.base import BaseOCREngine
from app.services.ocr.sarvam_doc_engine import SarvamDocEngine
from app.services.ocr.pymupdf_engine import PyMuPDFEngine
from app.logs.logger import logger


class SarvamVisionEngine(BaseOCREngine):
    """
    Sarvam AI Vision OCR Engine for Image reports (JPG, PNG, JPEG).
    Primary: Sarvam AI Document Intelligence (`/doc-ai/v1`)
    """
    engine_name = "Sarvam Vision OCR"

    def extract(self, file_path: str) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"[{self.engine_name}] Processing image report using Sarvam AI: {file_path}")

        # 1. Primary Engine: Sarvam AI Document Intelligence
        try:
            sarvam_doc = SarvamDocEngine()
            result = sarvam_doc.extract(file_path)
            result["engine"] = self.engine_name
            result["document_type"] = "image"
            logger.info(f"[{self.engine_name}] Sarvam AI extraction successful for: {file_path}")
            return result
        except Exception as e:
            logger.warning(f"[{self.engine_name}] Primary Sarvam extraction failed: {e}")

        # 2. Fallback: Local PyMuPDF Engine
        fallback = PyMuPDFEngine()
        res = fallback.extract(file_path)
        res["engine"] = f"{self.engine_name} (PyMuPDF Fallback)"
        res["document_type"] = "image"
        return res
