"""Patient + MedicalCase -- the spine of the patient journey. stage matches
app.core.workflow_engine.DEFAULT_STAGE_SEQUENCE. See docs/DATA_MODEL.md."""

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("organizations.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    preferred_language: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)


class MedicalCase(Base):
    __tablename__ = "medical_cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("organizations.id"), nullable=False)
    patient_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("patients.id"), nullable=False)
    assigned_doctor_id: Mapped[uuid.UUID | None] = mapped_column(UUID, ForeignKey("doctors.id"), nullable=True)
    stage: Mapped[str] = mapped_column(String, nullable=False, default="inquiry")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
