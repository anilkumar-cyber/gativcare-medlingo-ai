"""Emergency AI Agent -- owns the emergency RESPONSE workflow once SafetyAgent.precheck()
detects urgent content. Safety detects; this agent acts: prioritizes low-latency interpretation,
notifies clinician/emergency workflow, and never delays communication waiting on anything else.
It explicitly does not replace established emergency protocols -- it assists communication
around them. See docs/AI_ARCHITECTURE.md #emergency-mode."""

from app.ai.agents import Agent, AgentResponse
from app.ai.agents.interpreter_agent import MedicalInterpreterAgent

EMERGENCY_DISCLAIMER = (
    "This is AI-assisted communication support during a possible emergency. "
    "It does not replace calling emergency services or established hospital emergency protocols."
)


class EmergencyAgent(Agent):
    name = "emergency"
    SYSTEM_PROMPT = "You prioritize fast, clear, low-latency medical interpretation during a flagged emergency."

    def __init__(self, llm_provider):
        super().__init__(llm_provider)
        self.interpreter = MedicalInterpreterAgent(llm_provider)

    async def handle(self, request: dict) -> AgentResponse:
        # Reuses the Interpreter agent's logic directly -- an emergency doesn't need a different
        # interpretation style, it needs the same interpretation with notification/priority
        # side-effects, which the orchestrator handles via _dispatch_emergency_notification().
        response = await self.interpreter.handle(request)
        response.content = f"{response.content}\n\n{EMERGENCY_DISCLAIMER}"
        response.flags.append("emergency_flagged")
        response.agent_name = self.name
        return response
