import uuid
from datetime import datetime

from pydantic import BaseModel


class ConversationSessionCreate(BaseModel):
    medical_case_id: uuid.UUID | None = None
    mode: str = "text"


class ConversationSessionOut(BaseModel):
    id: uuid.UUID
    medical_case_id: uuid.UUID | None
    mode: str
    started_at: datetime
    ended_at: datetime | None

    class Config:
        from_attributes = True


class ConversationTurnOut(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    content: str
    confidence: float
    flags: list[str]
    created_at: datetime

    class Config:
        from_attributes = True
