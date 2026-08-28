from dataclasses import dataclass


@dataclass
class Bloque:
    id: int | None
    nombre: str
    codigo: str
    unidad_negocio_id: int