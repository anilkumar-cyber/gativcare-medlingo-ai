"""Tool interface. Tools are modular, named, single-purpose callables an agent or the
orchestrator can invoke (function-calling) -- translation, search, scheduling, document
processing, verification, notification, etc. A tool wraps an existing module service or
provider; it never contains business logic of its own. See docs/AI_ARCHITECTURE.md #ai-tools."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    tool_name: str
    output: Any
    error: str | None = None


class Tool(ABC):
    name: str
    description: str

    @abstractmethod
    async def run(self, **kwargs) -> ToolResult: ...
