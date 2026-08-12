import time
import json
import logging
from typing import AsyncGenerator, Optional, Dict, Any
import httpx
from app.services.ai.base import BaseAIProvider, AIProviderResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or getattr(settings, "OPENAI_API_KEY", "")
        self.base_url = "https://api.openai.com/v1"

    @property
    def provider_name(self) -> str:
        return "OPENAI"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AIProviderResponse:
        model_name = model or "gpt-4o-mini"
        start_time = time.time()

        if not self._api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"OpenAI API Error {resp.status_code}: {resp.text}")

            data = resp.json()
            latency_ms = int((time.time() - start_time) * 1000)
            result_text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", self.count_tokens(prompt))
            output_tokens = usage.get("completion_tokens", self.count_tokens(result_text))

            return AIProviderResponse(
                text=result_text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                raw_response=data,
                model_used=model_name,
                provider_name=self.provider_name,
                latency_ms=latency_ms,
            )

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        model_name = model or "gpt-4o-mini"

        if not self._api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            ) as resp:
                if resp.status_code != 200:
                    err_body = await resp.aread()
                    raise RuntimeError(f"OpenAI Stream Error {resp.status_code}: {err_body.decode()}")

                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and not line.startswith("data: [DONE]"):
                        chunk_str = line[6:]
                        try:
                            chunk_json = json.loads(chunk_str)
                            delta = chunk_json["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            continue
