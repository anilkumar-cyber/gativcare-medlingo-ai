"""See docs/DATA_MODEL.md #ai-memory and docs/AI_ARCHITECTURE.md #memory-architecture.
One table for all consent-gated patient memory types -- scope distinguishes them so a new
memory type never requires a migration."""

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

MEMORY_SCOPES = ("preference", "language", "medical_history")


class Consent(Base):
    __tablename__ = "consents"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("patients.id"), nullable=False)
    scope: Mapped[str] = mapped_column(String, nullable=False)
    granted_at: Mapped[datetime] = mapped_column(nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(nullable=True)


class AIMemoryFact(Base):
    __tablename__ = "ai_memory_facts"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("organizations.id"), nullable=False)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("patients.id"), nullable=False)
    scope: Mapped[str] = mapped_column(String, nullable=False)
    fact: Mapped[dict] = mapped_column(JSONB, nullable=False)
    source_turn_id: Mapped[uuid.UUID | None] = mapped_column(UUID, ForeignKey("conversation_turns.id"), nullable=True)
    consent_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("consents.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
