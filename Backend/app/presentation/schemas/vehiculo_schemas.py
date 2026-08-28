"""Esquemas Pydantic para la gestión y consulta de vehículos."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.presentation.schemas.catalogo_schemas import TipoResidenteResponse, TipoVehiculoResponse


class CrearVehiculoRequest(BaseModel):
    placa: str = Field(min_length=5, max_length=10)
    tipo_vehiculo_id: int
    residente_id: int


class ActualizarVehiculoRequest(BaseModel):
    placa: str = Field(min_length=5, max_length=10)
    tipo_vehiculo_id: int
    activo: bool = True


class VehiculoResponse(BaseModel):
    id: int
    placa: str
    tipo_vehiculo: TipoVehiculoResponse
    residente_id: int
    parqueadero_id: int | None = None
    activo: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ConsultaPlacaResponse(BaseModel):
    registrado: bool
    placa: str
    mensaje: str | None = None
    tipo_vehiculo: TipoVehiculoResponse | None = None
    torre: str | None = None
    apartamento: str | None = None
    tipo_residente: TipoResidenteResponse | None = None
    estado: str | None = None
    telefono_1: str | None = None
    telefono_2: str | None = None
    parqueadero: str | None = None