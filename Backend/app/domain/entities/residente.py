from dataclasses import dataclass, field
from datetime import datetime

from app.domain.entities.tipo_residente import TipoResidente
from app.domain.entities.vehiculo import Vehiculo


@dataclass
class Residente:
    id: int | None
    nombre: str
    documento: str
    tipo_residente: TipoResidente
    apartamento_id: int
    unidad_negocio_id: int
    telefono_1: str | None = None
    telefono_2: str | None = None
    activo: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
    vehiculos: list[Vehiculo] = field(default_factory=list)
