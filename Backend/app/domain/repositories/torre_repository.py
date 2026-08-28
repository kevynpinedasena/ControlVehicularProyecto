from abc import ABC, abstractmethod

from app.domain.entities.torre import Torre


class ITorreRepository(ABC):
    @abstractmethod
    async def obtener_por_id(self, torre_id: int) -> Torre | None: ...

    @abstractmethod
    async def listar(self, unidad_negocio_id: int) -> list[Torre]: ...

    @abstractmethod
    async def crear(self, torre: Torre) -> Torre: ...

    @abstractmethod
    async def actualizar(self, torre: Torre) -> Torre: ...

    @abstractmethod
    async def eliminar(self, torre_id: int) -> None: ...

    @abstractmethod
    async def existe_codigo(
        self, unidad_negocio_id: int, codigo: str, excluir_id: int | None = None
    ) -> bool: ...
