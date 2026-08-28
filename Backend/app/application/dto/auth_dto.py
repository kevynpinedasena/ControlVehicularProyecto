from dataclasses import dataclass

from app.domain.entities.enums import NombreRol


@dataclass
class CredencialesLoginDTO:
    correo: str
    password: str
    slug_unidad_negocio: str | None = None


@dataclass
class TokensDTO:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass
class UsuarioActualDTO:
    id: int
    nombre: str
    correo: str
    rol: NombreRol
    unidad_negocio_id: int | None = None
