"""Implements against the patients/medical_cases tables (docs/DATA_MODEL.md)."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions_seed import PATIENT_PERMISSIONS
from app.core.rbac import get_or_create_role
from app.core.security import create_access_token
from app.modules.auth import service as auth_service
from app.modules.patients.models import MedicalCase, Patient


async def create_patient(
    db: AsyncSession, *, org_id: uuid.UUID, full_name: str, email: str | None, phone: str | None, preferred_language: str | None
) -> Patient:
    patient = Patient(id=uuid.uuid4(), org_id=org_id, full_name=full_name, email=email, phone=phone, preferred_language=preferred_language)
    db.add(patient)
    await db.commit()
    return patient


async def get_patient(db: AsyncSession, patient_id: uuid.UUID) -> Patient | None:
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    return result.scalar_one_or_none()


async def list_patients(db: AsyncSession, *, org_id: uuid.UUID) -> list[Patient]:
    result = await db.execute(select(Patient).where(Patient.org_id == org_id))
    return list(result.scalars().all())


async def create_case(db: AsyncSession, *, org_id: uuid.UUID, patient_id: uuid.UUID) -> MedicalCase:
    case = MedicalCase(id=uuid.uuid4(), org_id=org_id, patient_id=patient_id)
    db.add(case)
    await db.commit()
    return case


async def get_case(db: AsyncSession, case_id: uuid.UUID) -> MedicalCase | None:
    result = await db.execute(select(MedicalCase).where(MedicalCase.id == case_id))
    return result.scalar_one_or_none()


async def list_cases_for_patient(db: AsyncSession, patient_id: uuid.UUID) -> list[MedicalCase]:
    result = await db.execute(select(MedicalCase).where(MedicalCase.patient_id == patient_id))
    return list(result.scalars().all())


async def update_case_stage(db: AsyncSession, medical_case_id: uuid.UUID, new_stage: str) -> MedicalCase | None:
    """Called by app.core.workflow_engine.WorkflowEngine.advance()."""
    case = await get_case(db, medical_case_id)
    if case is None:
        return None
    case.stage = new_stage
    await db.commit()
    return case


async def create_patient_login(db: AsyncSession, *, patient: Patient, email: str, password: str) -> str:
    """Staff-initiated: creates a portal login for an existing patient record, seeding the
    org's "Patient" role on first use. Returns a signed access token -- staff hands the
    email/password to the patient separately; returning the token too just makes this testable
    in one call instead of requiring an immediate second /auth/login round-trip."""
    patient_role = await get_or_create_role(db, org_id=patient.org_id, name="Patient", permission_names=PATIENT_PERMISSIONS)
    user = await auth_service.create_user(
        db, org_id=patient.org_id, email=email, password=password, full_name=patient.full_name, role_id=patient_role.id, patient_id=patient.id
    )
    await db.commit()
    return create_access_token(user_id=str(user.id), org_id=str(patient.org_id))
