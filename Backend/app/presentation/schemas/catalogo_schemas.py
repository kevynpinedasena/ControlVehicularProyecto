"""Esquemas de respuesta para los catálogos globales de tipo de vehículo y tipo de residente."""
from pydantic import BaseModel


class TipoVehiculoResponse(BaseModel):
    id: int
    codigo: str
    nombre: str


class TipoResidenteResponse(BaseModel):
    id: int
    codigo: str
    nombre: str