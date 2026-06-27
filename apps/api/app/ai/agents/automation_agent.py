"""Automation AI Agent -- reacts to events with a simple rule table, no LLM call required for
the common cases (an LLM call to decide "should I send a notification" would be slower and less
predictable than a rule lookup). Subscribes to app.core.events.event_bus; this is what makes
"new module reacts to an existing event without existing modules knowing it exists" concrete.
"""

from app.ai.agents import Agent, AgentResponse
from app.core.events import (
    AI_EMERGENCY_DETECTED,
    AI_NEEDS_HUMAN_REVIEW,
    MEDICAL_CASE_STAGE_CHANGED,
    REPORT_UPLOADED,
    Event,
    event_bus,
)

# event_type -> (notification_template, recipient_role)
AUTOMATION_RULES: dict[str, tuple[str, str]] = {
    REPORT_UPLOADED: ("report_uploaded_review_needed", "patient_coordinator"),
    MEDICAL_CASE_STAGE_CHANGED: ("case_stage_changed", "patient_coordinator"),
    AI_NEEDS_HUMAN_REVIEW: ("ai_review_needed", "assigned_clinician"),
    AI_EMERGENCY_DETECTED: ("emergency_escalation", "emergency_staff"),
}


class AutomationAgent(Agent):
    name = "automation"
    SYSTEM_PROMPT = "You map events to automation actions via a fixed rule table, not inference."

    async def handle(self, request: dict) -> AgentResponse:
        event_type = request.get("event_type")
        rule = AUTOMATION_RULES.get(event_type)
        if rule is None:
            return AgentResponse(agent_name=self.name, content="no automation rule for this event", flags=["no_rule"])

        template, recipient_role = rule
        from app.modules.notifications import service as notification_service
        await notification_service.notify(
            request.get("recipient_user_id"), template=template, metadata=request.get("payload", {})
        )
        return AgentResponse(agent_name=self.name, content=f"dispatched '{template}' to {recipient_role}")

    async def on_event(self, event: Event) -> None:
        await self.handle({"event_type": event.type, "payload": event.payload, "recipient_user_id": None})


def register_default_automations(llm_provider) -> AutomationAgent:
    agent = AutomationAgent(llm_provider)
    for event_type in AUTOMATION_RULES:
        event_bus.subscribe(event_type, agent.on_event)
    return agent
