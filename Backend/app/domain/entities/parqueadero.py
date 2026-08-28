from dataclasses import dataclass

from app.domain.entities.tipo_vehiculo import TipoVehiculo

COMUNAL = "COMUNAL"
PRIVADO = "PRIVADO"


@dataclass
class Parqueadero:
    id: int | None
    bloque_id: int
    numero: str
    tipo_espacio: str  # COMUNAL | PRIVADO
    tipo_vehiculo: TipoVehiculo
    capacidad: int
    unidad_negocio_id: int
    propietario_residente_id: int | None = None
    activo: bool = True