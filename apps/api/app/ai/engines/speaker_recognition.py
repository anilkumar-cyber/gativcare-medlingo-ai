"""SpeakerRecognitionEngine -- for text/authenticated requests, the speaker's role is just the
authenticated user's role (real, DB-backed, no ML needed). Voice diarization for audio input is
a separate concern handled by the VoiceIntelligenceAgent/STT provider, not duplicated here.
See docs/ARCHITECTURE.md #1."""

from app.ai.engines import Engine


class SpeakerRecognitionEngine(Engine):
    name = "speaker_recognition"

    async def run(self, payload: dict) -> dict:
        user = payload.get("user")
        role_name = getattr(getattr(user, "role", None), "name", None)
        return {"role": (role_name or "patient").lower()}
