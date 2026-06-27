"""Real chained pipeline, not a stub -- see docs/AI_ARCHITECTURE.md #voice-pipeline.

raw_audio -> denoise -> enhance -> speaker detect -> language detect -> STT ->
MedLingoOrchestrator (text path, task="interpret") -> TTS -> output_audio

Each step is a provider/engine call behind an interface; this file owns sequencing only.
"""

from dataclasses import dataclass

from app.ai.agents.orchestrator import MedLingoOrchestrator, OrchestratorRequest
from app.ai.engines.language_intelligence import LanguageIntelligenceEngine
from app.ai.engines.speaker_recognition import SpeakerRecognitionEngine
from app.ai.providers.audio import AudioProcessor
from app.ai.providers.base import STTProvider, TTSProvider


@dataclass
class VoiceTurnRequest:
    org_id: str
    user_id: str
    conversation_session_id: str
    audio: bytes
    target_lang: str
    voice_id: str | None = None
    voice_clone_consent: bool = False


@dataclass
class VoiceTurnResponse:
    transcript: str
    interpreted_text: str
    audio: bytes
    confidence: float
    flags: list[str]


class VoicePipeline:
    def __init__(
        self,
        *,
        audio_processor: AudioProcessor,
        stt_provider: STTProvider,
        tts_provider: TTSProvider,
        orchestrator: MedLingoOrchestrator,
    ):
        self.audio_processor = audio_processor
        self.stt = stt_provider
        self.tts = tts_provider
        self.orchestrator = orchestrator
        self.language_engine = LanguageIntelligenceEngine()
        self.speaker_engine = SpeakerRecognitionEngine()

    async def run(self, request: VoiceTurnRequest) -> VoiceTurnResponse:
        cleaned = await self.audio_processor.denoise(request.audio)
        enhanced = await self.audio_processor.enhance(cleaned)

        speaker = await self.speaker_engine.run({"audio": enhanced})
        language_hint = (await self.language_engine.run({"audio": enhanced})).get("language")

        transcript = await self.stt.transcribe(enhanced, language_hint=language_hint)

        orchestrator_response = await self.orchestrator.handle_request(
            OrchestratorRequest(
                task="interpret",
                org_id=request.org_id,
                user_id=request.user_id,
                text=transcript,
                conversation_session_id=request.conversation_session_id,
                source_lang=language_hint,
                target_lang=request.target_lang,
                extra={"speaker_role": speaker.get("role")},
            )
        )

        output_audio = await self.tts.synthesize(
            orchestrator_response.content,
            language=request.target_lang,
            voice_id=request.voice_id if request.voice_clone_consent else None,
        )

        return VoiceTurnResponse(
            transcript=transcript,
            interpreted_text=orchestrator_response.content,
            audio=output_audio,
            confidence=orchestrator_response.confidence,
            flags=orchestrator_response.flags,
        )
