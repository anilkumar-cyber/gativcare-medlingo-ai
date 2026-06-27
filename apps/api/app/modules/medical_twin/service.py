"""Medical Twin -- a read-time aggregate, not a stored table. Composes existing records into one
continuity-of-care view. Never computes or stores a diagnosis/risk score. See
docs/AI_ARCHITECTURE.md #medical-twin and docs/DATA_MODEL.md."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai_memory import service as memory_service
from app.modules.medical_twin.schemas import MedicalTwin


class PatientConsentRequiredError(Exception):
    pass


async def get_twin(session: AsyncSession, patient_id: uuid.UUID) -> MedicalTwin:
    memory = await memory_service.recall_all(session, patient_id)
    if not any(memory.values()):
        # No consented memory at all is not an error -- a brand-new patient has an empty twin.
        pass

    from app.modules.patients import service as patients_service
    from app.modules.medical_reports import service as reports_service
    from app.modules.travel import service as travel_service
    from app.modules.insurance import service as insurance_service

    patient = await patients_service.get_patient(patient_id)
    reports = await reports_service.get_reports_for_patient(patient_id)
    travel = await travel_service.get_itineraries_for_patient(patient_id)
    insurance = await insurance_service.get_policies_for_patient(patient_id)

    return MedicalTwin(
        patient_id=patient_id,
        medical_history=memory.get("medical_history", []),
        preferences=memory.get("preference", []),
        language_preferences=memory.get("language", []),
        reports=reports,
        travel_history=travel,
        insurance=insurance,
        patient_summary=patient,
    )
