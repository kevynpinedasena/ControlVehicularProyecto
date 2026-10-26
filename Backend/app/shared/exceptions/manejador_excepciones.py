"""Manejo centralizado de excepciones: traduce errores de dominio a respuestas HTTP consistentes."""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.exceptions.excepciones import ErrorDominio
from app.shared.logging.logger import obtener_logger

logger = obtener_logger(__name__)

_CODIGO_A_STATUS = {
    "PLACA_INVALIDA": status.HTTP_400_BAD_REQUEST,
    "PLACA_DUPLICADA": status.HTTP_409_CONFLICT,
    "REGLA_VEHICULO_INVALIDA": status.HTTP_400_BAD_REQUEST,
    "DOCUMENTO_DUPLICADO": status.HTTP_409_CONFLICT,
    "CORREO_DUPLICADO": status.HTTP_409_CONFLICT,
    "CODIGO_TORRE_DUPLICADO": status.HTTP_409_CONFLICT,
    "APARTAMENTO_DUPLICADO": status.HTTP_409_CONFLICT,
    "ENTIDAD_NO_ENCONTRADA": status.HTTP_404_NOT_FOUND,
    "CREDENCIALES_INVALIDAS": status.HTTP_401_UNAUTHORIZED,
    "USUARIO_INACTIVO": status.HTTP_403_FORBIDDEN,
    "PERMISO_DENEGADO": status.HTTP_403_FORBIDDEN,
    "TOKEN_INVALIDO": status.HTTP_401_UNAUTHORIZED,
    "SLUG_DUPLICADO": status.HTTP_409_CONFLICT,
    "UNIDAD_NEGOCIO_INACTIVA": status.HTTP_403_FORBIDDEN,
    "ACCESO_UNIDAD_NEGOCIO_INVALIDO": status.HTTP_403_FORBIDDEN,
    "ARCHIVO_INVALIDO": status.HTTP_400_BAD_REQUEST,
    "ARCHIVO_IMPORTACION_INVALIDO": status.HTTP_400_BAD_REQUEST,
    "CODIGO_BLOQUE_DUPLICADO": status.HTTP_409_CONFLICT,
    "PARQUEADERO_DUPLICADO": status.HTTP_409_CONFLICT,
    "PARQUEADERO_LLENO": status.HTTP_400_BAD_REQUEST,
    "TIPO_VEHICULO_INCOMPATIBLE": status.HTTP_400_BAD_REQUEST,
    "PROPIETARIO_INVALIDO": status.HTTP_400_BAD_REQUEST,
    "DEMASIADOS_INTENTOS": status.HTTP_429_TOO_MANY_REQUESTS,
}


def _respuesta_error(mensaje: str, codigo: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": True, "mensaje": mensaje, "codigo": codigo},
    )


def registrar_manejadores_excepciones(app: FastAPI) -> None:
    """Registra los manejadores globales de excepciones sobre la instancia de FastAPI."""

    @app.exception_handler(ErrorDominio)
    async def manejar_error_dominio(request: Request, exc: ErrorDominio) -> JSONResponse:
        status_code = _CODIGO_A_STATUS.get(exc.codigo, status.HTTP_400_BAD_REQUEST)
        return _respuesta_error(exc.mensaje, exc.codigo, status_code)

    @app.exception_handler(RequestValidationError)
    async def manejar_error_validacion(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _respuesta_error(
            "Los datos enviados no son válidos", "DATOS_INVALIDOS", status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    @app.exception_handler(Exception)
    async def manejar_error_inesperado(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Error interno no controlado")
        return _respuesta_error(
            "Ocurrió un error interno en el servidor", "ERROR_INTERNO", status.HTTP_500_INTERNAL_SERVER_ERROR
        )
