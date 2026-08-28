"""Endpoints de carga masiva (Excel). Restringido al Super Administrador de cada unidad."""
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import Response

from app.application.use_cases.importacion_use_cases import ImportarDatosMasivosUseCase
from app.infrastructure.excel.generador_plantilla import generar_plantilla_excel
from app.infrastructure.excel.lector_excel import leer_datos_importacion
from app.presentation.dependencies.autenticacion import UnidadNegocioActual, requerir_super_admin
from app.presentation.dependencies.casos_uso import caso_uso_importar_datos_masivos
from app.presentation.schemas.importacion_schemas import (
    DetalleImportacionResponse,
    ErrorImportacionResponse,
    ReporteImportacionResponse,
)

router = APIRouter(
    prefix="/import",
    tags=["Carga masiva"],
    dependencies=[Depends(requerir_super_admin)],
)

_TIPO_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/template")
async def descargar_plantilla() -> Response:
    contenido = generar_plantilla_excel()
    return Response(
        content=contenido,
        media_type=_TIPO_XLSX,
        headers={"Content-Disposition": 'attachment; filename="plantilla-carga-masiva.xlsx"'},
    )


@router.post("/upload", response_model=ReporteImportacionResponse)
async def subir_archivo_importacion(
    unidad_negocio_id: UnidadNegocioActual,
    caso_uso: Annotated[ImportarDatosMasivosUseCase, Depends(caso_uso_importar_datos_masivos)],
    archivo: Annotated[UploadFile, File()],
) -> ReporteImportacionResponse:
    contenido = await archivo.read()
    datos = leer_datos_importacion(contenido)
    reporte = await caso_uso.ejecutar(unidad_negocio_id, datos)

    return ReporteImportacionResponse(
        torres_creadas=reporte.torres_creadas,
        apartamentos_creados=reporte.apartamentos_creados,
        residentes_creados=reporte.residentes_creados,
        vehiculos_creados=reporte.vehiculos_creados,
        torres_actualizadas=reporte.torres_actualizadas,
        apartamentos_actualizados=reporte.apartamentos_actualizados,
        residentes_actualizados=reporte.residentes_actualizados,
        vehiculos_actualizados=reporte.vehiculos_actualizados,
        bloques_creados=reporte.bloques_creados,
        bloques_actualizados=reporte.bloques_actualizados,
        parqueaderos_creados=reporte.parqueaderos_creados,
        parqueaderos_actualizados=reporte.parqueaderos_actualizados,
        errores=[
            ErrorImportacionResponse(hoja=e.hoja, fila=e.fila, mensaje=e.mensaje) for e in reporte.errores
        ],
        detalles=[
            DetalleImportacionResponse(hoja=d.hoja, fila=d.fila, accion=d.accion, descripcion=d.descripcion)
            for d in reporte.detalles
        ],
    )
