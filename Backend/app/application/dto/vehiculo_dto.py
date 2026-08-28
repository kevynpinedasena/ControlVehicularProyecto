from dataclasses import dataclass

from app.domain.entities.tipo_residente import TipoResidente
from app.domain.entities.tipo_vehiculo import TipoVehiculo


@dataclass
class CrearVehiculoDTO:
    placa: str
    tipo_vehiculo_id: int
    residente_id: int


@dataclass
class ActualizarVehiculoDTO:
    placa: str
    tipo_vehiculo_id: int
    activo: bool


@dataclass
class AsignarParqueaderoVehiculoDTO:
    parqueadero_id: int | None


@dataclass
class ResultadoConsultaPlacaDTO:
    registrado: bool
    placa: str
    mensaje: str | None = None
    tipo_vehiculo: TipoVehiculo | None = None
    torre: str | None = None
    apartamento: str | None = None
    tipo_residente: TipoResidente | None = None
    estado: str | None = None
    telefono_1: str | None = None
    telefono_2: str | None = None
    parqueadero: str | None = None
