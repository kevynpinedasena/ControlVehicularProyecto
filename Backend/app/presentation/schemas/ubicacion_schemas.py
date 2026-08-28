"""Esquemas Pydantic para torres y apartamentos."""
from pydantic import BaseModel, Field


class CrearTorreRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    codigo: str = Field(min_length=1, max_length=20)


class ActualizarTorreRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    codigo: str = Field(min_length=1, max_length=20)


class TorreResponse(BaseModel):
    id: int
    nombre: str
    codigo: str


class CrearApartamentoRequest(BaseModel):
    torre_id: int
    numero: str = Field(min_length=1, max_length=20)


class ActualizarApartamentoRequest(BaseModel):
    torre_id: int
    numero: str = Field(min_length=1, max_length=20)
    activo: bool = True


class ApartamentoResponse(BaseModel):
    id: int
    torre_id: int
    numero: str
    activo: bool
