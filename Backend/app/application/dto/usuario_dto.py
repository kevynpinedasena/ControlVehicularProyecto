from dataclasses import dataclass

from app.domain.entities.enums import NombreRol


@dataclass
class CrearUsuarioDTO:
    nombre: str
    correo: str
    password: str
    rol: NombreRol


@dataclass
class ActualizarUsuarioDTO:
    nombre: str
    correo: str
    rol: NombreRol
    password: str | None = None


@dataclass
class RestablecerPasswordResultadoDTO:
    usuario_id: int
    correo: str
    nueva_password: str
