"""DTOs para la carga masiva de datos (torres, apartamentos, residentes, vehículos)."""
from dataclasses import dataclass, field


@dataclass
class FilaImportacion:
    """Una fila de una hoja de Excel, con sus valores por nombre de columna."""

    numero_fila: int
    valores: dict[str, str]

    def obtener(self, clave: str) -> str:
        return (self.valores.get(clave) or "").strip()


@dataclass
class DatosImportacion:
    """Contenido ya extraído del archivo Excel, agnóstico de openpyxl."""

    torres: list[FilaImportacion] = field(default_factory=list)
    apartamentos: list[FilaImportacion] = field(default_factory=list)
    residentes: list[FilaImportacion] = field(default_factory=list)
    vehiculos: list[FilaImportacion] = field(default_factory=list)
    bloques: list[FilaImportacion] = field(default_factory=list)
    parqueaderos: list[FilaImportacion] = field(default_factory=list)


@dataclass
class ErrorImportacionDTO:
    hoja: str
    fila: int
    mensaje: str


@dataclass
class DetalleImportacionDTO:
    """Una fila de la tabla de detalle: qué registro se creó o actualizó y con qué datos."""

    hoja: str
    fila: int
    accion: str  # "creado" | "actualizado"
    descripcion: str


@dataclass
class ReporteImportacionDTO:
    torres_creadas: int = 0
    apartamentos_creados: int = 0
    residentes_creados: int = 0
    vehiculos_creados: int = 0
    torres_actualizadas: int = 0
    apartamentos_actualizados: int = 0
    residentes_actualizados: int = 0
    vehiculos_actualizados: int = 0
    bloques_creados: int = 0
    bloques_actualizados: int = 0
    parqueaderos_creados: int = 0
    parqueaderos_actualizados: int = 0
    errores: list[ErrorImportacionDTO] = field(default_factory=list)
    detalles: list[DetalleImportacionDTO] = field(default_factory=list)
