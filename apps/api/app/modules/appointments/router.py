import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.core.security import require_permission
from app.modules.appointments import schemas, service

router = APIRouter()


@router.post("/", response_model=schemas.AppointmentOut, dependencies=[Depends(require_permission("appointments.book"))])
async def book_appointment(payload: schemas.AppointmentBook, db: AsyncSession = Depends(get_db)):
    return await service.book(db, payload.medical_case_id, payload.doctor_id, payload.scheduled_at)


@router.patch("/{appointment_id}", response_model=schemas.AppointmentOut, dependencies=[Depends(require_permission("appointments.book"))])
async def reschedule_appointment(appointment_id: uuid.UUID, payload: schemas.AppointmentReschedule, db: AsyncSession = Depends(get_db)):
    return await service.reschedule(db, appointment_id, payload.scheduled_at)


@router.get("/{appointment_id}", response_model=schemas.AppointmentOut)
async def read_appointment(appointment_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await service.get_appointment(db, appointment_id)
