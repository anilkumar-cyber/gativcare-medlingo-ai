"""Implements against appointments table. book()/reschedule() are the PRD's exposed interface
(docs/MODULES.md); also called by app.ai.tools.builtin.AppointmentSchedulingTool."""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.appointments.models import Appointment
from app.modules.patients import service as patients_service


async def book(db: AsyncSession, medical_case_id: uuid.UUID, doctor_id: uuid.UUID, slot: datetime) -> Appointment:
    case = await patients_service.get_case(db, medical_case_id)
    appointment = Appointment(
        id=uuid.uuid4(), org_id=case.org_id, medical_case_id=medical_case_id, doctor_id=doctor_id, scheduled_at=slot
    )
    db.add(appointment)
    await db.commit()
    return appointment


async def reschedule(db: AsyncSession, appointment_id: uuid.UUID, new_slot: datetime) -> Appointment | None:
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()
    if appointment is None:
        return None
    appointment.scheduled_at = new_slot
    await db.commit()
    return appointment


async def get_appointment(db: AsyncSession, appointment_id: uuid.UUID) -> Appointment | None:
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    return result.scalar_one_or_none()


async def list_for_case(db: AsyncSession, medical_case_id: uuid.UUID) -> list[Appointment]:
    result = await db.execute(select(Appointment).where(Appointment.medical_case_id == medical_case_id))
    return list(result.scalars().all())
