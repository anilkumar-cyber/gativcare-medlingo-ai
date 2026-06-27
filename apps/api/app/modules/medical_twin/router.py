import uuid

from fastapi import APIRouter, Depends

from app.core.security import require_permission
from app.modules.medical_twin.schemas import MedicalTwin

router = APIRouter()


@router.get(
    "/{patient_id}",
    response_model=MedicalTwin,
    dependencies=[Depends(require_permission("medical_twin.view"))],
)
async def get_medical_twin(patient_id: uuid.UUID):
    raise NotImplementedError  # wires service.get_twin() once the DB session dependency exists
