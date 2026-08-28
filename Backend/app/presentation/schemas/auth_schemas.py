"""Esquemas Pydantic para autenticación."""
from pydantic import BaseModel, EmailStr, Field

from app.domain.entities.enums import NombreRol


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str = Field(min_length=1)
    slug_unidad_negocio: str | None = Field(
        default=None, description="Código de la unidad de negocio (vacío para el admin de plataforma)"
    )


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UsuarioActualResponse(BaseModel):
    id: int
    nombre: str
    correo: str
    rol: NombreRol
    unidad_negocio_id: int | None = None
