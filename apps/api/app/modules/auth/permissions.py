# auth itself gates nothing beyond "has a valid token" (enforced by get_current_user, not a
# permission string) -- there is no auth.* permission to define here.

PERMISSIONS: list[str] = []
