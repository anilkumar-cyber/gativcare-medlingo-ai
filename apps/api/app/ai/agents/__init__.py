"""Agent base. Agents are task-level specialists composed of one or more engines plus a
persona system prompt. Agents never call each other directly — only the orchestrator
dispatches between them. See docs/AI_ARCHITECTURE.md."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentResponse:
    agent_name: str
    content: str
    confidence: float = 1.0
    flags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class Agent(ABC):
    name: str
    SYSTEM_PROMPT: str = ""

    def __init__(self, llm_provider):
        self.llm = llm_provider

    @abstractmethod
    async def handle(self, request: dict[str, Any]) -> AgentResponse: ...


def merge_responses(responses: list[AgentResponse]) -> AgentResponse:
    """Combines fan-out results from multiple agents into one. Used when an intent maps to more
    than one agent (e.g. "medical_report" -> documentation + clinical_reasoning). Confidence is
    the minimum, not the average -- a merged answer is only as trustworthy as its weakest part."""
    if len(responses) == 1:
        return responses[0]

    sections = [f"[{r.agent_name}]\n{r.content}" for r in responses if r.content]
    merged_flags = sorted({flag for r in responses for flag in r.flags})
    merged_metadata: dict[str, Any] = {}
    for r in responses:
        merged_metadata.update(r.metadata)

    return AgentResponse(
        agent_name="+".join(r.agent_name for r in responses),
        content="\n\n".join(sections),
        confidence=min((r.confidence for r in responses), default=1.0),
        flags=merged_flags,
        metadata=merged_metadata,
    )
