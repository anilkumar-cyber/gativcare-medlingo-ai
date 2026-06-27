import uuid
from datetime import datetime

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ConversationSession(Base):
    __tablename__ = "conversation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("organizations.id"), nullable=False)
    medical_case_id: Mapped[uuid.UUID | None] = mapped_column(UUID, ForeignKey("medical_cases.id"), nullable=True)
    mode: Mapped[str] = mapped_column(String, nullable=False, default="text")
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(nullable=True)


class ConversationTurn(Base):
    __tablename__ = "conversation_turns"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("conversation_sessions.id"), nullable=False)
    speaker_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID, ForeignKey("users.id"), nullable=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    flags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
