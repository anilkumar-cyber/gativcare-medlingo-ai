# See docs/RBAC.md. consent.manage gates grant/revoke; memory reads are gated by the consent
# record itself (service.py), not by a separate permission -- a permission can't substitute for
# patient consent on their own clinical/preference data.

PERMISSIONS = [
    "consent.manage",
]
