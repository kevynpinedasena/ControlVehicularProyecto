from dataclasses import dataclass


@dataclass
class CrearResidenteDTO:
    nombre: str
    documento: str
    tipo_residente_id: int
    apartamento_id: int
    telefono_1: str | None = None
    telefono_2: str | None = None


@dataclass
class ActualizarResidenteDTO:
    nombre: str
    documento: str
    tipo_residente_id: int
    apartamento_id: int
    activo: bool
    telefono_1: str | None = None
    telefono_2: str | None = None
