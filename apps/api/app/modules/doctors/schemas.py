import uuid

from pydantic import BaseModel


class DoctorCreate(BaseModel):
    full_name: str
    specialty: str | None = None
    languages: list[str] = []
    hospital_id: uuid.UUID | None = None


class DoctorOut(BaseModel):
    id: uuid.UUID
    full_name: str
    specialty: str | None
    languages: list[str]
    hospital_id: uuid.UUID | None

    class Config:
        from_attributes = True
