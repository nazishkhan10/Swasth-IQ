"""
Schema Registry (Phase 7 Medical AI — Architecture Freeze v8.2).
Manages intent-specific JSON output schemas for GPT-5 Nano.
"""

from typing import Dict, Any, List

class SchemaRegistry:
    """Registry of intent-specific JSON output schemas."""

    SCHEMAS = {
        "report_summary": {
            "type": "object",
            "required": ["summary", "findings", "explanation", "meaning", "lifestyle", "evidence", "follow_up", "disclaimer"],
            "properties": {
                "summary": {"type": "string"},
                "findings": {"type": "array"},
                "explanation": {"type": "string"},
                "meaning": {"type": "string"},
                "lifestyle": {"type": "array"},
                "evidence": {"type": "array"},
                "follow_up": {"type": "array"},
                "disclaimer": {"type": "string"}
            }
        },
        "parameter_explanation": {
            "type": "object",
            "required": ["summary", "findings", "explanation", "meaning", "lifestyle", "evidence", "follow_up", "disclaimer"],
            "properties": {
                "summary": {"type": "string"},
                "findings": {"type": "array"},
                "explanation": {"type": "string"},
                "meaning": {"type": "string"},
                "lifestyle": {"type": "array"},
                "evidence": {"type": "array"},
                "follow_up": {"type": "array"},
                "disclaimer": {"type": "string"}
            }
        },
        "condition_explanation": {
            "type": "object",
            "required": ["summary", "findings", "explanation", "meaning", "lifestyle", "evidence", "follow_up", "disclaimer"],
            "properties": {
                "summary": {"type": "string"},
                "findings": {"type": "array"},
                "explanation": {"type": "string"},
                "meaning": {"type": "string"},
                "lifestyle": {"type": "array"},
                "evidence": {"type": "array"},
                "follow_up": {"type": "array"},
                "disclaimer": {"type": "string"}
            }
        }
    }

    @classmethod
    def get_schema(cls, intent: str) -> Dict[str, Any]:
        return cls.SCHEMAS.get(intent, cls.SCHEMAS["report_summary"])
