"""LanguageIntelligenceEngine -- real detection via langdetect (statistical, no API call,
no key needed). Good enough for routing/labeling; medical terminology accuracy across languages
still comes from the LLM prompt, not this engine. See docs/ARCHITECTURE.md #1."""

from langdetect import LangDetectException, detect

from app.ai.engines import Engine


class LanguageIntelligenceEngine(Engine):
    name = "language_intelligence"

    async def run(self, payload: dict) -> dict:
        text = (payload.get("text") or "").strip()
        if not text:
            return {"language": "en", "confidence": 0.0}
        try:
            return {"language": detect(text), "confidence": 0.8}
        except LangDetectException:
            return {"language": "en", "confidence": 0.0}
