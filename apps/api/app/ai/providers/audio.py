"""DSP interface. Denoise/enhance are specialized ML problems best solved by a dedicated vendor
model, not reimplemented in-house -- same reasoning as STTProvider/TTSProvider in base.py."""

from abc import ABC, abstractmethod


class AudioProcessor(ABC):
    @abstractmethod
    async def denoise(self, audio: bytes) -> bytes: ...

    @abstractmethod
    async def enhance(self, audio: bytes) -> bytes: ...
