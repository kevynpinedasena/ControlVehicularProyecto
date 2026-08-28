from dataclasses import dataclass

from app.domain.entities.parqueadero import Parqueadero


@dataclass
class ParqueaderoConOcupacionDTO:
    parqueadero: Parqueadero
    vehiculos_asignados: int


@dataclass
class CrearBloqueDTO:
    nombre: str
    codigo: str


@dataclass
class ActualizarBloqueDTO:
    nombre: str
    codigo: str


@dataclass
class CrearParqueaderoDTO:
    bloque_id: int
    numero: str
    tipo_espacio: str
    tipo_vehiculo_id: int
    capacidad: int
    propietario_residente_id: int | None = None


@dataclass
class ActualizarParqueaderoDTO:
    bloque_id: int
    numero: str
    tipo_espacio: str
    tipo_vehiculo_id: int
    capacidad: int
    activo: bool
    propietario_residente_id: int | None = None