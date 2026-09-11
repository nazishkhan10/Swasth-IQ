from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseOCREngine(ABC):
    """Abstract Base Class for all OCR & Document Intelligence Engines."""
    
    engine_name: str = "BaseEngine"

    @abstractmethod
    def extract(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text, structure, tables, and blocks from target document file.
        Must return dict conforming to Unified OCR JSON Schema:
        {
            "document_type": "digital_pdf" | "scanned_pdf" | "image" | "txt",
            "engine": str,
            "confidence": float,
            "page_count": int,
            "processing_time": float,
            "pages": [
                {
                    "page": int,
                    "confidence": float,
                    "text": str,
                    "blocks": [
                        {
                            "id": str,
                            "type": str, # "header", "paragraph", "table", "list", "line"
                            "text": str,
                            "bbox": [x0, y0, x1, y1]
                        }
                    ],
                    "tables": [
                        {
                            "headers": List[str],
                            "rows": List[List[str]],
                            "bbox": [x0, y0, x1, y1]
                        }
                    ],
                    "headers": List[str],
                    "lists": List[str],
                    "images_metadata": List[dict]
                }
            ]
        }
        """
        pass
