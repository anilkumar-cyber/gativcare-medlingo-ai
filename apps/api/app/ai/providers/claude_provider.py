"""Default LLMProvider implementation. Only file in app/ai allowed to import the anthropic SDK."""

from app.ai.providers.base import LLMProvider


class ClaudeProvider(LLMProvider):
    async def complete(self, prompt: str, *, context: dict) -> str:
        raise NotImplementedError
