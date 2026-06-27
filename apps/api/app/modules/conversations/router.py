import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agents.orchestrator import OrchestratorRequest
from app.ai.providers.claude_provider import AIProviderError
from app.core.deps import get_current_user, get_db, get_orchestrator
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


@router.post(
    "/{session_id}/messages",
    response_model=schemas.MessageOut,
    dependencies=[Depends(require_permission("conversations.translate"))],
)
async def send_message(
    session_id: uuid.UUID,
    payload: schemas.MessageIn,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
    orchestrator=Depends(get_orchestrator),
):
    """The real-time entry point into MedLingoOrchestrator -- this is what
    AIAssistantWidget/the patient AI Interpreter page actually call. Requires
    ANTHROPIC_API_KEY to be a real key; without one this returns a clean 503, not a crash,
    because every other pipeline step (intent, language, speaker, context, safety, memory,
    persistence) runs for real regardless of whether the final LLM call succeeds."""
    request = OrchestratorRequest(
        org_id=str(user.org_id),
        user_id=str(user.id),
        text=payload.text,
        task=payload.task,
        patient_id=str(payload.patient_id) if payload.patient_id else None,
        medical_case_id=str(payload.medical_case_id) if payload.medical_case_id else None,
        conversation_session_id=str(session_id),
        target_lang=payload.target_lang,
        db=db,
    )
    try:
        response = await orchestrator.handle_request(request)
    except AIProviderError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"AI provider unavailable: {exc}") from exc

    return schemas.MessageOut(
        content=response.content,
        confidence=response.confidence,
        flags=response.flags,
        emergency=response.emergency,
        intent=response.intent,
    )
