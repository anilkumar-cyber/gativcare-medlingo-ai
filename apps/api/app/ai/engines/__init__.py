"""Engine base interface. Every file in this package implements one pipeline stage
from docs/ARCHITECTURE.md #1. Engines never call each other directly — only the
orchestrator composes them."""

from abc import ABC, abstractmethod
from typing import Any


class Engine(ABC):
    name: str

    @abstractmethod
    async def run(self, payload: dict[str, Any]) -> dict[str, Any]: ...
