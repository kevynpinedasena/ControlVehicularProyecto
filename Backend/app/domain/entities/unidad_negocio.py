from dataclasses import dataclass
from datetime import datetime


@dataclass
class UnidadNegocio:
    """Una unidad de negocio (conjunto residencial) dentro de la plataforma."""

    id: int | None
    nombre: str
    slug: str
    logo_url: str | None = None
    color_primario: str = "#2563eb"
    color_secundario: str = "#1e293b"
    activo: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
