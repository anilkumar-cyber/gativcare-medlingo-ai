"""Medical Documentation Agent — drafts clinical paperwork (SOAP notes, visit/discharge/
consultation summaries, prescription explanations, translated reports). Every output is a draft
requiring clinician sign-off; this agent never writes directly into the medical record."""

from app.ai.agents import Agent, AgentResponse

SYSTEM_PROMPT = """You draft clinical documentation from conversation transcripts and case
context: SOAP notes, visit summaries, discharge summaries, follow-up instructions, consultation
summaries, and plain-language prescription explanations. You write in standard clinical
documentation style for clinician-facing documents, and plain language for patient-facing copies.
You only include what was actually said or recorded — never infer findings that weren't stated.
Every draft must be reviewed and signed by the treating clinician before it becomes part of the
official record."""

DRAFT_DISCLAIMER = "DRAFT — requires clinician review and sign-off before becoming part of the medical record."


class MedicalDocumentationAgent(Agent):
    name = "medical_documentation"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    async def handle(self, request: dict) -> AgentResponse:
        prompt = self._build_prompt(request)
        completion = await self.llm.complete(prompt, context=request)
        content = f"{completion}\n\n{DRAFT_DISCLAIMER}"
        return AgentResponse(agent_name=self.name, content=content, metadata={"status": "draft"})

    def _build_prompt(self, request: dict) -> str:
        doc_type = request.get("document_type", "visit_summary")
        return (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"Document type requested: {doc_type}\n"
            f"Conversation transcript: {request.get('transcript', [])}\n"
            f"Case context: {request.get('medical_context', {})}\n\n"
            f"Produce the {doc_type} now, using only information present in the transcript/context."
        )
