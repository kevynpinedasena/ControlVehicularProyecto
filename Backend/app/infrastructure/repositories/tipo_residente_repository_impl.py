from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.tipo_residente import TipoResidente
from app.domain.repositories.tipo_residente_repository import ITipoResidenteRepository
from app.infrastructure.database.models import TipoResidenteModel


def _a_entidad(modelo: TipoResidenteModel) -> TipoResidente:
    return TipoResidente(id=modelo.id, codigo=modelo.codigo, nombre=modelo.nombre)


class TipoResidenteRepository(ITipoResidenteRepository):
    def __init__(self, sesion: AsyncSession) -> None:
        self._sesion = sesion

    async def listar(self) -> list[TipoResidente]:
        resultado = await self._sesion.execute(
            select(TipoResidenteModel).order_by(TipoResidenteModel.id)
        )
        return [_a_entidad(m) for m in resultado.scalars().all()]

    async def obtener_por_id(self, tipo_residente_id: int) -> TipoResidente | None:
        modelo = await self._sesion.get(TipoResidenteModel, tipo_residente_id)
        return _a_entidad(modelo) if modelo else None