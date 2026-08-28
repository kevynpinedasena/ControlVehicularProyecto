"""Catálogo de tipos de vehículo (p. ej. Carro, Moto)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TipoVehiculo:
    id: int
    codigo: str
    nombre: str