from abc import ABC, abstractmethod

from app.domain.entities.unidad_negocio import UnidadNegocio


class IUnidadNegocioRepository(ABC):
    @abstractmethod
    async def obtener_por_id(self, unidad_id: int) -> UnidadNegocio | None: ...

    @abstractmethod
    async def obtener_por_slug(self, slug: str) -> UnidadNegocio | None: ...

    @abstractmethod
    async def listar(self) -> list[UnidadNegocio]: ...

    @abstractmethod
    async def crear(self, unidad: UnidadNegocio) -> UnidadNegocio: ...

    @abstractmethod
    async def actualizar(self, unidad: UnidadNegocio) -> UnidadNegocio: ...

    @abstractmethod
    async def existe_slug(self, slug: str, excluir_id: int | None = None) -> bool: ...
