import uuid

from pydantic import BaseModel


class PatientCreate(BaseModel):
    full_name: str
    email: str | None = None
    phone: str | None = None
    preferred_language: str | None = None


class PatientOut(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str | None
    phone: str | None
    preferred_language: str | None

    class Config:
        from_attributes = True


class MedicalCaseOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    stage: str
    assigned_doctor_id: uuid.UUID | None

    class Config:
        from_attributes = True
