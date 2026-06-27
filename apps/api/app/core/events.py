"""Event bus. Modules/agents publish events; the Workflow/Automation agents and other modules
subscribe -- nobody calls another module directly to react to something that happened elsewhere.
This is what keeps 35+ modules from hardcoding cross-references. See docs/WORKFLOWS.md
#why-workflows-are-event-driven.

Phase 2: in-process pub/sub (good enough for tests and a single API process). Phase 3: swap
PubSub's implementation for Redis pub/sub -- subscribers don't change, only the transport does.
"""

from collections import defaultdict
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# Representative, not exhaustive -- new event types are added as new modules need them, no
# central registry edit required beyond this list for documentation purposes.
PATIENT_REGISTERED = "patient.registered"
APPOINTMENT_BOOKED = "appointment.booked"
REPORT_UPLOADED = "report.uploaded"
TRANSLATION_STARTED = "translation.started"
TRANSLATION_COMPLETED = "translation.completed"
VIDEO_CONSULTATION_STARTED = "video_consultation.started"
PRESCRIPTION_CREATED = "prescription.created"
HOSPITAL_ASSIGNED = "hospital.assigned"
TREATMENT_COMPLETED = "treatment.completed"
FOLLOW_UP_SCHEDULED = "follow_up.scheduled"
MEDICAL_CASE_STAGE_CHANGED = "medical_case.stage_changed"
AI_NEEDS_HUMAN_REVIEW = "ai.needs_human_review"
AI_EMERGENCY_DETECTED = "ai.emergency_detected"
AI_AGENT_CALL_RECORDED = "ai.agent_call_recorded"


@dataclass
class Event:
    type: str
    org_id: str
    payload: dict[str, Any]
    occurred_at: datetime = field(default_factory=datetime.utcnow)


Subscriber = Callable[[Event], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Subscriber]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Subscriber) -> None:
        self._subscribers[event_type].append(handler)

    async def publish(self, event: Event) -> None:
        for handler in self._subscribers.get(event.type, []):
            await handler(event)


event_bus = EventBus()
