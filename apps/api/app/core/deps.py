"""Shared FastAPI dependencies: get_db (tenant-scoped session), get_current_user."""

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core.db import async_session
from app.core.security import decode_access_token
from app.core.tenancy import set_tenant_context

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


def get_orchestrator(request: Request):
    """The single MedLingoOrchestrator instance created at app startup -- see app/main.py
    lifespan. Routes depend on this instead of importing/constructing one themselves."""
    return request.app.state.orchestrator


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated")

    payload = decode_access_token(token)
    user_id = payload.get("sub")
    org_id = payload.get("org_id")

    from app.modules.auth.models import User, Role  # local import avoids a core->modules cycle at import time

    await set_tenant_context(db, org_id)
    result = await db.execute(
        select(User).options(selectinload(User.role).selectinload(Role.permissions)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid user")
    return user
