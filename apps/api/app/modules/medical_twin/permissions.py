# See docs/RBAC.md. Mirrors patients.view/reports.view scoping -- the twin can't be looser
# than the records it aggregates.

PERMISSIONS = [
    "medical_twin.view",
    "medical_twin.edit_preferences",
]
