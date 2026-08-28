from abc import ABC, abstractmethod

from app.domain.entities.tipo_residente import TipoResidente


class ITipoResidenteRepository(ABC):
    @abstractmethod
    async def listar(self) -> list[TipoResidente]: ...

    @abstractmethod
    async def obtener_por_id(self, tipo_residente_id: int) -> TipoResidente | None: ...