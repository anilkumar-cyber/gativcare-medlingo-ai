"""Row-level "self" scoping for patient-portal users. A permission string alone can't express
"your own data only" (docs/RBAC.md design rule 2) -- routes call require_own_patient() after
require_permission() to add that check for users whose User.patient_id is set. Staff users
(patient_id is None) are unaffected and keep org-wide access per their permissions."""

import uuid

from fastapi import HTTPException, status


def require_own_patient(user, patient_id: uuid.UUID | str) -> None:
    if user.patient_id is not None and str(user.patient_id) != str(patient_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not your record")


def is_patient_user(user) -> bool:
    return user.patient_id is not None
