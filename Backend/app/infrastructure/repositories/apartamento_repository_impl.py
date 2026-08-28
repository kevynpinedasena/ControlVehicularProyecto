from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.apartamento import Apartamento
from app.domain.repositories.apartamento_repository import IApartamentoRepository
from app.infrastructure.database.models import ApartamentoModel


def _a_entidad(modelo: ApartamentoModel) -> Apartamento:
    return Apartamento(
        id=modelo.id,
        torre_id=modelo.torre_id,
        numero=modelo.numero,
        unidad_negocio_id=modelo.unidad_negocio_id,
        activo=modelo.activo,
    )


class ApartamentoRepository(IApartamentoRepository):
    def __init__(self, sesion: AsyncSession) -> None:
        self._sesion = sesion

    async def obtener_por_id(self, apartamento_id: int) -> Apartamento | None:
        modelo = await self._sesion.get(ApartamentoModel, apartamento_id)
        return _a_entidad(modelo) if modelo else None

    async def listar(self, unidad_negocio_id: int, torre_id: int | None = None) -> list[Apartamento]:
        consulta = select(ApartamentoModel).where(
            ApartamentoModel.unidad_negocio_id == unidad_negocio_id
        )
        if torre_id is not None:
            consulta = consulta.where(ApartamentoModel.torre_id == torre_id)
        resultado = await self._sesion.execute(consulta.order_by(ApartamentoModel.numero))
        return [_a_entidad(m) for m in resultado.scalars().all()]

    async def crear(self, apartamento: Apartamento) -> Apartamento:
        modelo = ApartamentoModel(
            torre_id=apartamento.torre_id,
            numero=apartamento.numero,
            unidad_negocio_id=apartamento.unidad_negocio_id,
            activo=apartamento.activo,
        )
        self._sesion.add(modelo)
        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        return _a_entidad(modelo)

    async def actualizar(self, apartamento: Apartamento) -> Apartamento:
        modelo = await self._sesion.get(ApartamentoModel, apartamento.id)
        if modelo is None:
            raise ValueError("Apartamento no encontrado para actualizar")
        modelo.torre_id = apartamento.torre_id
        modelo.numero = apartamento.numero
        modelo.activo = apartamento.activo
        await self._sesion.commit()
        await self._sesion.refresh(modelo)
        return _a_entidad(modelo)

    async def eliminar(self, apartamento_id: int) -> None:
        modelo = await self._sesion.get(ApartamentoModel, apartamento_id)
        if modelo is not None:
            await self._sesion.delete(modelo)
            await self._sesion.commit()

    async def existe_numero_en_torre(
        self, torre_id: int, numero: str, excluir_id: int | None = None
    ) -> bool:
        consulta = select(ApartamentoModel.id).where(
            ApartamentoModel.torre_id == torre_id, ApartamentoModel.numero == numero
        )
        if excluir_id is not None:
            consulta = consulta.where(ApartamentoModel.id != excluir_id)
        resultado = await self._sesion.execute(consulta)
        return resultado.first() is not None
