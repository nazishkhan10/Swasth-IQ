import os
import json
from typing import Dict, Any, Optional
from app.logs.logger import logger

BASE_OCR_RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ocr_results")


def get_ocr_result_dir(report_uuid: str, version: int = 1) -> str:
    """Returns the directory path for a report version's OCR JSON results."""
    target_dir = os.path.join(BASE_OCR_RESULTS_DIR, str(report_uuid), f"v{version}")
    os.makedirs(target_dir, exist_ok=True)
    return target_dir


def save_page_json(report_uuid: str, version: int, page_number: int, page_data: Dict[str, Any]) -> str:
    """Saves page structured OCR data as a JSON file and returns relative path."""
    target_dir = get_ocr_result_dir(report_uuid, version)
    file_name = f"page_{page_number}.json"
    full_path = os.path.join(target_dir, file_name)
    
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(page_data, f, indent=2, ensure_ascii=False)
        
    rel_path = os.path.relpath(full_path, os.path.dirname(BASE_OCR_RESULTS_DIR))
    logger.info(f"Saved page JSON [Report: {report_uuid}, v{version}, Page: {page_number}] to {rel_path}")
    return rel_path.replace("\\", "/")


def load_page_json(rel_path: str) -> Optional[Dict[str, Any]]:
    """Loads page structured OCR data from stored JSON file."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    full_path = os.path.normpath(os.path.join(base_dir, rel_path))
    
    if not os.path.exists(full_path):
        logger.error(f"OCR JSON file not found: {full_path}")
        return None
        
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read OCR JSON file {full_path}: {e}")
        return None
