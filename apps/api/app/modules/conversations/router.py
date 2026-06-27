import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.security import require_permission
from app.modules.conversations import schemas, service

router = APIRouter()


@router.post("/", response_model=schemas.ConversationSessionOut, dependencies=[Depends(require_permission("conversations.translate"))])
async def start_session(payload: schemas.ConversationSessionCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await service.start_session(db, user.org_id, payload.medical_case_id, payload.mode)


@router.post("/{session_id}/end", dependencies=[Depends(require_permission("conversations.translate"))])
async def end_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await service.end_session(db, session_id)
    return {"status": "ended"}


@router.get("/{session_id}/turns", response_model=list[schemas.ConversationTurnOut])
async def list_turns(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await service.list_turns(db, session_id)
