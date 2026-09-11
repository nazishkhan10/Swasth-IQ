import time
from typing import Dict, Any
from app.services.ocr.base import BaseOCREngine
from app.services.ocr.sarvam_doc_engine import SarvamDocEngine
from app.services.ocr.tesseract_engine import TesseractEngine
from app.logs.logger import logger


class SarvamVisionEngine(BaseOCREngine):
    """
    Sarvam AI Vision OCR Engine for Image reports (JPG, PNG, JPEG).
    Fallback Chain: Sarvam Vision -> Sarvam Document Intelligence -> PyMuPDF Free Fallback
    """
    engine_name = "Sarvam Vision OCR"

    def extract(self, file_path: str) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"[{self.engine_name}] Processing image report: {file_path}")

        # 1. Primary Engine: Sarvam AI Vision / Digitise Engine
        try:
            sarvam_doc = SarvamDocEngine()
            result = sarvam_doc.extract(file_path)
            result["engine"] = self.engine_name
            result["document_type"] = "image"
            logger.info(f"[{self.engine_name}] Primary Vision extraction successful for: {file_path}")
            return result
        except Exception as e:
            logger.warning(f"[{self.engine_name}] Primary Vision failed ({e}). Fallback 1: Sarvam Document Mode.")

        # 2. Fallback 1: Sarvam Document Mode
        try:
            sarvam_doc = SarvamDocEngine()
            result = sarvam_doc.extract(file_path)
            result["engine"] = f"{self.engine_name} (Fallback 1: Sarvam Doc)"
            result["document_type"] = "image"
            logger.info(f"[{self.engine_name}] Fallback 1 Sarvam Doc extraction successful for: {file_path}")
            return result
        except Exception as e:
            logger.warning(f"[{self.engine_name}] Fallback 1 failed ({e}). Fallback 2: Free Local PyMuPDF / Tesseract.")

        # 3. Fallback 2: Free & Reliable Local PyMuPDF Engine
        fallback = PyMuPDFEngine()
        res = fallback.extract(file_path)
        res["engine"] = f"{self.engine_name} (Fallback 2: Free PyMuPDF)"
        res["document_type"] = "image"
        return res


