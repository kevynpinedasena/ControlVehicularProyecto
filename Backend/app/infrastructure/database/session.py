"""Configuración del motor async de SQLAlchemy y la fábrica de sesiones."""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config.settings import obtener_configuracion

configuracion = obtener_configuracion()

engine = create_async_engine(
    configuracion.database_url,
    echo=not configuracion.es_produccion,
    pool_pre_ping=True,
    pool_size=configuracion.db_pool_size,
    max_overflow=configuracion.db_max_overflow,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def obtener_sesion() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia de FastAPI que provee una sesión de base de datos por request."""
    async with SessionLocal() as sesion:
        yield sesion
