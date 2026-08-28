from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.bloque import Bloque
from app.domain.repositories.bloque_repository import IBloqueRepository
from app.infrastructure.database.models import BloqueModel


def _a_entidad(modelo: BloqueModel) -> Bloque:
    return Bloque(
        id=modelo.id,
        nombre=modelo.nombre,
        codigo=modelo.codigo,
        unidad_negocio_id=modelo.unidad_negocio_id,
    )


class BloqueRepository(IBloqueRepository):
    def __init__(self, sesion: AsyncSession) -> None:
        self._sesion = sesion

    async def obtener_por_id(self, bloque_id: int) -> Bloque | None:
        modelo = await self._sesion.get(BloqueModel, bloque_id)
        return _a_entidad(modelo) if modelo else None

    async def listar(self, unidad_negocio_id: int) -> list[Bloque]:
        resultado = await self._sesion.execute(
            select(BloqueModel)
            .where(BloqueModel.unidad_negocio_id == unidad_negocio_id)
            .order_by(BloqueModel.nombre)
        )
        return [_a_entidad(m) for m in resultado.scalars().all()]

    async def crear(self, bloque: Bloque) -> Bloque:
        modelo = BloqueModel(
            nombre=bloque.nombre, codigo=bloque.codigo, unidad_negocio_id=bloque.unidad_negocio_id
        )
        self._sesion.add(modelo)
        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        return _a_entidad(modelo)

    async def actualizar(self, bloque: Bloque) -> Bloque:
        modelo = await self._sesion.get(BloqueModel, bloque.id)
        if modelo is None:
            raise ValueError("Bloque no encontrado para actualizar")
        modelo.nombre = bloque.nombre
        modelo.codigo = bloque.codigo
        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        return _a_entidad(modelo)

    async def eliminar(self, bloque_id: int) -> None:
        modelo = await self._sesion.get(BloqueModel, bloque_id)
        if modelo is not None:
            await self._sesion.delete(modelo)
            await self._sesion.commit()

    async def existe_codigo(
        self, unidad_negocio_id: int, codigo: str, excluir_id: int | None = None
    ) -> bool:
        consulta = select(BloqueModel.id).where(
            BloqueModel.unidad_negocio_id == unidad_negocio_id, BloqueModel.codigo == codigo
        )
        if excluir_id is not None:
            consulta = consulta.where(BloqueModel.id != excluir_id)
        resultado = await self._sesion.execute(consulta)
        return resultado.first() is not None