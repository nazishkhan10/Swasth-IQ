import fitz  # PyMuPDF
import time
from typing import Dict, Any, List
from app.services.ocr.base import BaseOCREngine
from app.logs.logger import logger


class PyMuPDFEngine(BaseOCREngine):
    engine_name = "PyMuPDF"

    def extract(self, file_path: str) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"[{self.engine_name}] Starting extraction for: {file_path}")

        doc = fitz.open(file_path)
        page_count = len(doc)
        pages_output: List[Dict[str, Any]] = []
        total_confidence = 0.0

        for page_idx in range(page_count):
            page = doc.load_page(page_idx)
            page_num = page_idx + 1

            # Extract raw text
            page_text = page.get_text("text") or ""
            
            # Extract structured blocks with coordinates
            # page.get_text("blocks") returns list of tuples: (x0, y0, x1, y1, text, block_no, block_type)
            raw_blocks = page.get_text("blocks")
            blocks: List[Dict[str, Any]] = []
            headers: List[str] = []
            lists: List[str] = []

            for b_idx, b in enumerate(raw_blocks):
                x0, y0, x1, y1, text, block_no, block_type = b[0], b[1], b[2], b[3], b[4], b[5], b[6]
                clean_text = text.strip()
                if not clean_text:
                    continue

                # Determine block type heuristic (header, list, paragraph)
                b_type = "paragraph"
                if len(clean_text) < 60 and (clean_text.isupper() or clean_text.endswith(":") or y0 < 100):
                    b_type = "header"
                    headers.append(clean_text)
                elif clean_text.startswith(("-", "•", "*", "1.", "2.", "3.")):
                    b_type = "list"
                    lists.append(clean_text)

                blocks.append({
                    "id": f"b{page_num}_{b_idx+1}",
                    "type": b_type,
                    "text": clean_text,
                    "bbox": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)]
                })

            # Extract tables using PyMuPDF table finder
            tables: List[Dict[str, Any]] = []
            try:
                tabs = page.find_tables()
                if tabs and tabs.tables:
                    for t in tabs.tables:
                        extracted = t.extract()
                        if extracted and len(extracted) > 0:
                            header_row = [str(cell or "").strip() for cell in extracted[0]]
                            body_rows = [[str(cell or "").strip() for cell in row] for row in extracted[1:]]
                            tables.append({
                                "headers": header_row,
                                "rows": body_rows,
                                "bbox": [round(t.bbox[0], 2), round(t.bbox[1], 2), round(t.bbox[2], 2), round(t.bbox[3], 2)]
                            })
            except Exception as te:
                logger.warning(f"[{self.engine_name}] Table extraction warning on page {page_num}: {te}")

            # Images metadata
            image_list = page.get_images(full=True)
            images_metadata = [{"id": f"img_{page_num}_{i+1}", "width": img[2], "height": img[3]} for i, img in enumerate(image_list)]

            # Confidence scoring: Digital PDF has native vector text layout -> high confidence
            page_conf = 0.98 if len(page_text.strip()) > 30 else 0.85
            total_confidence += page_conf

            pages_output.append({
                "page": page_num,
                "confidence": round(page_conf, 2),
                "text": page_text,
                "blocks": blocks,
                "tables": tables,
                "headers": headers,
                "lists": lists,
                "images_metadata": images_metadata
            })

        doc.close()
        proc_time = round(time.time() - start_time, 3)
        avg_conf = round(total_confidence / page_count, 2) if page_count > 0 else 0.0

        logger.info(f"[{self.engine_name}] Extraction completed in {proc_time}s across {page_count} pages with avg confidence {avg_conf}")

        return {
            "document_type": "digital_pdf",
            "engine": self.engine_name,
            "confidence": avg_conf,
            "page_count": page_count,
            "processing_time": proc_time,
            "pages": pages_output
        }
