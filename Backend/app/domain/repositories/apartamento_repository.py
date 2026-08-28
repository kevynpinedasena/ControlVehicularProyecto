from abc import ABC, abstractmethod

from app.domain.entities.apartamento import Apartamento


class IApartamentoRepository(ABC):
    @abstractmethod
    async def obtener_por_id(self, apartamento_id: int) -> Apartamento | None: ...

    @abstractmethod
    async def listar(self, unidad_negocio_id: int, torre_id: int | None = None) -> list[Apartamento]: ...

    @abstractmethod
    async def crear(self, apartamento: Apartamento) -> Apartamento: ...

    @abstractmethod
    async def actualizar(self, apartamento: Apartamento) -> Apartamento: ...

    @abstractmethod
    async def eliminar(self, apartamento_id: int) -> None: ...

    @abstractmethod
    async def existe_numero_en_torre(
        self, torre_id: int, numero: str, excluir_id: int | None = None
    ) -> bool: ...
