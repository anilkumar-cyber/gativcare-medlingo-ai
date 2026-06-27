import uuid

from pydantic import BaseModel


class HospitalCreate(BaseModel):
    name: str
    city: str | None = None
    country: str | None = None


class HospitalOut(BaseModel):
    id: uuid.UUID
    name: str
    city: str | None
    country: str | None

    class Config:
        from_attributes = True
