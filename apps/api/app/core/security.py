"""JWT auth + permission-check dependency. require_permission() is what every route uses
instead of role-name checks — see docs/RBAC.md design rule 1."""


def require_permission(permission: str):
    def dependency():
        raise NotImplementedError
    return dependency
