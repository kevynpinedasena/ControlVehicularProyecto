from dataclasses import dataclass
from datetime import datetime

from app.domain.entities.tipo_vehiculo import TipoVehiculo
from app.domain.value_objects.placa import Placa


@dataclass
class Vehiculo:
    id: int | None
    placa: Placa
    tipo_vehiculo: TipoVehiculo
    residente_id: int
    unidad_negocio_id: int
    parqueadero_id: int | None = None
    activo: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
