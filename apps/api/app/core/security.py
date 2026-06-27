"""JWT auth + permission-check dependency. require_permission() is what every route uses
instead of role-name checks — see docs/RBAC.md design rule 1."""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(*, user_id: str, org_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": user_id, "org_id": org_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token") from exc


def check_permission(user, permission: str) -> None:
    """Direct, non-FastAPI-DI check -- used by code that isn't a route handler (e.g.
    MedLingoOrchestrator), which calls this on a `user` it already loaded. require_permission()
    below wraps this for route-level Depends() usage; both check the same thing."""
    granted = {p.name for p in (user.role.permissions if user.role else [])}
    if permission not in granted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"missing permission: {permission}")


def require_permission(permission: str):
    """FastAPI dependency: checks the authenticated user's role permissions, not their role name
    (docs/RBAC.md design rule 1) -- so a custom role with the right permission string just works."""

    from app.core.deps import get_current_user

    async def dependency(user=Depends(get_current_user)) -> None:
        check_permission(user, permission)

    return dependency
