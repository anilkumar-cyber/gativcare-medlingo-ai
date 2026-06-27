"""Phase 3: implement against doctors table."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.appointments.models import Appointment
from app.modules.doctors.models import Doctor


async def create_doctor(
    db: AsyncSession, *, org_id: uuid.UUID, full_name: str, specialty: str | None, languages: list[str], hospital_id: uuid.UUID | None
) -> Doctor:
    doctor = Doctor(id=uuid.uuid4(), org_id=org_id, full_name=full_name, specialty=specialty, languages=languages, hospital_id=hospital_id)
    db.add(doctor)
    await db.commit()
    return doctor


async def get_doctor(db: AsyncSession, doctor_id: uuid.UUID) -> Doctor | None:
    result = await db.execute(select(Doctor).where(Doctor.id == doctor_id))
    return result.scalar_one_or_none()


async def list_doctors(db: AsyncSession, *, org_id: uuid.UUID) -> list[Doctor]:
    result = await db.execute(select(Doctor).where(Doctor.org_id == org_id))
    return list(result.scalars().all())


async def is_available(db: AsyncSession, doctor_id: uuid.UUID, slot) -> bool:
    result = await db.execute(
        select(Appointment).where(Appointment.doctor_id == doctor_id, Appointment.scheduled_at == slot, Appointment.status != "cancelled")
    )
    return result.scalar_one_or_none() is None


async def search(db: AsyncSession, *, org_id: uuid.UUID, query: str) -> list[Doctor]:
    """Called by app.ai.tools.builtin.DoctorSearchTool."""
    result = await db.execute(
        select(Doctor).where(Doctor.org_id == org_id, Doctor.full_name.ilike(f"%{query}%") | Doctor.specialty.ilike(f"%{query}%"))
    )
    return list(result.scalars().all())
