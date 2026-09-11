"""
Parameter Resolver Service.
Resolves raw OCR text strings to canonical parameter names, codes, and categories.
"""

import re
from typing import Optional, Dict, Any
from app.services.parser.parameter_dictionary import PARAMETER_DICTIONARY

class ParameterResolver:
    """Matches parameter aliases and regexes to standard Parameter objects."""

    @classmethod
    def resolve(cls, text: str) -> Optional[Dict[str, Any]]:
        clean_text = text.strip()
        if not clean_text:
            return None

        for param in PARAMETER_DICTIONARY:
            # Check canonical name exact / case-insensitive
            if param["name"].lower() == clean_text.lower():
                return param
            
            # Check aliases
            for alias in param["aliases"]:
                if re.search(alias, clean_text, re.IGNORECASE):
                    return param

        return None
