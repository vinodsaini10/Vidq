import time
import json
import logging
from typing import AsyncGenerator, Optional, Dict, Any
import httpx
from app.services.ai.base import BaseAIProvider, AIProviderResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class OllamaProvider(BaseAIProvider):
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")

    @property
    def provider_name(self) -> str:
        return "OLLAMA"

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
        model_name = model or "llama3"
        start_time = time.time()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model_name,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": False,
        }

        if response_format == "json":
            payload["format"] = "json"

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Ollama API Error {resp.status_code}: {resp.text}")

            data = resp.json()
            latency_ms = int((time.time() - start_time) * 1000)
            result_text = data.get("message", {}).get("content", "")
            input_tokens = data.get("prompt_eval_count", self.count_tokens(prompt))
            output_tokens = data.get("eval_count", self.count_tokens(result_text))

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
        model_name = model or "llama3"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model_name,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as resp:
                if resp.status_code != 200:
                    err_body = await resp.aread()
                    raise RuntimeError(f"Ollama Stream Error {resp.status_code}: {err_body.decode()}")

                async for line in resp.aiter_lines():
                    if line.strip():
                        try:
                            chunk_json = json.loads(line)
                            content = chunk_json.get("message", {}).get("content", "")
                            if content:
                                yield content
                        except Exception:
                            continue
