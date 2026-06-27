"""Implements against conversation_sessions/conversation_turns tables. add_turn() is called by
app.ai.agents.orchestrator after every agent response."""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.conversations.models import ConversationSession, ConversationTurn


async def start_session(
    db: AsyncSession, org_id: uuid.UUID, medical_case_id: uuid.UUID | None = None, mode: str = "text"
) -> ConversationSession:
    session = ConversationSession(id=uuid.uuid4(), org_id=org_id, medical_case_id=medical_case_id, mode=mode)
    db.add(session)
    await db.commit()
    return session


async def end_session(db: AsyncSession, session_id: uuid.UUID) -> None:
    result = await db.execute(select(ConversationSession).where(ConversationSession.id == session_id))
    session = result.scalar_one_or_none()
    if session is not None:
        session.ended_at = datetime.utcnow()
        await db.commit()


async def add_turn(
    db: AsyncSession, *, session_id: uuid.UUID, speaker_user_id: uuid.UUID | None, content: str, confidence: float, flags: list[str]
) -> ConversationTurn:
    turn = ConversationTurn(
        id=uuid.uuid4(), session_id=session_id, speaker_user_id=speaker_user_id, content=content, confidence=confidence, flags=flags
    )
    db.add(turn)
    await db.commit()
    return turn


async def list_turns(db: AsyncSession, session_id: uuid.UUID) -> list[ConversationTurn]:
    result = await db.execute(select(ConversationTurn).where(ConversationTurn.session_id == session_id))
    return list(result.scalars().all())
