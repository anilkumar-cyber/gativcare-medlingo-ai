"""Provider interfaces. No engine or orchestrator code may import a vendor SDK directly —
only an implementation of one of these interfaces may. See docs/ARCHITECTURE.md #4."""

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, prompt: str, *, context: dict[str, Any]) -> str: ...


class STTProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio: bytes, *, language_hint: str | None = None) -> str: ...


class TTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, *, language: str, voice_id: str | None = None) -> bytes: ...
