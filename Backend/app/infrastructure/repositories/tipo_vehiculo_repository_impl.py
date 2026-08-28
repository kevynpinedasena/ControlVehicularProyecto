from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.tipo_vehiculo import TipoVehiculo
from app.domain.repositories.tipo_vehiculo_repository import ITipoVehiculoRepository
from app.infrastructure.database.models import TipoVehiculoModel


def _a_entidad(modelo: TipoVehiculoModel) -> TipoVehiculo:
    return TipoVehiculo(id=modelo.id, codigo=modelo.codigo, nombre=modelo.nombre)


class TipoVehiculoRepository(ITipoVehiculoRepository):
    def __init__(self, sesion: AsyncSession) -> None:
        self._sesion = sesion

    async def listar(self) -> list[TipoVehiculo]:
        resultado = await self._sesion.execute(
            select(TipoVehiculoModel).order_by(TipoVehiculoModel.id)
        )
        return [_a_entidad(m) for m in resultado.scalars().all()]

    async def obtener_por_id(self, tipo_vehiculo_id: int) -> TipoVehiculo | None:
        modelo = await self._sesion.get(TipoVehiculoModel, tipo_vehiculo_id)
        return _a_entidad(modelo) if modelo else None