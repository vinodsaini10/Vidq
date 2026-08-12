import logging
from typing import Dict, Any, Optional, List
from app.services.ai.base import BaseAIProvider
from app.services.ai.providers.gemini_provider import GeminiProvider
from app.services.ai.providers.openai_provider import OpenAIProvider
from app.services.ai.providers.ollama_provider import OllamaProvider
from app.services.ai.providers.openai_compatible_provider import OpenAICompatibleProvider
from app.services.ai.providers.mock_provider import MockAIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, BaseAIProvider] = {}
        self._register_default_providers()

    def _register_default_providers(self):
        # Always register Gemini & Mock
        self._providers["GEMINI"] = GeminiProvider()
        self._providers["MOCK"] = MockAIProvider()

        # OpenAI if key available or lazily loaded
        if getattr(settings, "OPENAI_API_KEY", None):
            self._providers["OPENAI"] = OpenAIProvider()

        # Ollama if base URL configured
        ollama_url = getattr(settings, "OLLAMA_BASE_URL", None)
        if ollama_url:
            self._providers["OLLAMA"] = OllamaProvider(base_url=ollama_url)

    def register_provider(self, name: str, provider: BaseAIProvider):
        self._providers[name.upper()] = provider

    def get_provider(self, name: str) -> BaseAIProvider:
        provider_key = name.upper()
        if provider_key in self._providers:
            return self._providers[provider_key]
        
        # Fallback to Mock if provider not initialized or missing key
        logger.warning(f"Provider '{name}' requested but not found/configured. Falling back to MOCK provider.")
        return self._providers.get("MOCK", MockAIProvider())

    def list_providers(self) -> List[str]:
        return list(self._providers.keys())


class ModelRegistry:
    """Configurable Registry of AI Models with Pricing, Context Limits, and Capabilities."""

    DEFAULT_MODELS: Dict[str, Dict[str, Any]] = {
        "gemini-3.6-flash": {
            "provider": "GEMINI",
            "display_name": "Gemini 3.6 Flash",
            "context_window": 1048576,
            "input_price_per_1k": 0.00015,
            "output_price_per_1k": 0.00060,
            "max_tokens": 8192,
            "temperature": 0.7,
            "capabilities": {"vision": True, "streaming": True, "embedding": True, "fast": True},
            "is_active": True,
            "is_default": True,
        },
        "gemini-3.1-pro-preview": {
            "provider": "GEMINI",
            "display_name": "Gemini 3.1 Pro",
            "context_window": 2097152,
            "input_price_per_1k": 0.00125,
            "output_price_per_1k": 0.00500,
            "max_tokens": 8192,
            "temperature": 0.7,
            "capabilities": {"vision": True, "streaming": True, "embedding": True, "reasoning": True},
            "is_active": True,
            "is_default": False,
        },
        "gpt-4o-mini": {
            "provider": "OPENAI",
            "display_name": "GPT-4o Mini",
            "context_window": 128000,
            "input_price_per_1k": 0.00015,
            "output_price_per_1k": 0.00060,
            "max_tokens": 4096,
            "temperature": 0.7,
            "capabilities": {"vision": True, "streaming": True, "embedding": False, "fast": True},
            "is_active": True,
            "is_default": False,
        },
        "gpt-4o": {
            "provider": "OPENAI",
            "display_name": "GPT-4o",
            "context_window": 128000,
            "input_price_per_1k": 0.00250,
            "output_price_per_1k": 0.01000,
            "max_tokens": 4096,
            "temperature": 0.7,
            "capabilities": {"vision": True, "streaming": True, "embedding": False, "reasoning": True},
            "is_active": True,
            "is_default": False,
        },
        "llama3": {
            "provider": "OLLAMA",
            "display_name": "Llama 3 (Local)",
            "context_window": 8192,
            "input_price_per_1k": 0.0,
            "output_price_per_1k": 0.0,
            "max_tokens": 2048,
            "temperature": 0.7,
            "capabilities": {"vision": False, "streaming": True, "embedding": False, "local": True},
            "is_active": True,
            "is_default": False,
        },
        "mock-model-v1": {
            "provider": "MOCK",
            "display_name": "Mock Test Model",
            "context_window": 32000,
            "input_price_per_1k": 0.0,
            "output_price_per_1k": 0.0,
            "max_tokens": 2048,
            "temperature": 0.7,
            "capabilities": {"vision": True, "streaming": True, "mock": True},
            "is_active": True,
            "is_default": False,
        }
    }

    def __init__(self):
        self._models = dict(self.DEFAULT_MODELS)

    def get_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        return self._models.get(model_name)

    def get_default_model(self) -> str:
        for name, info in self._models.items():
            if info.get("is_default"):
                return name
        return "gemini-3.6-flash"

    def list_models(self) -> List[Dict[str, Any]]:
        result = []
        for name, info in self._models.items():
            result.append({"model_name": name, **info})
        return result

    def register_or_update_model(self, model_name: str, config: Dict[str, Any]):
        self._models[model_name] = config


provider_registry = ProviderRegistry()
model_registry = ModelRegistry()
