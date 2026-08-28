from dataclasses import dataclass
from datetime import datetime

from app.domain.entities.enums import NombreRol


@dataclass
class Usuario:
    id: int | None
    nombre: str
    correo: str
    password_hash: str
    rol: NombreRol
    unidad_negocio_id: int | None = None
    activo: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def puede_administrar(self) -> bool:
        return self.rol in (NombreRol.SUPER_ADMIN, NombreRol.ADMIN_PLATAFORMA)

    def es_admin_plataforma(self) -> bool:
        return self.rol == NombreRol.ADMIN_PLATAFORMA
