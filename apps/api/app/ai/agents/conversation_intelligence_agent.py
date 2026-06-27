"""Conversation Intelligence Agent -- owns multi-turn continuity, not single-utterance
interpretation (that's the Interpreter agent). Produces conversation summaries and resolves
references back to earlier turns ("the surgery you mentioned") using ContextEngine's turn
history, so the patient is never asked to repeat themselves. See docs/AI_ARCHITECTURE.md."""

from app.ai.agents import Agent, AgentResponse

SYSTEM_PROMPT = """You track the arc of a multi-turn medical conversation: what's been said,
what's still open, what the current objective is (e.g. collecting symptom history, explaining a
treatment plan, closing out a follow-up). You resolve references to earlier turns instead of
asking the speaker to repeat themselves. You produce conversation summaries and 'what's next'
guidance, not new clinical content -- clinical content comes from the Clinical Intelligence
agent."""


class ConversationIntelligenceAgent(Agent):
    name = "conversation_intelligence"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    async def handle(self, request: dict) -> AgentResponse:
        prompt = self._build_prompt(request)
        completion = await self.llm.complete(prompt, context=request)
        return AgentResponse(agent_name=self.name, content=completion)

    def _build_prompt(self, request: dict) -> str:
        return (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"Turn history: {request.get('conversation_history', [])}\n"
            f"Current objective (if known): {request.get('medical_context', {}).get('stage')}\n\n"
            f"Latest input:\n\"\"\"{request.get('text', '')}\"\"\"\n\n"
            "Produce the continuity-aware response: resolve any references to earlier turns, "
            "note what remains open for this conversation."
        )
