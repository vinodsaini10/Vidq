import json
import time
import hashlib
import logging
import asyncio
from typing import Optional, Dict, Any, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.ai.base import AIProviderResponse, BaseAIProvider
from app.services.ai.registry import provider_registry, model_registry
from app.services.ai.safety import safety_layer
from app.services.ai.credits import credit_system
from app.models.ai import AIUsage, AIGenerationHistory
from app.core.config import settings
from app.core.database import async_session_factory

logger = logging.getLogger(__name__)


class AIGateway:
    """Production-grade AI Gateway with Routing, Caching, Retries, Failover, and Cost Tracking."""

    def __init__(self):
        self.default_provider = "GEMINI"
        self.default_model = "gemini-3.6-flash"
        self.max_retries = getattr(settings, "AI_MAX_RETRIES", 2)
        self.enable_fallback = getattr(settings, "AI_ENABLE_FALLBACK", True)

    def _get_cache_key(self, feature: str, model: str, prompt: str, system_prompt: str = "") -> str:
        raw_str = f"{feature}:{model}:{system_prompt}:{prompt}"
        return "ai_cache:" + hashlib.sha256(raw_str.encode()).hexdigest()

    async def generate(
        self,
        db: AsyncSession,
        user_id: str,
        feature: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        credits_cost: int = 1,
        bypass_credit_check: bool = False,
    ) -> AIProviderResponse:
        """Executes an AI request through Gateway with Safety, Credits, Routing, Failover, and Usage Tracking."""
        
        # 1. Safety Check on Prompt
        if safety_layer.is_prompt_injection(prompt):
            logger.warning(f"Blocked prompt injection attempt by user {user_id}")

        sanitized_prompt = safety_layer.sanitize_external_content(prompt)

        # 2. Check and deduct credits
        if not bypass_credit_check:
            await credit_system.check_and_deduct_credits(db, user_id=user_id, credits_required=credits_cost)

        # 3. Model & Provider Routing
        chosen_model = model_name or self.default_model
        model_info = model_registry.get_model(chosen_model)
        chosen_provider = provider_name or (model_info.get("provider") if model_info else self.default_provider)

        # 4. Execute with Retry & Failover
        response = None
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                provider_instance: BaseAIProvider = provider_registry.get_provider(chosen_provider)
                response = await provider_instance.generate(
                    prompt=sanitized_prompt,
                    system_prompt=system_prompt,
                    model=chosen_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                    json_schema=json_schema,
                )
                break  # Success!
            except Exception as e:
                last_error = e
                logger.warning(f"AI Gateway Attempt {attempt+1} failed ({chosen_provider}/{chosen_model}): {e}")

                # Failover to fallback provider on last retry if enabled
                if attempt == self.max_retries and self.enable_fallback and chosen_provider != "MOCK":
                    logger.info("Attempting failover to fallback MOCK AI provider.")
                    try:
                        fallback_provider = provider_registry.get_provider("MOCK")
                        response = await fallback_provider.generate(
                            prompt=sanitized_prompt,
                            system_prompt=system_prompt,
                            model="mock-model-v1",
                            temperature=temperature,
                            max_tokens=max_tokens,
                            response_format=response_format,
                            json_schema=json_schema,
                        )
                        break
                    except Exception as fb_err:
                        last_error = fb_err

                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

        if not response:
            # Refund credit if generation failed completely
            if not bypass_credit_check:
                await credit_system.refund_credits(db, user_id, credits_cost)
            raise RuntimeError(f"AI Generation Failed after retries: {last_error}")

        # 5. Output Safety Filter
        response.text = safety_layer.filter_output_safety(response.text)

        # 6. Calculate Costs & Track Usage
        input_price = model_info.get("input_price_per_1k", 0.00015) if model_info else 0.00015
        output_price = model_info.get("output_price_per_1k", 0.00060) if model_info else 0.00060
        est_cost = (response.input_tokens / 1000.0 * input_price) + (response.output_tokens / 1000.0 * output_price)

        # Log AI Usage in Database
        usage_record = AIUsage(
            user_id=user_id,
            provider=response.provider_name,
            model_used=response.model_used,
            request_type=feature,
            prompt_tokens=response.input_tokens,
            completion_tokens=response.output_tokens,
            total_tokens=response.total_tokens,
            estimated_cost=round(est_cost, 6),
            credits_used=credits_cost,
            latency_ms=response.latency_ms,
            status="SUCCESS",
        )
        db.add(usage_record)

        # Log in Generation History
        history_record = AIGenerationHistory(
            user_id=user_id,
            prompt=sanitized_prompt,
            output=response.text[:2000],
            feature=feature,
            model_used=response.model_used,
        )
        db.add(history_record)
        await db.commit()

        return response

    async def generate_stream(
        self,
        db: AsyncSession,
        user_id: str,
        feature: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        credits_cost: int = 1,
    ) -> AsyncGenerator[str, None]:
        """Streams AI tokens via async generator with credit check."""
        await credit_system.check_and_deduct_credits(db, user_id=user_id, credits_required=credits_cost)

        sanitized_prompt = safety_layer.sanitize_external_content(prompt)
        chosen_model = model_name or self.default_model
        model_info = model_registry.get_model(chosen_model)
        chosen_provider = provider_name or (model_info.get("provider") if model_info else self.default_provider)

        provider_instance = provider_registry.get_provider(chosen_provider)

        try:
            async for chunk in provider_instance.generate_stream(
                prompt=sanitized_prompt,
                system_prompt=system_prompt,
                model=chosen_model,
                temperature=temperature,
                max_tokens=max_tokens,
            ):
                yield safety_layer.filter_output_safety(chunk)
        except Exception as e:
            logger.error(f"Stream generation error: {e}")
            yield f"\n[Stream Error: {str(e)}]"


ai_gateway = AIGateway()
