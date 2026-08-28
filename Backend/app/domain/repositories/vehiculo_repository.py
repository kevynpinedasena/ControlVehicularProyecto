from abc import ABC, abstractmethod

from app.domain.entities.vehiculo import Vehiculo


class IVehiculoRepository(ABC):
    @abstractmethod
    async def obtener_por_id(self, vehiculo_id: int) -> Vehiculo | None: ...

    @abstractmethod
    async def obtener_por_placa(self, unidad_negocio_id: int, placa: str) -> Vehiculo | None: ...

    @abstractmethod
    async def listar_por_residente(self, residente_id: int) -> list[Vehiculo]: ...

    @abstractmethod
    async def listar(
        self,
        unidad_negocio_id: int,
        skip: int = 0,
        limit: int = 50,
        busqueda: str | None = None,
        parqueadero_id: int | None = None,
    ) -> list[Vehiculo]: ...

    @abstractmethod
    async def crear(self, vehiculo: Vehiculo) -> Vehiculo: ...

    @abstractmethod
    async def actualizar(self, vehiculo: Vehiculo) -> Vehiculo: ...

    @abstractmethod
    async def eliminar(self, vehiculo_id: int) -> None: ...

    @abstractmethod
    async def existe_placa(
        self, unidad_negocio_id: int, placa: str, excluir_id: int | None = None
    ) -> bool: ...

    @abstractmethod
    async def contar_por_parqueadero(
        self, parqueadero_id: int, excluir_id: int | None = None
    ) -> int: ...
