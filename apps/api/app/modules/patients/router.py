import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.scope import require_own_patient
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
    if user.patient_id is not None:
        # A patient-portal user's "list" is just their own record -- never the org's full roster.
        own = await service.get_patient(db, user.patient_id)
        return [own] if own else []
    return await service.list_patients(db, org_id=user.org_id)


@router.get("/{patient_id}", response_model=schemas.PatientOut, dependencies=[Depends(require_permission("patients.view"))])
async def read_patient(patient_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    require_own_patient(user, patient_id)
    return await service.get_patient(db, patient_id)


@router.post("/{patient_id}/cases", response_model=schemas.MedicalCaseOut, dependencies=[Depends(require_permission("patients.edit"))])
async def create_case(patient_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await service.create_case(db, org_id=user.org_id, patient_id=patient_id)


@router.get("/{patient_id}/cases", response_model=list[schemas.MedicalCaseOut], dependencies=[Depends(require_permission("patients.view"))])
async def list_cases(patient_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    require_own_patient(user, patient_id)
    return await service.list_cases_for_patient(db, patient_id)


@router.get("/cases/{case_id}", response_model=schemas.MedicalCaseOut, dependencies=[Depends(require_permission("patients.view"))])
async def read_case(case_id: uuid.UUID, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    case = await service.get_case(db, case_id)
    if case is not None:
        require_own_patient(user, case.patient_id)
    return case


@router.post("/{patient_id}/login", response_model=schemas.PatientLoginOut, dependencies=[Depends(require_permission("patients.edit"))])
async def create_patient_login(patient_id: uuid.UUID, payload: schemas.PatientLoginCreate, db: AsyncSession = Depends(get_db)):
    """Staff-only: issues portal credentials for an existing patient. Not patient-scoped by
    require_own_patient -- a patient user has no patients.edit permission, so they can never
    reach this route to begin with (see docs/RBAC.md PATIENT_PERMISSIONS)."""
    patient = await service.get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="patient not found")
    token = await service.create_patient_login(db, patient=patient, email=payload.email, password=payload.password)
    return schemas.PatientLoginOut(access_token=token, email=payload.email)
