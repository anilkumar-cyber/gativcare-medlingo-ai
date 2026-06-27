"""Voice Intelligence Agent — owns the speech in/out boundary. Delegates actual ASR/TTS/DSP to
provider implementations (docs/AI_ARCHITECTURE.md #voice-pipeline); this agent owns sequencing,
speaker/emotion hand-off, and voice-clone consent enforcement, not the models themselves."""

from app.ai.agents import Agent, AgentResponse

SYSTEM_PROMPT = """You sequence the voice pipeline: enhanced audio in, transcribed text out (or
the reverse for synthesis). You never fabricate transcript content the audio doesn't support, and
you never synthesize a cloned voice without an explicit, current consent record."""


class VoiceCloneConsentError(Exception):
    pass


class VoiceIntelligenceAgent(Agent):
    name = "voice_intelligence"
    SYSTEM_PROMPT = SYSTEM_PROMPT

    def __init__(self, llm_provider, stt_provider, tts_provider):
        super().__init__(llm_provider)
        self.stt = stt_provider
        self.tts = tts_provider

    async def handle(self, request: dict) -> AgentResponse:
        direction = request.get("direction", "stt")
        if direction == "stt":
            text = await self.stt.transcribe(request["audio"], language_hint=request.get("language_hint"))
            return AgentResponse(agent_name=self.name, content=text)

        voice_id = request.get("voice_id")
        if voice_id and not request.get("voice_clone_consent"):
            raise VoiceCloneConsentError(
                "voice_id requested without an explicit, current voice_clone_consent record"
            )
        audio = await self.tts.synthesize(
            request["text"], language=request["language"], voice_id=voice_id
        )
        return AgentResponse(agent_name=self.name, content="", metadata={"audio": audio})
