"""Central settings. Every org-specific value (branding, AI config) lives in DB, not here —
this file holds only deployment-level config (DB URL, secrets, provider keys)."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24
    anthropic_api_key: str
    anthropic_model: str = "claude-sonnet-4-6"

    class Config:
        env_file = ".env"


settings = Settings()
