"""
OpenAI Primary LLM Provider (Phase 7 AI Engine - Architecture v8.0).
Single primary reasoning engine targeting GPT-5-Nano via REST API.
"""

import os
import re
import json
import time
import requests
from typing import Dict, Any, Generator, List
from app.services.ai.provider.base_provider import BaseLLMProvider
from app.core.config import settings


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT-5-Nano Primary Medical AI provider."""

    API_URL = "https://api.openai.com/v1/chat/completions"
    MODEL_NAME = "gpt-5-nano"

    # Cost per 1M tokens (USD): Input $0.05, Output $0.40
    COST_INPUT_PER_1M = 0.05
    COST_OUTPUT_PER_1M = 0.40

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name

    @property
    def provider_name(self) -> str:
        return f"OpenAI ({self.model_name})"

    def _get_api_key(self) -> str:
        return getattr(settings, "OPENAI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "") or os.environ.get("OPENAI_KEY", "")

    def is_available(self) -> bool:
        key = self._get_api_key()
        return len(key.strip()) > 0

    @classmethod
    def calculate_cost(cls, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculates estimated USD cost for GPT-5 Nano usage."""
        cost_in = (prompt_tokens / 1_000_000) * cls.COST_INPUT_PER_1M
        cost_out = (completion_tokens / 1_000_000) * cls.COST_OUTPUT_PER_1M
        return round(cost_in + cost_out, 6)

    def generate(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """Synchronous call to OpenAI Chat Completions API strictly using gpt-5-nano."""
        api_key = self._get_api_key()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured in settings or environment variables.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "top_p": 0.9,
            "max_completion_tokens": max_tokens
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        start_t = time.time()
        try:
            res = requests.post(self.API_URL, headers=headers, json=payload, timeout=30.0)
            
            # If max_completion_tokens unsupported on specific endpoint, fallback key to max_tokens
            if res.status_code == 400 and "max_completion_tokens" in res.text:
                payload.pop("max_completion_tokens", None)
                payload["max_tokens"] = max_tokens
                res = requests.post(self.API_URL, headers=headers, json=payload, timeout=30.0)

            # If model name not found, try fallback to gpt-4o-mini
            if res.status_code in [404, 400] and "model" in res.text:
                payload["model"] = "gpt-4o-mini"
                res = requests.post(self.API_URL, headers=headers, json=payload, timeout=30.0)

            res.raise_for_status()
            data = res.json()
            latency = round((time.time() - start_t) * 1000, 2)
            msg = data["choices"][0]["message"]
            content = msg.get("content") or msg.get("reasoning_content") or ""
            
            # Clean reasoning tags <think>...</think> and latex parens
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
            content = re.sub(r"\\\((.*?)\\\)", r"\1", content)
            
            usage = data.get("usage") or {}
            p_tokens = usage.get("prompt_tokens", len(str(messages)) // 4)
            c_tokens = usage.get("completion_tokens", len(content) // 4)
            t_tokens = usage.get("total_tokens", p_tokens + c_tokens)
            cost = self.calculate_cost(p_tokens, c_tokens)

            actual_model = data.get("model", self.model_name)
            return {
                "content": content,
                "provider": f"OpenAI ({actual_model})",
                "latency_ms": latency,
                "prompt_tokens": p_tokens,
                "completion_tokens": c_tokens,
                "tokens_used": t_tokens,
                "estimated_cost": cost,
                "is_mock": False
            }
        except Exception as e:
            raise RuntimeError(f"OpenAI gpt-5-nano API failure: {str(e)}")

    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4096
    ) -> Generator[str, None, None]:
        """Streaming SSE iterator from OpenAI Chat Completions API for gpt-5-nano."""
        api_key = self._get_api_key()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "top_p": 0.9,
            "max_completion_tokens": max_tokens,
            "stream": True
        }

        try:
            res = requests.post(self.API_URL, headers=headers, json=payload, stream=True, timeout=12.0)
            if res.status_code == 400 and "max_completion_tokens" in res.text:
                payload.pop("max_completion_tokens", None)
                payload["max_tokens"] = max_tokens
                res = requests.post(self.API_URL, headers=headers, json=payload, stream=True, timeout=12.0)

            if res.status_code in [404, 400] and "model" in res.text:
                payload["model"] = "gpt-4o-mini"
                res = requests.post(self.API_URL, headers=headers, json=payload, stream=True, timeout=12.0)

            res.raise_for_status()
            for line in res.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    if decoded.startswith("data: "):
                        raw_data = decoded[6:]
                        if raw_data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(raw_data)
                            delta = chunk["choices"][0]["delta"]
                            if "content" in delta and delta["content"]:
                                yield delta["content"]
                        except Exception:
                            continue
        except Exception as e:
            raise RuntimeError(f"OpenAI Stream failure: {str(e)}")
