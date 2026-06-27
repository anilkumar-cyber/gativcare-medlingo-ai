"""EmotionEngine -- keyword heuristic, same reasoning as SafetyAgent's pattern matching: cheap,
deterministic, testable, no model call required to ship. An LLM-based or audio-prosody-based
detector can replace/augment this later without changing the Engine interface.
See docs/ARCHITECTURE.md #1."""

import re

from app.ai.engines import Engine

EMOTION_PATTERNS: dict[str, list[str]] = {
    "fear": [r"\bscared\b", r"\bafraid\b", r"\bterrified\b", r"\bworried\b"],
    "pain": [r"\bhurts?\b", r"\bpainful\b", r"\bagony\b", r"\bin pain\b"],
    "urgency": [r"\burgent\b", r"\bright now\b", r"\bimmediately\b", r"\bemergency\b"],
    "frustration": [r"\bfrustrat", r"\bfed up\b", r"\bsick of\b"],
    "sadness": [r"\bsad\b", r"\bdepressed\b", r"\bhopeless\b"],
    "confusion": [r"\bconfused\b", r"\bdon'?t understand\b", r"\bnot sure what\b"],
}

_compiled = {emotion: re.compile("|".join(patterns), re.IGNORECASE) for emotion, patterns in EMOTION_PATTERNS.items()}


class EmotionEngine(Engine):
    name = "emotion"

    async def run(self, payload: dict) -> dict:
        text = payload.get("text", "") or ""
        for emotion, pattern in _compiled.items():
            if pattern.search(text):
                return {"emotion": emotion}
        return {"emotion": None}
