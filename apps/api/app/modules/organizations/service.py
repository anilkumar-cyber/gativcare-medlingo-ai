"""ai_config/branding/subscription all live on the Organization row -- see
docs/ARCHITECTURE.md #5. create_organization() is the org-signup flow: creates the org, seeds
an Owner role with the baseline permission set, and creates the first user."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions_seed import ORG_OWNER_PERMISSIONS
from app.core.rbac import get_or_create_role
from app.core.security import create_access_token
from app.modules.auth import service as auth_service
from app.modules.organizations.models import Organization


async def get_org_settings(db: AsyncSession, org_id: uuid.UUID) -> Organization | None:
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    return result.scalar_one_or_none()


async def create_organization(
    db: AsyncSession, *, org_name: str, owner_email: str, owner_password: str, owner_full_name: str | None = None
) -> tuple[Organization, str]:
    org = Organization(id=uuid.uuid4(), name=org_name)
    db.add(org)
    await db.flush()

    owner_role = await get_or_create_role(db, org_id=org.id, name="Owner", permission_names=ORG_OWNER_PERMISSIONS)

    user = await auth_service.create_user(
        db,
        org_id=org.id,
        email=owner_email,
        password=owner_password,
        full_name=owner_full_name,
        role_id=owner_role.id,
    )
    await db.commit()

    token = create_access_token(user_id=str(user.id), org_id=str(org.id))
    return org, token
