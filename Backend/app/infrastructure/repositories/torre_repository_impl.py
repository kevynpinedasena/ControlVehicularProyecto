from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.torre import Torre
from app.domain.repositories.torre_repository import ITorreRepository
from app.infrastructure.database.models import TorreModel


def _a_entidad(modelo: TorreModel) -> Torre:
    return Torre(
        id=modelo.id,
        nombre=modelo.nombre,
        codigo=modelo.codigo,
        unidad_negocio_id=modelo.unidad_negocio_id,
    )


class TorreRepository(ITorreRepository):
    def __init__(self, sesion: AsyncSession) -> None:
        self._sesion = sesion

    async def obtener_por_id(self, torre_id: int) -> Torre | None:
        modelo = await self._sesion.get(TorreModel, torre_id)
        return _a_entidad(modelo) if modelo else None

    async def listar(self, unidad_negocio_id: int) -> list[Torre]:
        resultado = await self._sesion.execute(
            select(TorreModel)
            .where(TorreModel.unidad_negocio_id == unidad_negocio_id)
            .order_by(TorreModel.nombre)
        )
        return [_a_entidad(m) for m in resultado.scalars().all()]

    async def crear(self, torre: Torre) -> Torre:
        modelo = TorreModel(
            nombre=torre.nombre, codigo=torre.codigo, unidad_negocio_id=torre.unidad_negocio_id
        )
        self._sesion.add(modelo)
        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        return _a_entidad(modelo)

    async def actualizar(self, torre: Torre) -> Torre:
        modelo = await self._sesion.get(TorreModel, torre.id)
        if modelo is None:
            raise ValueError("Torre no encontrada para actualizar")
        modelo.nombre = torre.nombre
        modelo.codigo = torre.codigo
        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        return _a_entidad(modelo)

    async def eliminar(self, torre_id: int) -> None:
        modelo = await self._sesion.get(TorreModel, torre_id)
        if modelo is not None:
            await self._sesion.delete(modelo)
            await self._sesion.commit()

    async def existe_codigo(
        self, unidad_negocio_id: int, codigo: str, excluir_id: int | None = None
    ) -> bool:
        consulta = select(TorreModel.id).where(
            TorreModel.unidad_negocio_id == unidad_negocio_id, TorreModel.codigo == codigo
        )
        if excluir_id is not None:
            consulta = consulta.where(TorreModel.id != excluir_id)
        resultado = await self._sesion.execute(consulta)
        return resultado.first() is not None
