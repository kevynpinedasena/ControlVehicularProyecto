from abc import ABC, abstractmethod

from app.domain.entities.bloque import Bloque


class IBloqueRepository(ABC):
    @abstractmethod
    async def obtener_por_id(self, bloque_id: int) -> Bloque | None: ...

    @abstractmethod
    async def listar(self, unidad_negocio_id: int) -> list[Bloque]: ...

    @abstractmethod
    async def crear(self, bloque: Bloque) -> Bloque: ...

    @abstractmethod
    async def actualizar(self, bloque: Bloque) -> Bloque: ...

    @abstractmethod
    async def eliminar(self, bloque_id: int) -> None: ...

    @abstractmethod
    async def existe_codigo(
        self, unidad_negocio_id: int, codigo: str, excluir_id: int | None = None
    ) -> bool: ...