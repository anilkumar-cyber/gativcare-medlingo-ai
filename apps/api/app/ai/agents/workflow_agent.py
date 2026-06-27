"""Workflow AI Agent -- answers 'what stage is this case at / what happens next' and can trigger
a stage advance via WorkflowEngine. It phrases workflow state in natural language; it does not
own the state machine itself (app.core.workflow_engine does)."""

from app.ai.agents import Agent, AgentResponse
from app.core.workflow_engine import WorkflowEngine

SYSTEM_PROMPT = """You explain where a patient's case stands in their treatment journey and what
the next step is, in plain language. You never skip a stage yourself -- you report on the
workflow engine's state and, if asked to advance, you confirm the next stage before any change is
made."""


class WorkflowAgent(Agent):
    name = "workflow"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    def __init__(self, llm_provider, workflow_engine: WorkflowEngine | None = None):
        super().__init__(llm_provider)
        self.workflow_engine = workflow_engine or WorkflowEngine()

    async def handle(self, request: dict) -> AgentResponse:
        current_stage = request.get("medical_context", {}).get("stage")
        next_stage = self.workflow_engine.next_stage(current_stage) if current_stage else None

        prompt = (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"Current stage: {current_stage}\nNext stage: {next_stage}\n\n"
            f"Patient/staff question:\n\"\"\"{request.get('text', '')}\"\"\"\n\n"
            "Explain the current stage and next step in plain language."
        )
        completion = await self.llm.complete(prompt, context=request)
        return AgentResponse(
            agent_name=self.name, content=completion, metadata={"current_stage": current_stage, "next_stage": next_stage}
        )
