import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.models import Role, User


async def get_user(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(
        select(User).options(selectinload(User.role).selectinload(Role.permissions)).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession, *, org_id: uuid.UUID, email: str, password: str, full_name: str | None = None, role_id: uuid.UUID | None = None
) -> User:
    user = User(
        id=uuid.uuid4(),
        org_id=org_id,
        role_id=role_id,
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
    )
    db.add(user)
    await db.flush()
    return user


async def authenticate(db: AsyncSession, *, email: str, password: str) -> str | None:
    """Returns a signed access token, or None if the credentials don't check out."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active or not verify_password(password, user.hashed_password):
        return None
    return create_access_token(user_id=str(user.id), org_id=str(user.org_id))


async def verify_permission(user: User, permission: str) -> bool:
    return permission in {p.name for p in (user.role.permissions if user.role else [])}
