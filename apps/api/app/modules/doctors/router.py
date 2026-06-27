import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.security import require_permission
from app.modules.doctors import schemas, service

router = APIRouter()


@router.post("/", response_model=schemas.DoctorOut, dependencies=[Depends(require_permission("doctors.manage"))])
async def create_doctor(payload: schemas.DoctorCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await service.create_doctor(
        db, org_id=user.org_id, full_name=payload.full_name, specialty=payload.specialty, languages=payload.languages, hospital_id=payload.hospital_id
    )


@router.get("/", response_model=list[schemas.DoctorOut])
async def list_doctors(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await service.list_doctors(db, org_id=user.org_id)


@router.get("/{doctor_id}", response_model=schemas.DoctorOut)
async def read_doctor(doctor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await service.get_doctor(db, doctor_id)
