"""Identity + DB-driven RBAC. Roles are named bundles of permissions stored here, not hardcoded
enums -- an org admin can create a custom role without a code change. See docs/RBAC.md."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", UUID, ForeignKey("permissions.id"), primary_key=True),
)


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # e.g. "patients.view"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID | None] = mapped_column(UUID, ForeignKey("organizations.id"), nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)  # e.g. "Doctor", "Senior Nurse"
    permissions: Mapped[list[Permission]] = relationship(secondary=role_permissions)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("organizations.id"), nullable=False)
    role_id: Mapped[uuid.UUID | None] = mapped_column(UUID, ForeignKey("roles.id"), nullable=True)
    # Set only for patient-portal logins -- links this user's account to exactly one patient
    # record, which is what makes row-level "self" scoping possible (docs/RBAC.md). Staff/doctor/
    # coordinator users leave this null.
    patient_id: Mapped[uuid.UUID | None] = mapped_column(UUID, ForeignKey("patients.id"), nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    role: Mapped[Role | None] = relationship()
