"""Medical Interpreter Agent — interprets meaning, not words. Same clinical fact rendered in
doctor-register or patient-register depending on the listener. See docs/AI_ARCHITECTURE.md."""

from app.ai.agents import Agent, AgentResponse

SYSTEM_PROMPT = """You are a certified medical interpreter and senior multilingual physician.
You never translate literally. You understand the clinical meaning of an utterance first, then
re-express it naturally in the target language, preserving medical accuracy, preserving the
pronunciation of drug/medical proper nouns, adapting tone to the listener's emotional state, and
respecting cultural norms (greetings, family involvement, religious sensitivity, directness vs
indirectness). You never add information that was not said. You never soften or omit clinically
important information, even when translating into a gentler register. You are not the treating
clinician — you interpret what the clinician or patient says; you do not generate new clinical
advice."""

CLINICAL_REGISTER_ROLES = {"doctor", "surgeon", "consultant", "nurse"}


class MedicalInterpreterAgent(Agent):
    name = "medical_interpreter"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    async def handle(self, request: dict) -> AgentResponse:
        prompt = self._build_prompt(request)
        completion = await self.llm.complete(prompt, context=request)
        return AgentResponse(agent_name=self.name, content=completion)

    def _build_prompt(self, request: dict) -> str:
        speaker_role = request.get("speaker_role", "patient")
        register = (
            "clinically precise terminology appropriate for a healthcare professional"
            if speaker_role in CLINICAL_REGISTER_ROLES
            else "plain, compassionate, patient-friendly language with no unexplained jargon"
        )
        emotion = request.get("emotion")
        tone_note = f"The speaker's detected emotional state is '{emotion}' — adapt tone accordingly.\n" if emotion else ""

        return (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"Speaker role: {speaker_role}\n"
            f"Source language: {request.get('source_lang')} -> Target language: {request.get('target_lang')}\n"
            f"Register for the output: {register}\n"
            f"{tone_note}"
            f"Relevant medical/case context: {request.get('medical_context', {})}\n"
            f"Relevant prior patient memory (consent-gated): {request.get('patient_memory', {})}\n\n"
            f"Utterance to interpret:\n\"\"\"{request.get('text', '')}\"\"\"\n\n"
            "Produce only the natural, medically accurate interpretation in the target language. "
            "Do not explain your reasoning."
        )
