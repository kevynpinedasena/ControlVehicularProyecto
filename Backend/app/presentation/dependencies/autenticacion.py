"""Dependencias de FastAPI para autenticación y autorización basada en roles."""
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.domain.entities.enums import NombreRol
from app.domain.entities.usuario import Usuario
from app.domain.exceptions.excepciones import (
    AccesoUnidadNegocioInvalidoError,
    PermisoDenegadoError,
    TokenInvalidoError,
    UsuarioInactivoError,
)
from app.infrastructure.security.jwt_handler import decodificar_token
from app.presentation.dependencies.repositorios import SesionBD
from app.infrastructure.repositories.usuario_repository_impl import UsuarioRepository

_esquema_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def obtener_usuario_autenticado(
    token: Annotated[str, Depends(_esquema_oauth2)],
    sesion: SesionBD,
) -> Usuario:
    payload = decodificar_token(token, tipo_esperado="access")
    usuario_id = int(payload["sub"])

    usuario = await UsuarioRepository(sesion).obtener_por_id(usuario_id)
    if usuario is None:
        raise TokenInvalidoError("El usuario del token ya no existe")
    if not usuario.activo:
        raise UsuarioInactivoError("El usuario se encuentra inactivo")

    return usuario


UsuarioAutenticado = Annotated[Usuario, Depends(obtener_usuario_autenticado)]


def requerir_roles(*roles_permitidos: NombreRol):
    """Fábrica de dependencias que exige que el usuario tenga uno de los roles indicados."""

    async def verificar(usuario: UsuarioAutenticado) -> Usuario:
        if usuario.rol not in roles_permitidos:
            raise PermisoDenegadoError(
                "No tiene permisos suficientes para realizar esta acción"
            )
        return usuario

    return verificar


requerir_super_admin = requerir_roles(NombreRol.SUPER_ADMIN)
requerir_cualquier_rol = requerir_roles(NombreRol.SUPER_ADMIN, NombreRol.VIGILANTE)
requerir_admin_plataforma = requerir_roles(NombreRol.ADMIN_PLATAFORMA)


async def obtener_unidad_negocio_actual(usuario: UsuarioAutenticado) -> int:
    """Devuelve el id de la unidad de negocio del usuario autenticado (tenant scoping)."""
    if usuario.unidad_negocio_id is None:
        raise AccesoUnidadNegocioInvalidoError(
            "Esta acción requiere un usuario asociado a una unidad de negocio"
        )
    return usuario.unidad_negocio_id


UnidadNegocioActual = Annotated[int, Depends(obtener_unidad_negocio_actual)]
