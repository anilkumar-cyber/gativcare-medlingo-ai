"""Travel Concierge Agent -- split out of the general Patient Concierge for the
travel/visa/hotel/airport-pickup slice of the journey (docs/MODULES.md travel/hotels/
airport_pickup/visa modules). Not a clinician; never answers clinical questions."""

from app.ai.agents import Agent, AgentResponse

SYSTEM_PROMPT = """You are a travel coordinator for international medical patients: flights,
visas, hotels, airport pickup, local logistics. You are not a clinician -- redirect any clinical
question to the care team or the Clinical Intelligence agent."""


class TravelConciergeAgent(Agent):
    name = "travel_concierge"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    async def handle(self, request: dict) -> AgentResponse:
        prompt = self._build_prompt(request)
        completion = await self.llm.complete(prompt, context=request)
        return AgentResponse(agent_name=self.name, content=completion)

    def _build_prompt(self, request: dict) -> str:
        return (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"Case stage: {request.get('medical_context', {}).get('stage')}\n"
            f"Travel/visa/hotel data on file: {request.get('journey_data', {}).get('travel', {})}\n\n"
            f"Request:\n\"\"\"{request.get('text', '')}\"\"\"\n\n"
            "Respond directly and helpfully."
        )
