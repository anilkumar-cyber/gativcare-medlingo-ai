"""Sets app.current_org_id for the request's DB session, enforced again by Postgres RLS.
See docs/DATA_MODEL.md #multi-tenant-enforcement."""


async def set_tenant_context(session, org_id: str) -> None:
    raise NotImplementedError
