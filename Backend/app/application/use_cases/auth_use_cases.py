"""Casos de uso de autenticación: login, refresco de token y usuario actual."""
from app.application.dto.auth_dto import CredencialesLoginDTO, TokensDTO, UsuarioActualDTO
from app.domain.entities.enums import NombreRol
from app.domain.exceptions.excepciones import (
    AccesoUnidadNegocioInvalidoError,
    CredencialesInvalidasError,
    EntidadNoEncontradaError,
    UnidadNegocioInactivaError,
    UsuarioInactivoError,
)
from app.domain.repositories.unidad_negocio_repository import IUnidadNegocioRepository
from app.domain.repositories.usuario_repository import IUsuarioRepository
from app.infrastructure.security.hashing import verificar_password
from app.infrastructure.security.jwt_handler import (
    crear_access_token,
    crear_refresh_token,
    decodificar_token,
)


class AutenticarUsuarioUseCase:
    """Valida credenciales y unidad de negocio, y emite el par de tokens."""

    def __init__(
        self,
        usuario_repository: IUsuarioRepository,
        unidad_negocio_repository: IUnidadNegocioRepository,
    ) -> None:
        self._usuarios = usuario_repository
        self._unidades = unidad_negocio_repository

    async def ejecutar(self, credenciales: CredencialesLoginDTO) -> TokensDTO:
        usuario = await self._usuarios.obtener_por_correo(credenciales.correo)
        if usuario is None or not verificar_password(credenciales.password, usuario.password_hash):
            raise CredencialesInvalidasError("El correo o la contraseña son incorrectos")

        if not usuario.activo:
            raise UsuarioInactivoError("El usuario se encuentra inactivo")

        if usuario.rol == NombreRol.ADMIN_PLATAFORMA:
            if credenciales.slug_unidad_negocio:
                raise AccesoUnidadNegocioInvalidoError(
                    "Este usuario administra la plataforma y no pertenece a una unidad de negocio"
                )
        else:
            unidad = (
                await self._unidades.obtener_por_id(usuario.unidad_negocio_id)
                if usuario.unidad_negocio_id
                else None
            )
            if unidad is None:
                raise AccesoUnidadNegocioInvalidoError("El usuario no pertenece a una unidad de negocio válida")
            if not unidad.activo:
                raise UnidadNegocioInactivaError("Esta unidad de negocio se encuentra deshabilitada")
            if credenciales.slug_unidad_negocio and credenciales.slug_unidad_negocio != unidad.slug:
                raise AccesoUnidadNegocioInvalidoError("No tienes acceso a esta unidad de negocio")

        return TokensDTO(
            access_token=crear_access_token(usuario.id, usuario.rol.value, usuario.unidad_negocio_id),
            refresh_token=crear_refresh_token(usuario.id),
        )


class RefrescarTokenUseCase:
    """Emite un nuevo access token a partir de un refresh token válido."""

    def __init__(self, usuario_repository: IUsuarioRepository) -> None:
        self._usuarios = usuario_repository

    async def ejecutar(self, refresh_token: str) -> TokensDTO:
        payload = decodificar_token(refresh_token, tipo_esperado="refresh")
        usuario = await self._usuarios.obtener_por_id(int(payload["sub"]))

        if usuario is None or not usuario.activo:
            raise UsuarioInactivoError("El usuario no existe o está inactivo")

        return TokensDTO(
            access_token=crear_access_token(usuario.id, usuario.rol.value, usuario.unidad_negocio_id),
            refresh_token=crear_refresh_token(usuario.id),
        )


class ObtenerUsuarioActualUseCase:
    """Recupera los datos públicos del usuario autenticado."""

    def __init__(self, usuario_repository: IUsuarioRepository) -> None:
        self._usuarios = usuario_repository

    async def ejecutar(self, usuario_id: int) -> UsuarioActualDTO:
        usuario = await self._usuarios.obtener_por_id(usuario_id)
        if usuario is None:
            raise EntidadNoEncontradaError("El usuario autenticado no existe")

        return UsuarioActualDTO(
            id=usuario.id,
            nombre=usuario.nombre,
            correo=usuario.correo,
            rol=usuario.rol,
            unidad_negocio_id=usuario.unidad_negocio_id,
        )
