"""Scanned-document text extraction interface. Native PDF/Word text extraction skips this and
goes straight to summarization -- see docs/AI_ARCHITECTURE.md #document-intelligence."""

from abc import ABC, abstractmethod


class OCRProvider(ABC):
    @abstractmethod
    async def extract(self, file_bytes: bytes, *, mime_type: str) -> str: ...
