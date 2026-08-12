from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncGenerator, Dict, Any, Optional, List


@dataclass
class AIProviderResponse:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    raw_response: Optional[Any] = None
    model_used: str = ""
    provider_name: str = ""
    latency_ms: int = 0


class BaseAIProvider(ABC):
    """Abstract base interface for all AI providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the provider name e.g. 'GEMINI', 'OPENAI', 'OLLAMA'."""
        pass

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_format: Optional[str] = None,  # "json" or None
        json_schema: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AIProviderResponse:
        """Generates a complete response from the AI model."""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Streams token chunks as they are produced."""
        pass

    def count_tokens(self, text: str) -> int:
        """Estimates or calculates token length of a given text string."""
        if not text:
            return 0
        # Standard rough heuristic: ~4 characters per token
        return max(1, len(text) // 4)
