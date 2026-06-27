from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.modules.organizations import schemas, service

router = APIRouter()


@router.post("/signup", response_model=schemas.OrgSignupResponse)
async def signup(payload: schemas.OrgSignupRequest, db: AsyncSession = Depends(get_db)):
    org, token = await service.create_organization(
        db,
        org_name=payload.org_name,
        owner_email=payload.owner_email,
        owner_password=payload.owner_password,
        owner_full_name=payload.owner_full_name,
    )
    return schemas.OrgSignupResponse(organization=schemas.OrganizationOut.model_validate(org), access_token=token)


@router.get("/me", response_model=schemas.OrganizationOut)
async def read_my_organization(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    org = await service.get_org_settings(db, user.org_id)
    return org
