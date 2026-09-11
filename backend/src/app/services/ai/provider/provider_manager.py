"""
Provider Manager Facade Gateway (Phase 7 AI Engine - Architecture v8.0).
Clean, minimal abstraction layer delegating directly to OpenAIProvider (GPT-5-Nano).
Provides seamless future extensibility without application code rewrites.
"""

import logging
from typing import Dict, Any, Generator, List
from app.services.ai.provider.openai_provider import OpenAIProvider

logger = logging.getLogger("medical_report_analyzer")


class ProviderManager:
    """Minimal abstraction facade for LLM Providers."""

    def __init__(self, model_name: str = "gpt-5-nano"):
        self.primary_provider = OpenAIProvider(model_name=model_name)

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """Delegates chat completion requests to the active primary OpenAI provider."""
        return self.primary_provider.generate(messages, temperature, max_tokens, json_mode)

    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> Generator[Dict[str, Any], None, None]:
        """Streams response tokens from the active primary OpenAI provider."""
        for chunk in self.primary_provider.stream(messages, temperature, max_tokens):
            yield {
                "text": chunk,
                "provider": self.primary_provider.provider_name,
                "is_fallback": False
            }

    def get_health(self) -> Dict[str, Any]:
        """Returns health metrics for the OpenAI provider gateway."""
        return {
            "openai_available": self.primary_provider.is_available(),
            "active_primary": self.primary_provider.provider_name,
            "architecture_version": "v8.0-Freeze"
        }
