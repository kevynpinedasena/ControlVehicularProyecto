from dataclasses import dataclass


@dataclass
class Apartamento:
    id: int | None
    torre_id: int
    numero: str
    unidad_negocio_id: int
    activo: bool = True
