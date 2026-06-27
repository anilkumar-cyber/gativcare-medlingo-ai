import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.security import require_permission
from app.modules.hospitals import schemas, service

router = APIRouter()


@router.post("/", response_model=schemas.HospitalOut, dependencies=[Depends(require_permission("hospitals.manage"))])
async def create_hospital(payload: schemas.HospitalCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await service.create_hospital(db, org_id=user.org_id, name=payload.name, city=payload.city, country=payload.country)


@router.get("/", response_model=list[schemas.HospitalOut])
async def list_hospitals(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    return await service.list_hospitals(db, org_id=user.org_id)


@router.get("/{hospital_id}", response_model=schemas.HospitalOut)
async def read_hospital(hospital_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await service.get_hospital(db, hospital_id)
