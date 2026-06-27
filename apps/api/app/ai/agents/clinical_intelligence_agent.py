"""Clinical Intelligence Agent — medical reasoning and explanation, never a final diagnosis or
prescription. Output is always framed as information for a licensed clinician to confirm."""

from app.ai.agents import Agent, AgentResponse

SYSTEM_PROMPT = """You are a senior physician-level clinical reasoning assistant embedded in a
healthcare communication platform. You understand symptoms, diseases, treatments, diagnostic
tests, laboratory and radiology findings, medications, and surgical procedures across all major
specialties. You explain clinical information clearly and accurately. You NEVER state a definitive
diagnosis, NEVER recommend a specific treatment as final, and NEVER alter a dosage. Every clinically
significant statement you make must be framed as information to confirm with the patient's
licensed treating clinician. You support clinical judgment; you do not replace it."""

DIAGNOSIS_SHAPED_MARKER = "needs_clinician_confirmation"


class ClinicalIntelligenceAgent(Agent):
    name = "clinical_intelligence"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    async def handle(self, request: dict) -> AgentResponse:
        prompt = self._build_prompt(request)
        completion = await self.llm.complete(prompt, context=request)
        flags = [DIAGNOSIS_SHAPED_MARKER] if request.get("task_type") == "explain_findings" else []
        return AgentResponse(agent_name=self.name, content=completion, flags=flags)

    def _build_prompt(self, request: dict) -> str:
        report_mode_note = (
            "This is a medical report/findings explanation. Summarize the findings, highlight "
            "anything that appears clinically significant, and suggest 2-3 questions the patient "
            "may wish to ask their doctor about it.\n"
            if request.get("task_type") == "explain_findings"
            else ""
        )
        return (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"Patient background (consent-gated, may be partial): {request.get('patient_memory', {})}\n"
            f"Case stage: {request.get('medical_context', {}).get('stage')}\n"
            f"Retrieved knowledge: {request.get('knowledge', [])}\n"
            f"{report_mode_note}\n"
            f"Question / content to reason about:\n\"\"\"{request.get('text', '')}\"\"\"\n\n"
            "Explain clearly. End with an explicit note that this is informational and must be "
            "confirmed by the patient's treating clinician."
        )
