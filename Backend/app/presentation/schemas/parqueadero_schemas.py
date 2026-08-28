"""Esquemas Pydantic para la gestión de bloques y parqueaderos."""
from pydantic import BaseModel, Field

from app.presentation.schemas.catalogo_schemas import TipoVehiculoResponse


class CrearBloqueRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    codigo: str = Field(min_length=1, max_length=20)


class ActualizarBloqueRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    codigo: str = Field(min_length=1, max_length=20)


class BloqueResponse(BaseModel):
    id: int
    nombre: str
    codigo: str


class CrearParqueaderoRequest(BaseModel):
    bloque_id: int
    numero: str = Field(min_length=1, max_length=20)
    tipo_espacio: str = Field(pattern="^(COMUNAL|PRIVADO)$")
    tipo_vehiculo_id: int
    capacidad: int = Field(ge=1, le=100)
    propietario_residente_id: int | None = None


class ActualizarParqueaderoRequest(BaseModel):
    bloque_id: int
    numero: str = Field(min_length=1, max_length=20)
    tipo_espacio: str = Field(pattern="^(COMUNAL|PRIVADO)$")
    tipo_vehiculo_id: int
    capacidad: int = Field(ge=1, le=100)
    activo: bool = True
    propietario_residente_id: int | None = None


class ParqueaderoResponse(BaseModel):
    id: int
    bloque_id: int
    numero: str
    tipo_espacio: str
    tipo_vehiculo: TipoVehiculoResponse
    capacidad: int
    propietario_residente_id: int | None = None
    vehiculos_asignados: int
    activo: bool


class AsignarParqueaderoRequest(BaseModel):
    parqueadero_id: int | None