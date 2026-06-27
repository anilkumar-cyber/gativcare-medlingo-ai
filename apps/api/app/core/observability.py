"""AI quality observability. One event stream, consumed by the analytics module's
'AI Accuracy Metrics' / 'Translation Confidence' dashboards directly -- there's no separate
AI-metrics pipeline. See docs/AI_ARCHITECTURE.md #observability."""

import time
from contextlib import asynccontextmanager
from dataclasses import dataclass


@dataclass
class AgentCallEvent:
    agent_name: str
    org_id: str
    latency_ms: float
    confidence: float
    flags: list[str]
    provider_used: str


async def emit_agent_call_event(event: AgentCallEvent) -> None:
    # Phase 3: publish to the same event stream analytics.service consumes (Redis pub/sub or a
    # queue -- see docs/WORKFLOWS.md #why-workflows-are-event-driven).
    raise NotImplementedError


@asynccontextmanager
async def measure_agent_call(*, agent_name: str, org_id: str, provider_used: str):
    """Wrap an agent.handle() call: `async with measure_agent_call(...) as m: response = await agent.handle(payload); m.response = response`"""

    class _Measurement:
        response = None

    measurement = _Measurement()
    start = time.monotonic()
    try:
        yield measurement
    finally:
        if measurement.response is not None:
            await emit_agent_call_event(AgentCallEvent(
                agent_name=agent_name,
                org_id=org_id,
                latency_ms=(time.monotonic() - start) * 1000,
                confidence=measurement.response.confidence,
                flags=measurement.response.flags,
                provider_used=provider_used,
            ))
