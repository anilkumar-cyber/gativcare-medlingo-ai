"""Insurance AI Agent -- coverage/claims/pre-auth questions, split out of Patient Concierge
because insurance answers must be sourced from the patient's actual policy data (via the
insurance module/Knowledge Agent retrieval), never inferred or guessed."""

from app.ai.agents import Agent, AgentResponse

SYSTEM_PROMPT = """You answer insurance coverage, claims, and pre-authorization questions using
only the patient's actual policy data and retrieved insurer rules provided to you. If the
provided data doesn't cover the question, say so explicitly and route to the Insurance Executive
role rather than guessing at coverage."""


class InsuranceAgent(Agent):
    name = "insurance"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    async def handle(self, request: dict) -> AgentResponse:
        policy_data = request.get("journey_data", {}).get("insurance", {})
        if not policy_data and not request.get("knowledge"):
            return AgentResponse(
                agent_name=self.name,
                content="No insurance policy or rules data is available to answer this — "
                "routing to an Insurance Executive.",
                confidence=0.2,
                flags=["insufficient_data", "needs_human_review"],
            )
        prompt = self._build_prompt(request, policy_data)
        completion = await self.llm.complete(prompt, context=request)
        return AgentResponse(agent_name=self.name, content=completion)

    def _build_prompt(self, request: dict, policy_data: dict) -> str:
        return (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"Patient policy data: {policy_data}\n"
            f"Retrieved insurer rules: {request.get('knowledge', [])}\n\n"
            f"Question:\n\"\"\"{request.get('text', '')}\"\"\"\n\n"
            "Answer using only the data above."
        )
