"""Default LLMProvider implementation. Only file in app/ai allowed to import the anthropic SDK
-- every other engine/agent goes through the LLMProvider interface in base.py instead."""

import anthropic

from app.ai.providers.base import LLMProvider
from app.core.config import settings


class AIProviderError(Exception):
    """Raised when the underlying LLM call fails (bad/missing key, rate limit, outage) --
    callers should surface this as a clean 503, not a raw stack trace."""


class ClaudeProvider(LLMProvider):
    def __init__(self) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def complete(self, prompt: str, *, context: dict) -> str:
        try:
            response = await self._client.messages.create(
                model=settings.anthropic_model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
        except anthropic.AnthropicError as exc:
            raise AIProviderError(str(exc)) from exc

        return "".join(block.text for block in response.content if block.type == "text")
