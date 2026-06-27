from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.modules.auth import schemas, service
from app.modules.auth.models import User

router = APIRouter()


@router.post("/login", response_model=schemas.TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    token = await service.authenticate(db, email=form.username, password=form.password)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="incorrect email or password")
    return schemas.TokenResponse(access_token=token)


@router.get("/me", response_model=schemas.UserOut)
async def read_current_user(user: User = Depends(get_current_user)):
    return schemas.UserOut(
        id=user.id,
        org_id=user.org_id,
        email=user.email,
        full_name=user.full_name,
        role_name=user.role.name if user.role else None,
        permissions=sorted(p.name for p in (user.role.permissions if user.role else [])),
    )
