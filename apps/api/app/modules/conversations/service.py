"""Phase 3: implement against conversation_sessions/conversation_turns tables. add_turn() is
called by app.ai.agents.orchestrator after every agent response."""


async def start_session(org_id, medical_case_id=None, mode: str = "text"):
    raise NotImplementedError


async def add_turn(*, session_id, speaker_user_id, content: str, confidence: float, flags: list[str]):
    raise NotImplementedError
