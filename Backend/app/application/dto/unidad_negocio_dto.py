from dataclasses import dataclass


@dataclass
class CrearUnidadNegocioDTO:
    nombre: str
    slug: str
    color_primario: str
    color_secundario: str
    admin_nombre: str
    admin_correo: str
    admin_password: str
    logo_url: str | None = None


@dataclass
class ActualizarUnidadNegocioDTO:
    nombre: str
    slug: str
    color_primario: str
    color_secundario: str
    activo: bool
    logo_url: str | None = None
