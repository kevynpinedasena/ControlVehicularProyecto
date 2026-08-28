from dataclasses import dataclass


@dataclass
class CrearTorreDTO:
    nombre: str
    codigo: str


@dataclass
class ActualizarTorreDTO:
    nombre: str
    codigo: str


@dataclass
class CrearApartamentoDTO:
    torre_id: int
    numero: str


@dataclass
class ActualizarApartamentoDTO:
    torre_id: int
    numero: str
    activo: bool
