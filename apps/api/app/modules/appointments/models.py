import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("organizations.id"), nullable=False)
    medical_case_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("medical_cases.id"), nullable=False)
    doctor_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("doctors.id"), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="scheduled")
