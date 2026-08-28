"""Esquemas Pydantic para la gestión de usuarios."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.domain.entities.enums import NombreRol


class CrearUsuarioRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    correo: EmailStr
    password: str = Field(min_length=8, max_length=100)
    rol: NombreRol


class ActualizarUsuarioRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    correo: EmailStr
    rol: NombreRol
    password: str | None = Field(default=None, min_length=8, max_length=100)


class CambiarEstadoUsuarioRequest(BaseModel):
    activo: bool


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: NombreRol
    unidad_negocio_id: int | None = None
    activo: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
