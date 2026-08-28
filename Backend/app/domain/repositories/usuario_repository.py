from abc import ABC, abstractmethod

from app.domain.entities.usuario import Usuario


class IUsuarioRepository(ABC):
    """Contrato para el acceso a datos de usuarios del sistema."""

    @abstractmethod
    async def obtener_por_id(self, usuario_id: int) -> Usuario | None: ...

    @abstractmethod
    async def obtener_por_correo(self, correo: str) -> Usuario | None: ...

    @abstractmethod
    async def listar(
        self, unidad_negocio_id: int | None = None, skip: int = 0, limit: int = 50
    ) -> list[Usuario]: ...

    @abstractmethod
    async def crear(self, usuario: Usuario) -> Usuario: ...

    @abstractmethod
    async def actualizar(self, usuario: Usuario) -> Usuario: ...

    @abstractmethod
    async def existe_correo(self, correo: str, excluir_id: int | None = None) -> bool: ...
