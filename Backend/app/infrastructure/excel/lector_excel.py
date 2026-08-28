"""Lectura de archivos Excel (.xlsx) de carga masiva, agnóstica de la capa de aplicación."""
from io import BytesIO

import openpyxl

from app.application.dto.importacion_dto import DatosImportacion, FilaImportacion
from app.domain.exceptions.excepciones import ErrorDominio

_HOJA_A_ATRIBUTO = {
    "Torres": "torres",
    "Apartamentos": "apartamentos",
    "Residentes": "residentes",
    "Bloques": "bloques",
    "Parqueaderos": "parqueaderos",
    "Vehiculos": "vehiculos",
}


class ArchivoImportacionInvalidoError(ErrorDominio):
    codigo = "ARCHIVO_IMPORTACION_INVALIDO"


def _celda_a_texto(celda: object) -> str:
    """Convierte una celda a texto, evitando que Excel convierta documentos/placas numéricas
    en flotantes (ej. '123456789.0')."""
    if celda is None:
        return ""
    if isinstance(celda, float) and celda.is_integer():
        return str(int(celda))
    return str(celda).strip()


def leer_datos_importacion(contenido: bytes) -> DatosImportacion:
    """Convierte el contenido crudo de un .xlsx en filas de datos, agrupadas por hoja."""
    try:
        libro = openpyxl.load_workbook(BytesIO(contenido), data_only=True, read_only=True)
    except Exception as error:  # noqa: BLE001 - cualquier archivo corrupto/no-excel cae aquí
        raise ArchivoImportacionInvalidoError(
            "El archivo no es un Excel (.xlsx) válido o está dañado"
        ) from error

    datos = DatosImportacion()

    for nombre_hoja, atributo in _HOJA_A_ATRIBUTO.items():
        if nombre_hoja not in libro.sheetnames:
            continue

        filas_crudas = list(libro[nombre_hoja].iter_rows(values_only=True))
        if not filas_crudas:
            continue

        encabezados = [_celda_a_texto(celda) for celda in filas_crudas[0]]
        filas: list[FilaImportacion] = []

        for numero_fila, fila in enumerate(filas_crudas[1:], start=2):
            if all(_celda_a_texto(celda) == "" for celda in fila):
                continue  # fila vacía, se ignora silenciosamente

            valores = {
                encabezados[indice]: _celda_a_texto(fila[indice])
                for indice in range(min(len(encabezados), len(fila)))
                if encabezados[indice]
            }
            filas.append(FilaImportacion(numero_fila=numero_fila, valores=valores))

        setattr(datos, atributo, filas)

    return datos
