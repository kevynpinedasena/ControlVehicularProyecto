from dataclasses import dataclass

from app.domain.entities.enums import NombreRol


@dataclass
class Rol:
    id: int | None
    nombre: NombreRol
