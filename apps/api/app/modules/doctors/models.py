import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("organizations.id"), nullable=False)
    hospital_id: Mapped[uuid.UUID | None] = mapped_column(UUID, ForeignKey("hospitals.id"), nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID, ForeignKey("users.id"), nullable=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    specialty: Mapped[str | None] = mapped_column(String, nullable=True)
    languages: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
