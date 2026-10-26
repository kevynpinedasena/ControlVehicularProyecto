"""Casos de uso para la gestión de usuarios del sistema, dentro de una unidad de negocio."""
import secrets

from app.application.dto.usuario_dto import (
    ActualizarUsuarioDTO,
    CrearUsuarioDTO,
    RestablecerPasswordResultadoDTO,
)
from app.domain.entities.enums import NombreRol
from app.domain.entities.usuario import Usuario
from app.domain.exceptions.excepciones import (
    CorreoDuplicadoError,
    EntidadNoEncontradaError,
    PermisoDenegadoError,
)
from app.domain.repositories.usuario_repository import IUsuarioRepository
from app.infrastructure.security.hashing import hashear_password


async def _obtener_usuario_del_tenant(
    usuarios: IUsuarioRepository, unidad_negocio_id: int, usuario_id: int
) -> Usuario:
    usuario = await usuarios.obtener_por_id(usuario_id)
    if usuario is None or usuario.unidad_negocio_id != unidad_negocio_id:
        raise EntidadNoEncontradaError("El usuario no existe")
    return usuario


class CrearUsuarioUseCase:
    def __init__(self, usuario_repository: IUsuarioRepository) -> None:
        self._usuarios = usuario_repository

    async def ejecutar(self, unidad_negocio_id: int, datos: CrearUsuarioDTO) -> Usuario:
        if datos.rol == NombreRol.ADMIN_PLATAFORMA:
            raise PermisoDenegadoError("No se puede crear un administrador de plataforma desde aquí")

        if await self._usuarios.existe_correo(datos.correo):
            raise CorreoDuplicadoError(f"El correo {datos.correo} ya está registrado")

        usuario = Usuario(
            id=None,
            nombre=datos.nombre,
            correo=datos.correo,
            password_hash=hashear_password(datos.password),
            rol=datos.rol,
            unidad_negocio_id=unidad_negocio_id,
        )
        return await self._usuarios.crear(usuario)


class ListarUsuariosUseCase:
    def __init__(self, usuario_repository: IUsuarioRepository) -> None:
        self._usuarios = usuario_repository

    async def ejecutar(self, unidad_negocio_id: int, skip: int = 0, limit: int = 50) -> list[Usuario]:
        return await self._usuarios.listar(unidad_negocio_id, skip=skip, limit=limit)


class ObtenerUsuarioUseCase:
    def __init__(self, usuario_repository: IUsuarioRepository) -> None:
        self._usuarios = usuario_repository

    async def ejecutar(self, unidad_negocio_id: int, usuario_id: int) -> Usuario:
        return await _obtener_usuario_del_tenant(self._usuarios, unidad_negocio_id, usuario_id)


class ActualizarUsuarioUseCase:
    def __init__(self, usuario_repository: IUsuarioRepository) -> None:
        self._usuarios = usuario_repository

    async def ejecutar(
        self, unidad_negocio_id: int, usuario_id: int, datos: ActualizarUsuarioDTO
    ) -> Usuario:
        if datos.rol == NombreRol.ADMIN_PLATAFORMA:
            raise PermisoDenegadoError("No se puede asignar el rol de administrador de plataforma")

        usuario_actual = await _obtener_usuario_del_tenant(self._usuarios, unidad_negocio_id, usuario_id)

        if datos.correo != usuario_actual.correo and await self._usuarios.existe_correo(
            datos.correo, excluir_id=usuario_id
        ):
            raise CorreoDuplicadoError(f"El correo {datos.correo} ya está registrado")

        usuario_actualizado = Usuario(
            id=usuario_id,
            nombre=datos.nombre,
            correo=datos.correo,
            password_hash=(
                hashear_password(datos.password) if datos.password else usuario_actual.password_hash
            ),
            rol=datos.rol,
            unidad_negocio_id=unidad_negocio_id,
            activo=usuario_actual.activo,
        )
        return await self._usuarios.actualizar(usuario_actualizado)


class CambiarEstadoUsuarioUseCase:
    def __init__(self, usuario_repository: IUsuarioRepository) -> None:
        self._usuarios = usuario_repository

    async def ejecutar(self, unidad_negocio_id: int, usuario_id: int, activo: bool) -> Usuario:
        usuario = await _obtener_usuario_del_tenant(self._usuarios, unidad_negocio_id, usuario_id)
        usuario.activo = activo
        return await self._usuarios.actualizar(usuario)


class ListarUsuariosDeUnidadUseCase:
    """Uso exclusivo del Administrador de Plataforma: lista los usuarios de CUALQUIER unidad."""

    def __init__(self, usuario_repository: IUsuarioRepository) -> None:
        self._usuarios = usuario_repository

    async def ejecutar(self, unidad_negocio_id: int) -> list[Usuario]:
        return await self._usuarios.listar(unidad_negocio_id, skip=0, limit=200)


class RestablecerPasswordUsuarioUseCase:
    """Uso exclusivo del Administrador de Plataforma: asigna una contraseña nueva a cualquier
    usuario, sin necesidad de conocer (ni de poder recuperar) la contraseña actual. Si no se
    indica una contraseña personalizada, se genera una aleatoria. La contraseña en texto plano
    solo existe en la respuesta de este caso de uso: nunca se almacena ni se registra en ningún
    lugar.
    """

    def __init__(self, usuario_repository: IUsuarioRepository) -> None:
        self._usuarios = usuario_repository

    async def ejecutar(
        self,
        unidad_negocio_id: int,
        usuario_id: int,
        password_personalizada: str | None = None,
    ) -> RestablecerPasswordResultadoDTO:
        usuario = await _obtener_usuario_del_tenant(self._usuarios, unidad_negocio_id, usuario_id)

        nueva_password = password_personalizada or secrets.token_urlsafe(9)
        usuario.password_hash = hashear_password(nueva_password)
        await self._usuarios.actualizar(usuario)

        return RestablecerPasswordResultadoDTO(
            usuario_id=usuario.id,
            correo=usuario.correo,
            nueva_password=nueva_password,
        )
