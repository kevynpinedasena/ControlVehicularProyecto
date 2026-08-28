"""Casos de uso de solo lectura para los catálogos de tipo de vehículo y tipo de residente."""
from app.domain.entities.tipo_residente import TipoResidente
from app.domain.entities.tipo_vehiculo import TipoVehiculo
from app.domain.repositories.tipo_residente_repository import ITipoResidenteRepository
from app.domain.repositories.tipo_vehiculo_repository import ITipoVehiculoRepository


class ListarTiposVehiculoUseCase:
    def __init__(self, tipo_vehiculo_repository: ITipoVehiculoRepository) -> None:
        self._tipos = tipo_vehiculo_repository

    async def ejecutar(self) -> list[TipoVehiculo]:
        return await self._tipos.listar()


class ListarTiposResidenteUseCase:
    def __init__(self, tipo_residente_repository: ITipoResidenteRepository) -> None:
        self._tipos = tipo_residente_repository

    async def ejecutar(self) -> list[TipoResidente]:
        return await self._tipos.listar()