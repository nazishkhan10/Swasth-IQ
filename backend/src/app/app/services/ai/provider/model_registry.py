"""
Model Registry (Phase 7 — Architecture Freeze v8.2).
Configuration-driven model abstraction returning primary reasoning model `gpt-5-nano`.
Enables effortless future model updates (e.g., Azure OpenAI, Llama) without code refactoring.
"""

import os
from typing import Dict, Any

class ModelRegistry:
    """Configuration-driven registry for LLM Models."""

    DEFAULT_PROVIDER = "OpenAI"
    DEFAULT_MODEL = "gpt-5-nano"

    MODELS = {
        "gpt-5-nano": {
            "provider": "OpenAI",
            "model_name": "gpt-5-nano",
            "cost_input_per_1m": 0.05,
            "cost_output_per_1m": 0.40,
            "max_tokens": 4096,
            "supports_json_schema": True
        }
    }

    @classmethod
    def get_primary_model_config(cls) -> Dict[str, Any]:
        target = os.environ.get("PRIMARY_AI_MODEL", cls.DEFAULT_MODEL)
        return cls.MODELS.get(target, cls.MODELS[cls.DEFAULT_MODEL])
