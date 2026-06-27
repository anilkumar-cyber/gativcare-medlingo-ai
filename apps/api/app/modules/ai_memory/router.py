from fastapi import APIRouter, Depends

from app.core.security import require_permission
from app.modules.ai_memory import schemas, service

router = APIRouter()


@router.post("/consents", response_model=schemas.ConsentOut, dependencies=[Depends(require_permission("consent.manage"))])
async def grant_consent(payload: schemas.ConsentIn):
    raise NotImplementedError  # wires service.grant_consent() once DB session dependency exists


@router.delete("/consents", dependencies=[Depends(require_permission("consent.manage"))])
async def revoke_consent(payload: schemas.ConsentIn):
    raise NotImplementedError  # wires service.revoke_consent()
