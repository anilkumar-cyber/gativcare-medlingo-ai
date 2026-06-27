"""SQLAlchemy session + declarative base. Tenant context (app.current_org_id) is set on this
session per-request -- see app/core/tenancy.py and docs/DATA_MODEL.md."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.database_url)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
