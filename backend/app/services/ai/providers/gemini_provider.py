import time
import logging
from typing import AsyncGenerator, Optional, Dict, Any
from google import genai
from app.services.ai.base import BaseAIProvider, AIProviderResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._client = None
        if self._api_key:
            try:
                self._client = genai.Client(
                    api_key=self._api_key,
                    http_options={"headers": {"User-Agent": "aistudio-build"}}
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Client: {e}")

    @property
    def provider_name(self) -> str:
        return "GEMINI"

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
        model_name = model or settings.AI_DEFAULT_MODEL or "gemini-3.6-flash"
        start_time = time.time()

        if not self._client:
            raise RuntimeError("Gemini API key is missing or client not initialized.")

        config: Dict[str, Any] = {
            "temperature": temperature,
        }
        if system_prompt:
            config["system_instruction"] = system_prompt

        if response_format == "json":
            config["response_mime_type"] = "application/json"
            if json_schema:
                config["response_schema"] = json_schema

        try:
            response = self._client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )

            latency_ms = int((time.time() - start_time) * 1000)
            result_text = response.text or ""
            input_tokens = self.count_tokens((system_prompt or "") + prompt)
            output_tokens = self.count_tokens(result_text)

            return AIProviderResponse(
                text=result_text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                raw_response=response,
                model_used=model_name,
                provider_name=self.provider_name,
                latency_ms=latency_ms,
            )
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise e

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        model_name = model or settings.AI_DEFAULT_MODEL or "gemini-3.6-flash"

        if not self._client:
            raise RuntimeError("Gemini API key missing.")

        config: Dict[str, Any] = {"temperature": temperature}
        if system_prompt:
            config["system_instruction"] = system_prompt

        response_stream = self._client.models.generate_content_stream(
            model=model_name,
            contents=prompt,
            config=config,
        )

        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
