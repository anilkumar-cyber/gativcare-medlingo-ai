"""Knowledge Agent — retrieval-augmented answers over medical guidelines, hospital/doctor info,
drug data, medical-tourism/insurance/visa rules, and FAQs. Thin by design: it composes retrieved
passages into an answer, it doesn't reason beyond what was retrieved (that's Clinical
Intelligence's job for clinical content)."""

from app.ai.agents import Agent, AgentResponse

SYSTEM_PROMPT = """You answer questions strictly from the retrieved passages you are given. If the
retrieved passages don't contain the answer, say so explicitly rather than guessing. Always cite
which retrieved item each part of your answer came from."""


class KnowledgeAgent(Agent):
    name = "knowledge"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    async def handle(self, request: dict) -> AgentResponse:
        passages = request.get("knowledge", [])
        if not passages:
            return AgentResponse(
                agent_name=self.name,
                content="No relevant information was found in the knowledge base for this question.",
                confidence=0.0,
                flags=["no_retrieval_hits"],
            )
        prompt = self._build_prompt(request, passages)
        completion = await self.llm.complete(prompt, context=request)
        return AgentResponse(agent_name=self.name, content=completion)

    def _build_prompt(self, request: dict, passages: list) -> str:
        numbered = "\n".join(f"[{i+1}] {p}" for i, p in enumerate(passages))
        return (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"Retrieved passages:\n{numbered}\n\n"
            f"Question:\n\"\"\"{request.get('text', '')}\"\"\"\n\n"
            "Answer using only the passages above, with citation numbers."
        )
