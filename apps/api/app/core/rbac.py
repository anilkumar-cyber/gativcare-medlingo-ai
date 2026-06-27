"""Shared role/permission provisioning -- used by organizations.service (Owner role at signup)
and patients.service (Patient role at first portal-login creation). One place so "get or create a
permission row" isn't reimplemented per caller. See docs/RBAC.md."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import Permission, Role


async def get_or_create_permission(db: AsyncSession, name: str) -> Permission:
    result = await db.execute(select(Permission).where(Permission.name == name))
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing
    permission = Permission(id=uuid.uuid4(), name=name)
    db.add(permission)
    await db.flush()
    return permission


async def get_or_create_role(db: AsyncSession, *, org_id: uuid.UUID, name: str, permission_names: list[str]) -> Role:
    result = await db.execute(select(Role).where(Role.org_id == org_id, Role.name == name))
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing
    permissions = [await get_or_create_permission(db, p) for p in permission_names]
    role = Role(id=uuid.uuid4(), org_id=org_id, name=name, permissions=permissions)
    db.add(role)
    await db.flush()
    return role
