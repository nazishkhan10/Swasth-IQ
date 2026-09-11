"""
Parser Rules Engine.
Executes Markdown table parsing (`|`-separated rows), space-aligned table parsing, retrospective token parsing,
and line-by-line regex extraction with smart cell-type auto-detection to guarantee column alignment.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from app.services.parser.parameter_resolver import ParameterResolver
from app.services.parser.unit_normalizer import UnitNormalizer
from app.services.parser.value_parser import ValueParser
from app.services.parser.reference_range_parser import ReferenceRangeParser
from app.logs.logger import logger

class ParserRules:
    """Combines Markdown table parsing, retrospective space line tokenization, and line regex parsing."""

    @classmethod
    def _parse_line_retrospective(cls, line: str) -> Optional[Dict[str, Any]]:
        text = line.strip()
        if not text or re.search(r"^(haematology|hematology|complete blood count|cbc|rbc indices|platelets? indices|differential|absolute leucocyte|test description|interpretation)", text, re.IGNORECASE):
            return None

        # Find where numeric value begins in line (e.g. "HbA1c 8.4 %" -> param: "HbA1c", val_part: "8.4 %")
        num_start = re.search(r"\s+([<>=]*\s*[\d\.]+)", text)
        if not num_start:
            return None

        raw_param = text[:num_start.start()].strip()
        remainder = text[num_start.start():].strip()

        # Clean flags L/H/N and punctuation like commas from raw_param
        clean_param = re.sub(r"[\s,]+[L|H|N]\b", "", raw_param, flags=re.IGNORECASE).strip()
        clean_param = re.sub(r"[,:]", "", clean_param).strip()
        param_info = ParameterResolver.resolve(clean_param)

        if not param_info:
            paren_match = re.search(r"\(([^\)]+)\)", clean_param)
            if paren_match:
                param_info = ParameterResolver.resolve(paren_match.group(1))

        if not param_info:
            return None

        remainder = re.sub(r"(\d+),(\d+)", r"\1\2", remainder)

        units_pattern = r"(g/dL|g/dl|/cumm|cumm|lakhs/cumm|million/cumm|Mil-\s*lion/cumm|Million/cumm|/cu\.mm|lakh/cu\.mm|thou/cu\.mm|10\^3/µL|10\^6/µL|%|fl|fL|pg|Pg|mg/dL|mL/min/1\.73m2|mL/min|uIU/mL|µIU/mL)"
        unit_match = re.search(units_pattern, remainder, re.IGNORECASE)
        raw_unit = unit_match.group(1).strip() if unit_match else ""
        if unit_match:
            remainder_no_unit = remainder[:unit_match.start()] + " " + remainder[unit_match.end():]
        else:
            remainder_no_unit = remainder

        ref_match = re.search(r"(\d+\.?\d*\s*(?:-|–|to)\s*\d+\.?\d*|[<>=]\s*[\d\.]+)", remainder_no_unit, re.IGNORECASE)
        raw_ref = ref_match.group(1).strip() if ref_match else ""
        if ref_match:
            remainder_vals = remainder_no_unit[:ref_match.start()] + " " + remainder_no_unit[ref_match.end():]
        else:
            remainder_vals = remainder_no_unit

        val_match = re.search(r"([<>=]*\s*[\d\.]+)", remainder_vals)
        if not val_match:
            return None

        raw_val = val_match.group(1).strip()
        val_text, num_val = ValueParser.parse(raw_val)
        norm_unit = UnitNormalizer.normalize(raw_unit)
        ref_info = ReferenceRangeParser.parse(raw_ref)

        return {
            "parameter_name": param_info["name"],
            "parameter_code": param_info["code"],
            "category": param_info["category"],
            "value": val_text,
            "numeric_value": num_val,
            "unit": norm_unit,
            "reference_range": ref_info["raw"],
            "reference_context": ref_info["context"],
            "reference_low": ref_info["low"],
            "reference_high": ref_info["high"]
        }


    @classmethod
    def _parse_row_smart(cls, cols: List[str], header_map: Dict[str, int]) -> Optional[Dict[str, Any]]:
        """
        Smartly parses a row of table cells into (param_info, raw_val, raw_unit, raw_ref).
        Uses header_map as baseline and applies cell-type classification heuristics to prevent column shift.
        """
        clean_cols = [c.strip() for c in cols if c and c.strip()]
        if len(clean_cols) < 2:
            return None

        # 1. Parameter cell
        param_idx = header_map.get("param", 0)
        raw_param = clean_cols[param_idx] if param_idx < len(clean_cols) else clean_cols[0]

        # Check if single-space attached a numeric value to parameter string e.g. "Blood Urea Nitrogen (BUN) 26.4"
        attached_num_match = re.search(r"^(.*?)\s+([<>=]*\s*\d+\.?\d+)$", raw_param)
        if attached_num_match:
            candidate_param = attached_num_match.group(1).strip()
            candidate_val = attached_num_match.group(2).strip()
            p_check = ParameterResolver.resolve(candidate_param)
            if p_check:
                raw_param = candidate_param
                clean_cols = [candidate_param, candidate_val] + [clean_cols[i] for i in range(len(clean_cols)) if i != param_idx]
                param_idx = 0

        param_info = ParameterResolver.resolve(raw_param)
        if not param_info:
            paren_match = re.search(r"\(([^\)]+)\)", raw_param)
            if paren_match:
                param_info = ParameterResolver.resolve(paren_match.group(1))

        if not param_info:
            return None

        # Remaining cells after parameter
        remaining_cols = [clean_cols[i] for i in range(len(clean_cols)) if i != param_idx]

        raw_val = ""
        raw_unit = ""
        raw_ref = ""

        # 2. Smart Cell Classification among remaining_cols
        # A) Find Reference Range cell (matches "13.5-17.5", "0.74–1.35", "> 60", ">60", "<100", "< 0.0 - 5.2", "70 - 114")
        ref_cell_idx = -1
        for i, cell in enumerate(remaining_cols):
            c_clean = cell.strip()
            if re.search(r"\d+\.?\d*\s*(?:-|–|to)\s*\d+\.?\d*|^[<>=]\s*[\d\.]+$", c_clean, re.IGNORECASE):
                ref_cell_idx = i
                raw_ref = c_clean
                break

        # B) Find Unit cell (matches %, mg/dL, mL/min, uIU/mL, etc.)
        unit_cell_idx = -1
        for i, cell in enumerate(remaining_cols):
            if i == ref_cell_idx:
                continue
            c_clean = cell.strip()
            if UnitNormalizer.is_known_unit(c_clean):
                unit_cell_idx = i
                raw_unit = c_clean
                break

        # C) Find Value cell (numeric float/integer e.g. "8.4", "54", "1.48", "6.8", "242", "161", "189", "26.4")
        val_cell_idx = -1
        for i, cell in enumerate(remaining_cols):
            if i == ref_cell_idx or i == unit_cell_idx:
                continue
            c_clean = cell.strip()
            if re.search(r"^[<>=]*\s*[\d\.]+$|^Negative$|^Positive$|^Trace$|^Nil$", c_clean, re.IGNORECASE):
                val_cell_idx = i
                raw_val = c_clean
                break

        # Fallback to header map if smart detection left anything empty
        if not raw_val:
            v_i = header_map.get("val", 1)
            raw_val = clean_cols[v_i] if v_i < len(clean_cols) else (remaining_cols[0] if remaining_cols else "")
        if not raw_unit:
            u_i = header_map.get("unit", 2)
            raw_unit = clean_cols[u_i] if u_i < len(clean_cols) else ""
        if not raw_ref:
            r_i = header_map.get("ref", 3)
            raw_ref = clean_cols[r_i] if r_i < len(clean_cols) else ""

        val_text, num_val = ValueParser.parse(raw_val)
        norm_unit = UnitNormalizer.normalize(raw_unit)
        ref_info = ReferenceRangeParser.parse(raw_ref)

        return {
            "parameter_name": param_info["name"],
            "parameter_code": param_info["code"],
            "category": param_info["category"],
            "value": val_text,
            "numeric_value": num_val,
            "unit": norm_unit,
            "reference_range": ref_info["raw"],
            "reference_context": ref_info["context"],
            "reference_low": ref_info["low"],
            "reference_high": ref_info["high"]
        }

    @classmethod
    def extract_from_markdown_tables(cls, pages: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        extracted = []
        warnings = []

        for page in pages:
            page_num = page.get("page", 1)
            text = page.get("text", "")
            if not text:
                continue

            lines = text.splitlines()
            header_map = {"param": 0, "val": 1, "unit": 2, "ref": 3}

            for line_no, line in enumerate(lines):
                clean_line = line.strip()
                if not clean_line or "|" not in clean_line:
                    continue

                if re.match(r"^[\s\|\-\:]+$", clean_line):
                    continue

                cols = [c.strip() for c in clean_line.split("|")]
                if cols and not cols[0]:
                    cols.pop(0)
                if cols and not cols[-1]:
                    cols.pop()

                if len(cols) < 2:
                    continue

                first_col_lower = cols[0].lower()
                if any(k in first_col_lower for k in ["parameter", "test", "investigation", "description"]):
                    for idx, c in enumerate(cols):
                        c_lower = c.lower()
                        if any(k in c_lower for k in ["parameter", "test", "description"]):
                            header_map["param"] = idx
                        elif any(k in c_lower for k in ["result", "value", "observed"]):
                            header_map["val"] = idx
                        elif any(k in c_lower for k in ["unit"]):
                            header_map["unit"] = idx
                        elif any(k in c_lower for k in ["reference", "range", "interval"]):
                            header_map["ref"] = idx
                    continue

                parsed = cls._parse_row_smart(cols, header_map)
                if parsed:
                    if not parsed["unit"]:
                        warnings.append({
                            "page_number": page_num,
                            "parameter_name": parsed["parameter_name"],
                            "warning_type": "Missing Unit",
                            "message": f"Unit missing for parameter '{parsed['parameter_name']}'."
                        })
                    if not parsed["reference_range"]:
                        warnings.append({
                            "page_number": page_num,
                            "parameter_name": parsed["parameter_name"],
                            "warning_type": "Missing Reference Range",
                            "message": f"Reference range missing for parameter '{parsed['parameter_name']}'."
                        })

                    extracted.append({
                        "page_number": page_num,
                        "block_id": f"md_p{page_num}_l{line_no+1}",
                        "parameter_name": parsed["parameter_name"],
                        "parameter_code": parsed["parameter_code"],
                        "category": parsed["category"],
                        "value": parsed["value"],
                        "numeric_value": parsed["numeric_value"],
                        "unit": parsed["unit"],
                        "reference_range": parsed["reference_range"],
                        "reference_context": parsed["reference_context"],
                        "reference_low": parsed["reference_low"],
                        "reference_high": parsed["reference_high"],
                        "status": "Pending Validation",
                        "confidence": 0.96,
                        "bbox": "[10, 10, 500, 500]",
                        "source": "table"
                    })

        return extracted, warnings

    @classmethod
    def extract_from_tables(cls, pages: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        extracted = []
        warnings = []

        for page in pages:
            page_num = page.get("page", 1)
            tables = page.get("tables", [])

            for t_idx, table in enumerate(tables):
                headers = [str(h).lower().strip() for h in table.get("headers", [])]
                rows = table.get("rows", [])

                header_map = {"param": 0, "val": 1, "unit": 2, "ref": 3}
                for idx, col in enumerate(headers):
                    if any(k in col for k in ["parameter", "test", "description"]):
                        header_map["param"] = idx
                    elif any(k in col for k in ["result", "value", "observed"]):
                        header_map["val"] = idx
                    elif any(k in col for k in ["unit"]):
                        header_map["unit"] = idx
                    elif any(k in col for k in ["reference", "range", "interval"]):
                        header_map["ref"] = idx

                for r_idx, row in enumerate(rows):
                    cols = [str(cell or "").strip() for cell in row]
                    parsed = cls._parse_row_smart(cols, header_map)
                    if parsed:
                        extracted.append({
                            "page_number": page_num,
                            "block_id": f"t{page_num}_{t_idx+1}_r{r_idx+1}",
                            "parameter_name": parsed["parameter_name"],
                            "parameter_code": parsed["parameter_code"],
                            "category": parsed["category"],
                            "value": parsed["value"],
                            "numeric_value": parsed["numeric_value"],
                            "unit": parsed["unit"],
                            "reference_range": parsed["reference_range"],
                            "reference_context": parsed["reference_context"],
                            "reference_low": parsed["reference_low"],
                            "reference_high": parsed["reference_high"],
                            "status": "Pending Validation",
                            "confidence": 0.95,
                            "bbox": str(table.get("bbox", [])),
                            "source": "table"
                        })

        return extracted, warnings

    @classmethod
    def extract_from_blocks(cls, pages: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        extracted = []
        warnings = []

        for page in pages:
            page_num = page.get("page", 1)
            blocks = page.get("blocks", [])

            for block in blocks:
                text = block.get("text", "").strip()
                if not text:
                    continue

                lines = text.splitlines()
                header_map = {"param": 0, "val": 1, "unit": 2, "ref": 3}

                for line_no, line in enumerate(lines):
                    line_clean = line.strip()
                    if not line_clean or "|" in line_clean:
                        continue

                    # 1. Try retrospective right-to-left un-delimited line tokenization
                    retro_parsed = cls._parse_line_retrospective(line_clean)
                    if retro_parsed:
                        extracted.append({
                            "page_number": page_num,
                            "block_id": f"p{page_num}_l{line_no+1}",
                            "parameter_name": retro_parsed["parameter_name"],
                            "parameter_code": retro_parsed["parameter_code"],
                            "category": retro_parsed["category"],
                            "value": retro_parsed["value"],
                            "numeric_value": retro_parsed["numeric_value"],
                            "unit": retro_parsed["unit"],
                            "reference_range": retro_parsed["reference_range"],
                            "reference_context": retro_parsed["reference_context"],
                            "reference_low": retro_parsed["reference_low"],
                            "reference_high": retro_parsed["reference_high"],
                            "status": "Pending Validation",
                            "confidence": round(float(block.get("confidence", 0.94)), 2),
                            "bbox": str(block.get("bbox", [])),
                            "source": "line"
                        })
                        continue

                    # 2. Check space-aligned columns (2+ spaces)
                    space_cols = [c.strip() for c in re.split(r"\s{2,}", line_clean) if c.strip()]
                    if len(space_cols) >= 2:
                        first_lower = space_cols[0].lower()
                        if any(k in first_lower for k in ["parameter", "test", "investigation"]):
                            for idx, c in enumerate(space_cols):
                                c_lower = c.lower()
                                if any(k in c_lower for k in ["parameter", "test"]):
                                    header_map["param"] = idx
                                elif any(k in c_lower for k in ["result", "value"]):
                                    header_map["val"] = idx
                                elif any(k in c_lower for k in ["unit"]):
                                    header_map["unit"] = idx
                                elif any(k in c_lower for k in ["reference", "range"]):
                                    header_map["ref"] = idx
                            continue

                        parsed = cls._parse_row_smart(space_cols, header_map)
                        if parsed:
                            extracted.append({
                                "page_number": page_num,
                                "block_id": block.get("id"),
                                "parameter_name": parsed["parameter_name"],
                                "parameter_code": parsed["parameter_code"],
                                "category": parsed["category"],
                                "value": parsed["value"],
                                "numeric_value": parsed["numeric_value"],
                                "unit": parsed["unit"],
                                "reference_range": parsed["reference_range"],
                                "reference_context": parsed["reference_context"],
                                "reference_low": parsed["reference_low"],
                                "reference_high": parsed["reference_high"],
                                "status": "Pending Validation",
                                "confidence": round(float(block.get("confidence", 0.90)), 2),
                                "bbox": str(block.get("bbox", [])),
                                "source": "space_table"
                            })
                            continue

        return extracted, warnings
