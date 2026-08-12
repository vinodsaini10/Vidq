import re
import logging
from typing import str

logger = logging.getLogger(__name__)

# Patterns for prompt injection defense
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|system)\s+(instructions|prompts|rules)",
    r"disregard\s+(all\s+)?(previous|above|system)\s+(instructions|prompts|rules)",
    r"you\s+are\s+now\s+(a|an)\s+unrestricted",
    r"jailbreak",
    r"override\s+(system|safety)\s+(prompt|rules|filters)",
    r"reveal\s+(system\s+prompt|instructions|secret|api_key|database)",
    r"act\s+as\s+DAN",
    r"system:\s*\"?you\s+are",
]

# Patterns for sensitive data leakage prevention in outputs
SENSITIVE_DATA_PATTERNS = [
    (r"AIzaSy[A-Za-z0-9_-]{33}", "[REDACTED_API_KEY]"),
    (r"sk-[A-Za-z0-9_-]{32,}", "[REDACTED_OPENAI_KEY]"),
    (r"postgresql://[^\s]+", "[REDACTED_DB_URL]"),
    (r"redis://[^\s]+", "[REDACTED_REDIS_URL]"),
    (r"bearer\s+[A-Za-z0-9_.-]{20,}", "[REDACTED_TOKEN]"),
]


class AISafetyLayer:
    """Security and sanitization layer for AI inputs and outputs."""

    @staticmethod
    def sanitize_external_content(content: str) -> str:
        """Sanitizes untrusted YouTube data or user input against prompt injection."""
        if not content:
            return ""

        sanitized = content
        for pattern in PROMPT_INJECTION_PATTERNS:
            sanitized = re.sub(pattern, "[FILTERED_INSTRUCTION_ATTEMPT]", sanitized, flags=re.IGNORECASE)

        # Enforce bounds on raw untrusted external strings
        if len(sanitized) > 10000:
            sanitized = sanitized[:10000] + "... [TRUNCATED]"

        return sanitized

    @staticmethod
    def filter_output_safety(text: str) -> str:
        """Ensures generated response does not leak credentials or sensitive secrets."""
        if not text:
            return ""

        filtered = text
        for pattern, replacement in SENSITIVE_DATA_PATTERNS:
            filtered = re.sub(pattern, replacement, filtered)

        return filtered

    @staticmethod
    def is_prompt_injection(user_input: str) -> bool:
        """Checks if input matches high-confidence prompt injection attacks."""
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, user_input, flags=re.IGNORECASE):
                logger.warning(f"Prompt injection pattern detected: '{pattern}'")
                return True
        return False


safety_layer = AISafetyLayer()
