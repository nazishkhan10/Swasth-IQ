"""
JSON Schema Validator (Phase 7 Medical AI - Architecture v8.0).
Validates GPT responses against structured schema and enforces standard output formats.
"""

import json
from typing import Dict, Any, Tuple

class JSONSchemaValidator:
    """Validates medical insight JSON outputs."""

    REQUIRED_KEYS = ["summary", "explanation", "evidence", "confidence", "disclaimer"]

    @classmethod
    def validate_insight(cls, raw_response: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Parses and validates structured medical insight responses.
        Returns (is_valid, parsed_dict, error_message).
        """
        try:
            # Strip markdown codeblock backticks if present
            clean_text = raw_response.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

            data = json.loads(clean_text)
            if not isinstance(data, dict):
                return False, {}, "Output is not a JSON object."

            missing = [k for k in cls.REQUIRED_KEYS if k not in data]
            if missing:
                return False, data, f"Missing required keys: {', '.join(missing)}"

            return True, data, ""
        except Exception as e:
            return False, {}, f"JSON Parsing Error: {str(e)}"
