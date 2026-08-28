from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.unidad_negocio import UnidadNegocio
from app.domain.repositories.unidad_negocio_repository import IUnidadNegocioRepository
from app.infrastructure.database.models import UnidadNegocioModel


def _a_entidad(modelo: UnidadNegocioModel) -> UnidadNegocio:
    return UnidadNegocio(
        id=modelo.id,
        nombre=modelo.nombre,
        slug=modelo.slug,
        logo_url=modelo.logo_url,
        color_primario=modelo.color_primario,
        color_secundario=modelo.color_secundario,
        activo=modelo.activo,
        created_at=modelo.created_at,
        updated_at=modelo.updated_at,
    )


class UnidadNegocioRepository(IUnidadNegocioRepository):
    def __init__(self, sesion: AsyncSession) -> None:
        self._sesion = sesion

    async def obtener_por_id(self, unidad_id: int) -> UnidadNegocio | None:
        modelo = await self._sesion.get(UnidadNegocioModel, unidad_id)
        return _a_entidad(modelo) if modelo else None

    async def obtener_por_slug(self, slug: str) -> UnidadNegocio | None:
        resultado = await self._sesion.execute(
            select(UnidadNegocioModel).where(UnidadNegocioModel.slug == slug)
        )
        modelo = resultado.scalar_one_or_none()
        return _a_entidad(modelo) if modelo else None

    async def listar(self) -> list[UnidadNegocio]:
        resultado = await self._sesion.execute(
            select(UnidadNegocioModel).order_by(UnidadNegocioModel.nombre)
        )
        return [_a_entidad(m) for m in resultado.scalars().all()]

    async def crear(self, unidad: UnidadNegocio) -> UnidadNegocio:
        modelo = UnidadNegocioModel(
            nombre=unidad.nombre,
            slug=unidad.slug,
            logo_url=unidad.logo_url,
            color_primario=unidad.color_primario,
            color_secundario=unidad.color_secundario,
            activo=unidad.activo,
        )
        self._sesion.add(modelo)
        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        return _a_entidad(modelo)

    async def actualizar(self, unidad: UnidadNegocio) -> UnidadNegocio:
        modelo = await self._sesion.get(UnidadNegocioModel, unidad.id)
        if modelo is None:
            raise ValueError("Unidad de negocio no encontrada para actualizar")
        modelo.nombre = unidad.nombre
        modelo.slug = unidad.slug
        modelo.logo_url = unidad.logo_url
        modelo.color_primario = unidad.color_primario
        modelo.color_secundario = unidad.color_secundario
        modelo.activo = unidad.activo
        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        return _a_entidad(modelo)

    async def existe_slug(self, slug: str, excluir_id: int | None = None) -> bool:
        consulta = select(UnidadNegocioModel.id).where(UnidadNegocioModel.slug == slug)
        if excluir_id is not None:
            consulta = consulta.where(UnidadNegocioModel.id != excluir_id)
        resultado = await self._sesion.execute(consulta)
        return resultado.first() is not None
