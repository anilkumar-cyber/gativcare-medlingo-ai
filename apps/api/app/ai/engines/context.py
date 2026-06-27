"""ContextEngine -- real DB lookup of the case's current stage, the one piece of "medical
context" that's structured data rather than free text. Conversation history/turn context is
handled by the Conversation Intelligence agent, not duplicated here. See docs/ARCHITECTURE.md #1."""

from app.ai.engines import Engine


class ContextEngine(Engine):
    name = "context"

    async def run(self, payload: dict) -> dict:
        medical_case_id = payload.get("medical_case_id")
        db = payload.get("db")
        if not medical_case_id or db is None:
            return {"stage": None}

        from app.modules.patients import service as patients_service

        case = await patients_service.get_case(db, medical_case_id)
        return {"stage": case.stage if case else None}
