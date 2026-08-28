"""Catálogo de tipos de residente (p. ej. Propietario, Arrendatario)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class TipoResidente:
    id: int
    codigo: str
    nombre: str