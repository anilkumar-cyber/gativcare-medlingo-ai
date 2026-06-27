import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.scope import require_own_patient
from app.core.security import require_permission
from app.modules.appointments import schemas, service

router = APIRouter()


@router.post("/", response_model=schemas.AppointmentOut, dependencies=[Depends(require_permission("appointments.book"))])
async def book_appointment(payload: schemas.AppointmentBook, db: AsyncSession = Depends(get_db)):
    return await service.book(db, payload.medical_case_id, payload.doctor_id, payload.scheduled_at)


@router.patch("/{appointment_id}", response_model=schemas.AppointmentOut, dependencies=[Depends(require_permission("appointments.book"))])
async def reschedule_appointment(appointment_id: uuid.UUID, payload: schemas.AppointmentReschedule, db: AsyncSession = Depends(get_db)):
    return await service.reschedule(db, appointment_id, payload.scheduled_at)


@router.get("/{appointment_id}", response_model=schemas.AppointmentOut, dependencies=[Depends(require_permission("patients.view"))])
async def read_appointment(appointment_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    appointment = await service.get_appointment(db, appointment_id)
    if appointment is not None:
        await _require_own_case(db, user, appointment.medical_case_id)
    return appointment


@router.get("/case/{medical_case_id}", response_model=list[schemas.AppointmentOut], dependencies=[Depends(require_permission("patients.view"))])
async def list_appointments_for_case(medical_case_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await _require_own_case(db, user, medical_case_id)
    return await service.list_for_case(db, medical_case_id)


async def _require_own_case(db: AsyncSession, user, medical_case_id: uuid.UUID) -> None:
    if user.patient_id is None:
        return
    from app.modules.patients import service as patients_service

    case = await patients_service.get_case(db, medical_case_id)
    if case is not None:
        require_own_patient(user, case.patient_id)
