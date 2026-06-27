import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.core.db import Base

# Import every module's models so Base.metadata is fully populated for autogenerate --
# SQLAlchemy only knows about a table once its model class has been imported somewhere.
from app.modules.organizations import models as _organizations_models  # noqa: F401
from app.modules.auth import models as _auth_models  # noqa: F401
from app.modules.hospitals import models as _hospitals_models  # noqa: F401
from app.modules.doctors import models as _doctors_models  # noqa: F401
from app.modules.patients import models as _patients_models  # noqa: F401
from app.modules.appointments import models as _appointments_models  # noqa: F401
from app.modules.conversations import models as _conversations_models  # noqa: F401
from app.modules.ai_memory import models as _ai_memory_models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=settings.database_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = create_async_engine(settings.database_url)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
