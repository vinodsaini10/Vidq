import time
import json
import logging
from typing import AsyncGenerator, Optional, Dict, Any
import httpx
from app.services.ai.base import BaseAIProvider, AIProviderResponse

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider(BaseAIProvider):
    """Supports Groq, Together AI, Anyscale, DeepSeek, vLLM, LMStudio, etc."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, provider_label: str = "OPENAI_COMPATIBLE"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "none"
        self._provider_label = provider_label

    @property
    def provider_name(self) -> str:
        return self._provider_label

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
        model_name = model or "default-model"
        start_time = time.time()

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
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        endpoint = f"{self.base_url}/chat/completions" if not self.base_url.endswith("/chat/completions") else self.base_url

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(endpoint, json=payload, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"OpenAI-Compatible API Error {resp.status_code}: {resp.text}")

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
        model_name = model or "default-model"

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
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        endpoint = f"{self.base_url}/chat/completions" if not self.base_url.endswith("/chat/completions") else self.base_url

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", endpoint, json=payload, headers=headers) as resp:
                if resp.status_code != 200:
                    err_body = await resp.aread()
                    raise RuntimeError(f"OpenAI-Compatible Stream Error {resp.status_code}: {err_body.decode()}")

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
