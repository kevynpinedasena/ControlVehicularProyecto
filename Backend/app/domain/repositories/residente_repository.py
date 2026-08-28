from abc import ABC, abstractmethod

from app.domain.entities.residente import Residente


class IResidenteRepository(ABC):
    @abstractmethod
    async def obtener_por_id(self, residente_id: int) -> Residente | None: ...

    @abstractmethod
    async def listar(
        self,
        unidad_negocio_id: int,
        skip: int = 0,
        limit: int = 50,
        busqueda: str | None = None,
    ) -> list[Residente]: ...

    @abstractmethod
    async def crear(self, residente: Residente) -> Residente: ...

    @abstractmethod
    async def actualizar(self, residente: Residente) -> Residente: ...

    @abstractmethod
    async def eliminar(self, residente_id: int) -> None: ...

    @abstractmethod
    async def existe_documento(
        self, unidad_negocio_id: int, documento: str, excluir_id: int | None = None
    ) -> bool: ...
