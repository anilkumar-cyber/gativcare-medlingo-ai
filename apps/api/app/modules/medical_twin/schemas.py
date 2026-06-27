import uuid

from pydantic import BaseModel


class MedicalTwin(BaseModel):
    patient_id: uuid.UUID
    medical_history: list[dict]
    preferences: list[dict]
    language_preferences: list[dict]
    reports: list
    travel_history: list
    insurance: list
    patient_summary: dict | None

    class Config:
        # Explicitly no diagnosis/risk_score field -- see docs/AI_ARCHITECTURE.md #medical-twin.
        # Adding one here would need a product/clinical-governance decision, not a code change.
        extra = "forbid"
