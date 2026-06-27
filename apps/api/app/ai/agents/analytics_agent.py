"""Analytics AI Agent -- answers natural-language questions about an org's own metrics
(docs/ARCHITECTURE.md Analytics module) by composing already-computed aggregates. It does not
compute aggregates itself -- that's the analytics module's job; this agent is a phrasing layer
over numbers the module already produced, same retrieval-then-compose shape as Knowledge Agent."""

from app.ai.agents import Agent, AgentResponse

SYSTEM_PROMPT = """You answer questions about an organization's own operational metrics
(patients served, languages used, response times, satisfaction, AI accuracy) using only the
pre-computed figures you are given. You never estimate or fabricate a number that wasn't
provided."""


class AnalyticsAgent(Agent):
    name = "analytics"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    async def handle(self, request: dict) -> AgentResponse:
        metrics = request.get("metrics", {})
        if not metrics:
            return AgentResponse(
                agent_name=self.name,
                content="No metrics were available for this query.",
                confidence=0.0,
                flags=["no_metrics_data"],
            )
        prompt = (
            f"{self.SYSTEM_PROMPT}\n\nMetrics: {metrics}\n\n"
            f"Question:\n\"\"\"{request.get('text', '')}\"\"\"\n\nAnswer using only these figures."
        )
        completion = await self.llm.complete(prompt, context=request)
        return AgentResponse(agent_name=self.name, content=completion)
