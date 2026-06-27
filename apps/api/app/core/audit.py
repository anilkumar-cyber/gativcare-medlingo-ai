"""Append-only audit event writer. INSERT-only at the DB grant level — see docs/DATA_MODEL.md."""


async def record_event(*, org_id: str, actor_user_id: str, action: str, entity_type: str, entity_id: str, metadata: dict | None = None) -> None:
    raise NotImplementedError
