"""Casos de uso de administración de plataforma: alta y gestión de unidades de negocio."""
from app.application.dto.unidad_negocio_dto import (
    ActualizarUnidadNegocioDTO,
    CrearUnidadNegocioDTO,
)
from app.domain.entities.enums import NombreRol
from app.domain.entities.unidad_negocio import UnidadNegocio
from app.domain.entities.usuario import Usuario
from app.domain.exceptions.excepciones import (
    CorreoDuplicadoError,
    EntidadNoEncontradaError,
    SlugDuplicadoError,
)
from app.domain.repositories.unidad_negocio_repository import IUnidadNegocioRepository
from app.domain.repositories.usuario_repository import IUsuarioRepository
from app.infrastructure.security.hashing import hashear_password_async
from app.shared.utils.normalizador import normalizar_slug


class CrearUnidadNegocioUseCase:
    """Crea una unidad de negocio junto con su usuario Super Administrador inicial."""

    def __init__(
        self,
        unidad_repository: IUnidadNegocioRepository,
        usuario_repository: IUsuarioRepository,
    ) -> None:
        self._unidades = unidad_repository
        self._usuarios = usuario_repository

    async def ejecutar(self, datos: CrearUnidadNegocioDTO) -> UnidadNegocio:
        slug = normalizar_slug(datos.slug)
        if await self._unidades.existe_slug(slug):
            raise SlugDuplicadoError(f"El código '{slug}' ya está en uso por otra unidad de negocio")

        if await self._usuarios.existe_correo(datos.admin_correo):
            raise CorreoDuplicadoError(f"El correo {datos.admin_correo} ya está registrado")

        unidad = await self._unidades.crear(
            UnidadNegocio(
                id=None,
                nombre=datos.nombre,
                slug=slug,
                logo_url=datos.logo_url,
                color_primario=datos.color_primario,
                color_secundario=datos.color_secundario,
            )
        )

        await self._usuarios.crear(
            Usuario(
                id=None,
                nombre=datos.admin_nombre,
                correo=datos.admin_correo,
                password_hash=await hashear_password_async(datos.admin_password),
                rol=NombreRol.SUPER_ADMIN,
                unidad_negocio_id=unidad.id,
            )
        )

        return unidad


class ListarUnidadesNegocioUseCase:
    def __init__(self, unidad_repository: IUnidadNegocioRepository) -> None:
        self._unidades = unidad_repository

    async def ejecutar(self) -> list[UnidadNegocio]:
        return await self._unidades.listar()


class ObtenerUnidadNegocioPublicaUseCase:
    """Consulta pública (sin autenticación) usada por la pantalla de ingreso por slug."""

    def __init__(self, unidad_repository: IUnidadNegocioRepository) -> None:
        self._unidades = unidad_repository

    async def ejecutar(self, slug: str) -> UnidadNegocio:
        unidad = await self._unidades.obtener_por_slug(normalizar_slug(slug))
        if unidad is None:
            raise EntidadNoEncontradaError("No existe una unidad de negocio con ese código")
        return unidad


class ActualizarUnidadNegocioUseCase:
    def __init__(self, unidad_repository: IUnidadNegocioRepository) -> None:
        self._unidades = unidad_repository

    async def ejecutar(self, unidad_id: int, datos: ActualizarUnidadNegocioDTO) -> UnidadNegocio:
        unidad_actual = await self._unidades.obtener_por_id(unidad_id)
        if unidad_actual is None:
            raise EntidadNoEncontradaError("La unidad de negocio no existe")

        slug = normalizar_slug(datos.slug)
        if slug != unidad_actual.slug and await self._unidades.existe_slug(slug, excluir_id=unidad_id):
            raise SlugDuplicadoError(f"El código '{slug}' ya está en uso por otra unidad de negocio")

        return await self._unidades.actualizar(
            UnidadNegocio(
                id=unidad_id,
                nombre=datos.nombre,
                slug=slug,
                logo_url=datos.logo_url if datos.logo_url is not None else unidad_actual.logo_url,
                color_primario=datos.color_primario,
                color_secundario=datos.color_secundario,
                activo=datos.activo,
            )
        )


class ActualizarLogoUnidadNegocioUseCase:
    def __init__(self, unidad_repository: IUnidadNegocioRepository) -> None:
        self._unidades = unidad_repository

    async def ejecutar(self, unidad_id: int, logo_url: str) -> UnidadNegocio:
        unidad = await self._unidades.obtener_por_id(unidad_id)
        if unidad is None:
            raise EntidadNoEncontradaError("La unidad de negocio no existe")
        unidad.logo_url = logo_url
        return await self._unidades.actualizar(unidad)
