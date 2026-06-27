import uuid
from datetime import datetime

from pydantic import BaseModel


class AppointmentBook(BaseModel):
    medical_case_id: uuid.UUID
    doctor_id: uuid.UUID
    scheduled_at: datetime


class AppointmentReschedule(BaseModel):
    scheduled_at: datetime


class AppointmentOut(BaseModel):
    id: uuid.UUID
    medical_case_id: uuid.UUID
    doctor_id: uuid.UUID
    scheduled_at: datetime
    status: str

    class Config:
        from_attributes = True
