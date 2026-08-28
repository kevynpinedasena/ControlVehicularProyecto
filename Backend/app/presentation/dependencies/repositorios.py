"""Proveedores (inyección de dependencias) de repositorios para FastAPI."""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.apartamento_repository import IApartamentoRepository
from app.domain.repositories.bloque_repository import IBloqueRepository
from app.domain.repositories.parqueadero_repository import IParqueaderoRepository
from app.domain.repositories.residente_repository import IResidenteRepository
from app.domain.repositories.tipo_residente_repository import ITipoResidenteRepository
from app.domain.repositories.tipo_vehiculo_repository import ITipoVehiculoRepository
from app.domain.repositories.torre_repository import ITorreRepository
from app.domain.repositories.unidad_negocio_repository import IUnidadNegocioRepository
from app.domain.repositories.usuario_repository import IUsuarioRepository
from app.domain.repositories.vehiculo_repository import IVehiculoRepository
from app.infrastructure.database.session import obtener_sesion
from app.infrastructure.repositories.apartamento_repository_impl import ApartamentoRepository
from app.infrastructure.repositories.bloque_repository_impl import BloqueRepository
from app.infrastructure.repositories.parqueadero_repository_impl import ParqueaderoRepository
from app.infrastructure.repositories.residente_repository_impl import ResidenteRepository
from app.infrastructure.repositories.tipo_residente_repository_impl import TipoResidenteRepository
from app.infrastructure.repositories.tipo_vehiculo_repository_impl import TipoVehiculoRepository
from app.infrastructure.repositories.torre_repository_impl import TorreRepository
from app.infrastructure.repositories.unidad_negocio_repository_impl import UnidadNegocioRepository
from app.infrastructure.repositories.usuario_repository_impl import UsuarioRepository
from app.infrastructure.repositories.vehiculo_repository_impl import VehiculoRepository

SesionBD = Annotated[AsyncSession, Depends(obtener_sesion)]


def obtener_usuario_repository(sesion: SesionBD) -> IUsuarioRepository:
    return UsuarioRepository(sesion)


def obtener_torre_repository(sesion: SesionBD) -> ITorreRepository:
    return TorreRepository(sesion)


def obtener_apartamento_repository(sesion: SesionBD) -> IApartamentoRepository:
    return ApartamentoRepository(sesion)


def obtener_residente_repository(sesion: SesionBD) -> IResidenteRepository:
    return ResidenteRepository(sesion)


def obtener_vehiculo_repository(sesion: SesionBD) -> IVehiculoRepository:
    return VehiculoRepository(sesion)


def obtener_unidad_negocio_repository(sesion: SesionBD) -> IUnidadNegocioRepository:
    return UnidadNegocioRepository(sesion)


def obtener_tipo_vehiculo_repository(sesion: SesionBD) -> ITipoVehiculoRepository:
    return TipoVehiculoRepository(sesion)


def obtener_tipo_residente_repository(sesion: SesionBD) -> ITipoResidenteRepository:
    return TipoResidenteRepository(sesion)


def obtener_bloque_repository(sesion: SesionBD) -> IBloqueRepository:
    return BloqueRepository(sesion)


def obtener_parqueadero_repository(sesion: SesionBD) -> IParqueaderoRepository:
    return ParqueaderoRepository(sesion)
