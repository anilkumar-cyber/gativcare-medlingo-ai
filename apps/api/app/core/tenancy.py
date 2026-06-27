"""Sets app.current_org_id for the request's DB session, enforced again by Postgres RLS.
See docs/DATA_MODEL.md #multi-tenant-enforcement."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def set_tenant_context(session: AsyncSession, org_id: str) -> None:
    # set_config(..., is_local=true) scopes this to the current transaction, not the pooled
    # connection -- critical so one request's org_id can never leak into the next request that
    # happens to reuse the same pooled connection.
    await session.execute(text("SELECT set_config('app.current_org_id', :org_id, true)"), {"org_id": str(org_id)})
