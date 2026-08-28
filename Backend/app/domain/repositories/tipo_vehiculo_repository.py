from abc import ABC, abstractmethod

from app.domain.entities.tipo_vehiculo import TipoVehiculo


class ITipoVehiculoRepository(ABC):
    @abstractmethod
    async def listar(self) -> list[TipoVehiculo]: ...

    @abstractmethod
    async def obtener_por_id(self, tipo_vehiculo_id: int) -> TipoVehiculo | None: ...