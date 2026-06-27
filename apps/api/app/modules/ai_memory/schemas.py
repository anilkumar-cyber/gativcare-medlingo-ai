import uuid
from datetime import datetime

from pydantic import BaseModel


class MemoryFactOut(BaseModel):
    id: uuid.UUID
    scope: str
    fact: dict
    created_at: datetime


class ConsentIn(BaseModel):
    patient_id: uuid.UUID
    scope: str


class ConsentOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    scope: str
    granted_at: datetime
    revoked_at: datetime | None
