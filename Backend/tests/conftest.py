"""Fixtures compartidas: base de datos SQLite en memoria y cliente HTTP de pruebas."""
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.domain.entities.enums import NombreRol
from app.domain.entities.usuario import Usuario
from app.infrastructure.database.base import Base
from app.infrastructure.database.models import (
    ApartamentoModel,
    RolModel,
    TipoResidenteModel,
    TipoVehiculoModel,
    TorreModel,
    UnidadNegocioModel,
)
from app.infrastructure.database.session import obtener_sesion
from app.infrastructure.repositories.usuario_repository_impl import UsuarioRepository
from app.infrastructure.security.hashing import hashear_password
from app.main import app

_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_SesionPrueba = async_sessionmaker(bind=_engine, class_=AsyncSession, expire_on_commit=False)


async def _obtener_sesion_prueba() -> AsyncGenerator[AsyncSession, None]:
    async with _SesionPrueba() as sesion:
        yield sesion


app.dependency_overrides[obtener_sesion] = _obtener_sesion_prueba


@pytest_asyncio.fixture(autouse=True)
async def preparar_base_datos():
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def sesion() -> AsyncGenerator[AsyncSession, None]:
    async with _SesionPrueba() as s:
        yield s


@pytest_asyncio.fixture(autouse=True)
async def tipos_creados(preparar_base_datos: None) -> None:
    async with _SesionPrueba() as s:
        s.add_all(
            [
                TipoVehiculoModel(id=1, codigo="CARRO", nombre="Carro"),
                TipoVehiculoModel(id=2, codigo="MOTO", nombre="Moto"),
                TipoResidenteModel(id=1, codigo="PROPIETARIO", nombre="Propietario"),
                TipoResidenteModel(id=2, codigo="ARRENDATARIO", nombre="Arrendatario"),
            ]
        )
        await s.commit()


@pytest_asyncio.fixture
async def cliente() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def roles_creados(sesion: AsyncSession) -> None:
    for rol in NombreRol:
        sesion.add(RolModel(nombre=rol))
    await sesion.commit()


@pytest_asyncio.fixture
async def unidad_negocio(sesion: AsyncSession, roles_creados: None) -> UnidadNegocioModel:
    unidad = UnidadNegocioModel(nombre="Conjunto de Prueba", slug="conjunto-prueba")
    sesion.add(unidad)
    await sesion.commit()
    await sesion.refresh(unidad)
    return unidad


@pytest_asyncio.fixture
async def torre_y_apartamento(
    sesion: AsyncSession, unidad_negocio: UnidadNegocioModel
) -> ApartamentoModel:
    torre = TorreModel(nombre="Torre 1", codigo="T1", unidad_negocio_id=unidad_negocio.id)
    sesion.add(torre)
    await sesion.flush()
    apartamento = ApartamentoModel(
        torre_id=torre.id, numero="101", unidad_negocio_id=unidad_negocio.id
    )
    sesion.add(apartamento)
    await sesion.commit()
    await sesion.refresh(apartamento)
    return apartamento


@pytest_asyncio.fixture
async def credenciales_admin_plataforma(sesion: AsyncSession, roles_creados: None) -> dict[str, str]:
    correo, password = "plataforma@conjunto.com", "Plataforma123!"
    await UsuarioRepository(sesion).crear(
        Usuario(
            id=None,
            nombre="Admin Plataforma",
            correo=correo,
            password_hash=hashear_password(password),
            rol=NombreRol.ADMIN_PLATAFORMA,
            unidad_negocio_id=None,
        )
    )
    return {"correo": correo, "password": password}


@pytest_asyncio.fixture
async def credenciales_super_admin(
    sesion: AsyncSession, unidad_negocio: UnidadNegocioModel
) -> dict[str, str]:
    correo, password = "admin@conjunto.com", "Admin123!"
    await UsuarioRepository(sesion).crear(
        Usuario(
            id=None,
            nombre="Super Admin",
            correo=correo,
            password_hash=hashear_password(password),
            rol=NombreRol.SUPER_ADMIN,
            unidad_negocio_id=unidad_negocio.id,
        )
    )
    return {"correo": correo, "password": password, "slug_unidad_negocio": unidad_negocio.slug}


@pytest_asyncio.fixture
async def credenciales_vigilante(
    sesion: AsyncSession, unidad_negocio: UnidadNegocioModel
) -> dict[str, str]:
    correo, password = "vigilante@conjunto.com", "Vigilante123!"
    await UsuarioRepository(sesion).crear(
        Usuario(
            id=None,
            nombre="Vigilante Uno",
            correo=correo,
            password_hash=hashear_password(password),
            rol=NombreRol.VIGILANTE,
            unidad_negocio_id=unidad_negocio.id,
        )
    )
    return {"correo": correo, "password": password, "slug_unidad_negocio": unidad_negocio.slug}
