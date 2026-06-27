"""Phase 3: implement against hospitals/departments tables."""

import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hospitals.models import Hospital


async def create_hospital(db: AsyncSession, *, org_id: uuid.UUID, name: str, city: str | None, country: str | None) -> Hospital:
    hospital = Hospital(id=uuid.uuid4(), org_id=org_id, name=name, city=city, country=country)
    db.add(hospital)
    await db.commit()
    return hospital


async def get_hospital(db: AsyncSession, hospital_id: uuid.UUID) -> Hospital | None:
    result = await db.execute(select(Hospital).where(Hospital.id == hospital_id))
    return result.scalar_one_or_none()


async def list_hospitals(db: AsyncSession, *, org_id: uuid.UUID) -> list[Hospital]:
    result = await db.execute(select(Hospital).where(Hospital.org_id == org_id))
    return list(result.scalars().all())


async def search(db: AsyncSession, *, org_id: uuid.UUID, query: str) -> list[Hospital]:
    """Called by app.ai.tools.builtin.HospitalSearchTool."""
    result = await db.execute(
        select(Hospital).where(Hospital.org_id == org_id, or_(Hospital.name.ilike(f"%{query}%"), Hospital.city.ilike(f"%{query}%")))
    )
    return list(result.scalars().all())
