"""Phase 3: JWT auth + user lookup against the users table (docs/ARCHITECTURE.md #6)."""


async def get_user(user_id):
    raise NotImplementedError


async def verify_permission(user_id, permission: str) -> bool:
    raise NotImplementedError
