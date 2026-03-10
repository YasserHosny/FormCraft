from abc import ABC, abstractmethod

from app.schemas.ai import SuggestionRequest


class LLMProvider(ABC):
    """Abstract LLM provider interface. Implement for each provider (Bedrock, OpenAI, etc.)."""

    @abstractmethod
    async def classify_field(self, request: SuggestionRequest) -> dict:
        """Send label + context to LLM, return raw JSON dict."""
        ...
