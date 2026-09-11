"""
Duplicate Resolver Service.
Resolves duplicate parameter extractions by selecting the highest-confidence and table-aligned instances.
"""

from typing import List, Dict, Any, Tuple

class DuplicateResolver:
    """Selects the canonical medical value when multiple OCR blocks match the same parameter."""

    @classmethod
    def resolve(cls, extracted_params: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        resolved: Dict[str, Dict[str, Any]] = {}
        warnings: List[Dict[str, Any]] = []

        for item in extracted_params:
            code = item.get("parameter_code") or item.get("parameter_name")
            if not code:
                continue

            if code not in resolved:
                resolved[code] = item
            else:
                existing = resolved[code]

                # Scoring criteria:
                # 1. Has valid numeric value (+10)
                # 2. Table source (+5)
                # 3. Has unit (+3)
                # 4. Has reference range (+2)
                # 5. Higher confidence (+confidence)

                def score(entry: Dict[str, Any]) -> float:
                    s = 0.0
                    if entry.get("numeric_value") is not None:
                        s += 10.0
                    if entry.get("source") in ["table", "space_table"]:
                        s += 5.0
                    if entry.get("unit"):
                        s += 3.0
                    if entry.get("reference_range"):
                        s += 2.0
                    s += float(entry.get("confidence", 0.0))
                    return s

                if score(item) > score(existing):
                    resolved[code] = item

                warnings.append({
                    "page_number": item.get("page_number", 1),
                    "parameter_name": item.get("parameter_name"),
                    "warning_type": "Duplicate Value",
                    "message": f"Duplicate entry for '{item.get('parameter_name')}' resolved. Selected value: '{resolved[code].get('value')}'"
                })

        return list(resolved.values()), warnings
