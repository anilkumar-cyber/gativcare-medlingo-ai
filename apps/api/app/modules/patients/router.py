import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.security import require_permission
from app.modules.patients import schemas, service

router = APIRouter()


@router.post("/", response_model=schemas.PatientOut, dependencies=[Depends(require_permission("patients.edit"))])
async def create_patient(payload: schemas.PatientCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await service.create_patient(
        db, org_id=user.org_id, full_name=payload.full_name, email=payload.email, phone=payload.phone, preferred_language=payload.preferred_language
    )


@router.get("/", response_model=list[schemas.PatientOut], dependencies=[Depends(require_permission("patients.view"))])
async def list_patients(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await service.list_patients(db, org_id=user.org_id)


@router.get("/{patient_id}", response_model=schemas.PatientOut, dependencies=[Depends(require_permission("patients.view"))])
async def read_patient(patient_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await service.get_patient(db, patient_id)


@router.post("/{patient_id}/cases", response_model=schemas.MedicalCaseOut, dependencies=[Depends(require_permission("patients.edit"))])
async def create_case(patient_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await service.create_case(db, org_id=user.org_id, patient_id=patient_id)


@router.get("/{patient_id}/cases", response_model=list[schemas.MedicalCaseOut], dependencies=[Depends(require_permission("patients.view"))])
async def list_cases(patient_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await service.list_cases_for_patient(db, patient_id)


@router.get("/cases/{case_id}", response_model=schemas.MedicalCaseOut, dependencies=[Depends(require_permission("patients.view"))])
async def read_case(case_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await service.get_case(db, case_id)
