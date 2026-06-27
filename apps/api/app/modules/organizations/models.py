"""See docs/DATA_MODEL.md -- branding/domain/subscription_tier/ai_config all live here, DB-driven
per docs/ARCHITECTURE.md #5 (never hardcoded or deployed-per-customer)."""

import uuid
from datetime import datetime

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    domain: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String, nullable=True)
    subscription_tier: Mapped[str] = mapped_column(String, nullable=False, default="trial")
    ai_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
