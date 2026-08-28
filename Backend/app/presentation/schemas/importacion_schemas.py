"""Esquemas Pydantic para la carga masiva de datos."""
from pydantic import BaseModel


class ErrorImportacionResponse(BaseModel):
    hoja: str
    fila: int
    mensaje: str


class DetalleImportacionResponse(BaseModel):
    hoja: str
    fila: int
    accion: str
    descripcion: str


class ReporteImportacionResponse(BaseModel):
    torres_creadas: int
    apartamentos_creados: int
    residentes_creados: int
    vehiculos_creados: int
    torres_actualizadas: int
    apartamentos_actualizados: int
    residentes_actualizados: int
    vehiculos_actualizados: int
    bloques_creados: int
    bloques_actualizados: int
    parqueaderos_creados: int
    parqueaderos_actualizados: int
    errores: list[ErrorImportacionResponse]
    detalles: list[DetalleImportacionResponse]
