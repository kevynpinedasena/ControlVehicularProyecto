from abc import ABC, abstractmethod

from app.domain.entities.parqueadero import Parqueadero


class IParqueaderoRepository(ABC):
    @abstractmethod
    async def obtener_por_id(self, parqueadero_id: int) -> Parqueadero | None: ...

    @abstractmethod
    async def listar(self, unidad_negocio_id: int, bloque_id: int | None = None) -> list[Parqueadero]: ...

    @abstractmethod
    async def crear(self, parqueadero: Parqueadero) -> Parqueadero: ...

    @abstractmethod
    async def actualizar(self, parqueadero: Parqueadero) -> Parqueadero: ...

    @abstractmethod
    async def eliminar(self, parqueadero_id: int) -> None: ...

    @abstractmethod
    async def existe_numero_en_bloque(
        self, bloque_id: int, numero: str, excluir_id: int | None = None
    ) -> bool: ...