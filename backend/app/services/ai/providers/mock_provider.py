import time
import json
import asyncio
from typing import AsyncGenerator, Optional, Dict, Any
from app.services.ai.base import BaseAIProvider, AIProviderResponse


class MockAIProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "MOCK"

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
        start_time = time.time()
        topic = prompt[:40] if len(prompt) > 40 else prompt

        if response_format == "json":
            result_text = json.dumps({
                "titles": [
                    {"title": f"I Tried {topic} For 30 Days (Viral Results)", "ctr_score": "96%", "reason": "Curiosity & challenge hook"},
                    {"title": f"Why 99% Fail At {topic} (Do This Instead)", "ctr_score": "94%", "reason": "Negative pattern interrupt"}
                ],
                "seo_score": 92,
                "summary": f"Mock AI Generated analysis for '{topic}'."
            })
        else:
            result_text = f"Mock AI generated response for topic: '{topic}' with 90%+ predicted engagement."

        input_tokens = self.count_tokens((system_prompt or "") + prompt)
        output_tokens = self.count_tokens(result_text)

        return AIProviderResponse(
            text=result_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            raw_response={"mock": True},
            model_used=model or "mock-model-v1",
            provider_name=self.provider_name,
            latency_ms=int((time.time() - start_time) * 1000)
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
        chunks = [
            " [VidPulse AI] ", "Analysis ", "complete ", "for: ", f"'{prompt[:30]}'. ",
            "\n\n1. High CTR Strategy: Focus on strong visual contrast.\n2. Key Retention Driver: Hook within first 5 seconds."
        ]
        for c in chunks:
            yield c
            await asyncio.sleep(0.02)
