"""AI quality observability. One event stream, consumed by the analytics module's
'AI Accuracy Metrics' / 'Translation Confidence' dashboards directly -- there's no separate
AI-metrics pipeline. See docs/AI_ARCHITECTURE.md #observability."""

import logging
import time
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass

from app.core.events import AI_AGENT_CALL_RECORDED, Event, event_bus

logger = logging.getLogger("ai.observability")


@dataclass
class AgentCallEvent:
    agent_name: str
    org_id: str
    latency_ms: float
    confidence: float
    flags: list[str]
    provider_used: str


async def emit_agent_call_event(event: AgentCallEvent) -> None:
    # Real publish onto the same EventBus everything else uses (app/core/events.py) -- the
    # analytics module subscribes to AGENT_CALL_RECORDED once it exists (Phase 3 continued);
    # until then this is a no-op fan-out, not a crash, and the log line keeps it observable now.
    logger.info("agent call", extra=asdict(event))
    await event_bus.publish(Event(type=AI_AGENT_CALL_RECORDED, org_id=event.org_id, payload=asdict(event)))


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
