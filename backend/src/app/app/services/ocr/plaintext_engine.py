import time
from typing import Dict, Any, List
from app.services.ocr.base import BaseOCREngine
from app.logs.logger import logger


class PlainTextEngine(BaseOCREngine):
    engine_name = "PlainText"

    def extract(self, file_path: str) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"[{self.engine_name}] Reading raw text file: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            logger.error(f"[{self.engine_name}] Failed to read file {file_path}: {e}")
            content = ""

        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        blocks: List[Dict[str, Any]] = []
        headers: List[str] = []
        lists: List[str] = []
        tables: List[Dict[str, Any]] = []

        # Parse pseudo-tables or formatted text blocks
        for idx, p in enumerate(paragraphs):
            lines = [l.strip() for l in p.split("\n") if l.strip()]
            first_line = lines[0] if lines else ""

            b_type = "paragraph"
            if len(first_line) < 50 and (first_line.isupper() or first_line.endswith(":")):
                b_type = "header"
                headers.append(first_line)
            elif first_line.startswith(("-", "•", "*", "1.", "2.")):
                b_type = "list"
                lists.append(first_line)

            # Simple tabular detection in text (if lines contain tabs or multiple spaces/colons)
            if len(lines) >= 2 and any("\t" in l or "  " in l or ":" in l for l in lines):
                table_rows = []
                for line in lines:
                    parts = [pt.strip() for pt in line.replace("\t", "  ").split("  ") if pt.strip()]
                    if len(parts) >= 2:
                        table_rows.append(parts)
                if len(table_rows) >= 2:
                    tables.append({
                        "headers": table_rows[0],
                        "rows": table_rows[1:],
                        "bbox": [0, 0, 100, 100]
                    })

            blocks.append({
                "id": f"b1_{idx+1}",
                "type": b_type,
                "text": p,
                "bbox": [10, 10 + (idx * 40), 500, 40 + (idx * 40)]
            })

        proc_time = round(time.time() - start_time, 3)

        return {
            "document_type": "txt",
            "engine": self.engine_name,
            "confidence": 1.0,
            "page_count": 1,
            "processing_time": proc_time,
            "pages": [
                {
                    "page": 1,
                    "confidence": 1.0,
                    "text": content,
                    "blocks": blocks,
                    "tables": tables,
                    "headers": headers,
                    "lists": lists,
                    "images_metadata": []
                }
            ]
        }
