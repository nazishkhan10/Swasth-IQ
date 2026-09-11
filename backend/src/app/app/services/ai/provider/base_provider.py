"""
Base LLM Provider Interface (Phase 7 — AI Engine).
Defines standard contract for Sarvam 105B Primary and GLM 4.7 Fallback providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Generator, List


class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns provider human readable identifier."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Checks if provider API key is present and service is reachable."""
        pass

    @abstractmethod
    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """Synchronous chat completion."""
        pass

    @abstractmethod
    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> Generator[str, None, None]:
        """Streaming token iterator (yields text chunks)."""
        pass
