# See docs/RBAC.md -- org-level config permissions. Signup itself is unauthenticated by design
# (it's how a new tenant is born); everything else here requires a valid token.

PERMISSIONS = [
    "ai.manage_config",
    "api.manage_keys",
]
