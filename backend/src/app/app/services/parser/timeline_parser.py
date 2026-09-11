"""
Timeline Parser Strategy Service.
Parses Longitudinal Patient History Tracking Reports containing multiple diagnostic encounter visits.
"""

import re
from typing import List, Dict, Any, Tuple
from app.services.parser.parameter_resolver import ParameterResolver
from app.services.parser.unit_normalizer import UnitNormalizer
from app.services.parser.value_parser import ValueParser
from app.services.parser.reference_range_parser import ReferenceRangeParser
from app.logs.logger import logger


class TimelineParser:
    """Parses multi-visit longitudinal timeline reports into structured encounter records."""

    @classmethod
    def parse(cls, pages: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        extracted_params = []
        warnings = []

        full_text = "\n".join([p.get("text", "") for p in pages if p.get("text")])
        if not full_text:
            return extracted_params, warnings

        # Split text into visit blocks e.g. "[VISIT 1] Baseline Encounter - 2024-06-19"
        visit_blocks = re.split(r"(?=\[VISIT\s*\d+\]|\bVISIT\s*\d+\b)", full_text, flags=re.IGNORECASE)

        for v_idx, block in enumerate(visit_blocks):
            b_text = block.strip()
            if not b_text or not re.search(r"VISIT\s*\d+", b_text, re.IGNORECASE):
                continue

            # Extract Visit Number, Title, Date
            header_match = re.search(r"(?:\[VISIT\s*(\d+)\]|VISIT\s*(\d+))\s*([^-\n]*)\s*(?:-\s*(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}))?", b_text, re.IGNORECASE)
            visit_num = header_match.group(1) or header_match.group(2) if header_match else str(v_idx + 1)
            visit_title = header_match.group(3).strip() if header_match and header_match.group(3) else f"Encounter {visit_num}"
            visit_date = header_match.group(4) if header_match and header_match.group(4) else None

            # Extract Facility
            fac_match = re.search(r"(?:facility|lab|hospital)\s*[:\-]\s*([^\n]+)", b_text, re.IGNORECASE)
            facility = fac_match.group(1).strip() if fac_match else "Unspecified Facility"

            lines = b_text.splitlines()
            for l_idx, line in enumerate(lines):
                line_clean = line.strip()
                if not line_clean or "VISIT" in line_clean.upper() or "FACILITY" in line_clean.upper():
                    continue

                # Key-Value match: "HbA1c : 6.8 % (Elevated)" or "Vit D : 22.0 ng/ml (Insufficient)"
                match = re.search(r"^([A-Za-z0-9\s\(\)\-\/\.\%]+?)\s*[:\-]\s+([<>=]*\s*[\d\.]+)\s*([A-Za-z\/\%µ\^\d]*)\s*(\(.*?\))?$", line_clean)
                if match:
                    p_str = match.group(1).strip()
                    v_str = match.group(2).strip()
                    u_str = match.group(3).strip()
                    r_str = match.group(4) or ""

                    param_info = ParameterResolver.resolve(p_str)
                    if not param_info:
                        paren_match = re.search(r"\(([^\)]+)\)", p_str)
                        if paren_match:
                            param_info = ParameterResolver.resolve(paren_match.group(1))

                    if param_info:
                        val_text, num_val = ValueParser.parse(v_str)
                        norm_unit = UnitNormalizer.normalize(u_str)
                        ref_info = ReferenceRangeParser.parse(r_str)

                        # Contextualize parameter name with Visit tag to differentiate timeline parameters
                        extracted_params.append({
                            "page_number": 1,
                            "block_id": f"v{visit_num}_l{l_idx+1}",
                            "parameter_name": f"{param_info['name']} (Visit {visit_num} - {visit_date or 'Historical'})",
                            "parameter_code": f"{param_info['code']}_V{visit_num}",
                            "category": "Timeline Encounter",
                            "value": val_text,
                            "numeric_value": num_val,
                            "unit": norm_unit,
                            "reference_range": ref_info["raw"] or r_str.strip("()"),
                            "reference_context": f"Facility: {facility} | Date: {visit_date or 'Historical'}",
                            "reference_low": ref_info["low"],
                            "reference_high": ref_info["high"],
                            "status": "Pending Validation",
                            "confidence": 0.95,
                            "bbox": "[0, 0, 0, 0]",
                            "source": "timeline"
                        })

        if not extracted_params:
            warnings.append({
                "page_number": 1,
                "parameter_name": None,
                "warning_type": "Timeline Extraction Warning",
                "message": "Longitudinal report detected but no visit parameters could be parsed."
            })

        return extracted_params, warnings
