"""Patient Concierge Agent — healthcare concierge + travel assistant for the non-clinical parts
of the journey (appointments, hospital navigation, travel, hotel, visa, insurance guidance,
medication reminders, recovery guidance, FAQs). Bridges into the journey/coordination modules
rather than reasoning about them itself — it composes answers, it doesn't own travel/insurance
business logic."""

from app.ai.agents import Agent, AgentResponse

SYSTEM_PROMPT = """You are a warm, efficient healthcare concierge and international patient
coordinator. You help patients navigate appointments, hospital logistics, travel, hotels, visas,
insurance questions, medication reminders, and recovery guidance. You are not a clinician: for any
question about symptoms, diagnosis, or treatment, you redirect to the Clinical Intelligence agent
or the patient's care team rather than answering yourself."""


class PatientConciergeAgent(Agent):
    name = "patient_concierge"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    async def handle(self, request: dict) -> AgentResponse:
        prompt = self._build_prompt(request)
        completion = await self.llm.complete(prompt, context=request)
        return AgentResponse(agent_name=self.name, content=completion)

    def _build_prompt(self, request: dict) -> str:
        return (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"Case stage: {request.get('medical_context', {}).get('stage')}\n"
            f"Relevant journey data (travel/visa/insurance, if any): {request.get('journey_data', {})}\n"
            f"Patient language/cultural preference (consent-gated): {request.get('patient_memory', {})}\n\n"
            f"Patient request:\n\"\"\"{request.get('text', '')}\"\"\"\n\n"
            "Respond directly and helpfully. If this touches a clinical question, say so and "
            "defer to the care team instead of answering it."
        )
