"""Configuración de entornos de Alembic (online/offline) para el motor async."""
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config.settings import obtener_configuracion
from app.infrastructure.database.base import Base
from app.infrastructure.database.models import (  # noqa: F401  (registran los modelos en el metadata)
    ApartamentoModel,
    ResidenteModel,
    RolModel,
    TorreModel,
    UsuarioModel,
    VehiculoModel,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

configuracion_app = obtener_configuracion()
config.set_main_option("sqlalchemy.url", configuracion_app.database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
