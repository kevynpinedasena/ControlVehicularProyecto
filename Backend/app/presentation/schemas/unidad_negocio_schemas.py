"""Esquemas Pydantic para la administración de unidades de negocio (plataforma)."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class CrearUnidadNegocioRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    slug: str = Field(min_length=2, max_length=80)
    color_primario: str = Field(default="#2563eb", max_length=20)
    color_secundario: str = Field(default="#1e293b", max_length=20)
    admin_nombre: str = Field(min_length=2, max_length=150)
    admin_correo: EmailStr
    admin_password: str = Field(min_length=8, max_length=100)


class ActualizarUnidadNegocioRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    slug: str = Field(min_length=2, max_length=80)
    color_primario: str = Field(max_length=20)
    color_secundario: str = Field(max_length=20)
    activo: bool = True


class UnidadNegocioResponse(BaseModel):
    id: int
    nombre: str
    slug: str
    logo_url: str | None = None
    color_primario: str
    color_secundario: str
    activo: bool
    created_at: datetime | None = None


class UnidadNegocioPublicaResponse(BaseModel):
    nombre: str
    slug: str
    logo_url: str | None = None
    color_primario: str
    color_secundario: str
    activo: bool


class RestablecerPasswordRequest(BaseModel):
    nueva_password: str | None = Field(default=None, min_length=8, max_length=100)


class RestablecerPasswordResponse(BaseModel):
    usuario_id: int
    correo: str
    nueva_password: str
