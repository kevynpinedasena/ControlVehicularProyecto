"""Esquemas Pydantic para la gestión de residentes."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.presentation.schemas.catalogo_schemas import TipoResidenteResponse
from app.presentation.schemas.vehiculo_schemas import VehiculoResponse


class CrearResidenteRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    documento: str = Field(min_length=1, max_length=30)
    tipo_residente_id: int
    apartamento_id: int
    telefono_1: str | None = Field(default=None, max_length=30)
    telefono_2: str | None = Field(default=None, max_length=30)


class ActualizarResidenteRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    documento: str = Field(min_length=1, max_length=30)
    tipo_residente_id: int
    apartamento_id: int
    activo: bool = True
    telefono_1: str | None = Field(default=None, max_length=30)
    telefono_2: str | None = Field(default=None, max_length=30)


class ResidenteResponse(BaseModel):
    id: int
    nombre: str
    documento: str
    tipo_residente: TipoResidenteResponse
    apartamento_id: int
    telefono_1: str | None = None
    telefono_2: str | None = None
    activo: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    vehiculos: list[VehiculoResponse] = []