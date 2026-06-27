import uuid

from pydantic import BaseModel, EmailStr


class OrgSignupRequest(BaseModel):
    org_name: str
    owner_email: EmailStr
    owner_password: str
    owner_full_name: str | None = None


class OrganizationOut(BaseModel):
    id: uuid.UUID
    name: str
    domain: str | None
    subscription_tier: str

    class Config:
        from_attributes = True


class OrgSignupResponse(BaseModel):
    organization: OrganizationOut
    access_token: str
