"""Almacenamiento de logos de unidades de negocio como data URI en la base de datos.

Se guarda embebido en la fila (columna `logo_url`, de tipo texto) en vez de en el disco del
contenedor: en un despliegue como Render, el disco no es persistente y cualquier archivo subido
se perdería en el siguiente redeploy. La base de datos (Neon/Postgres) sí persiste.
"""
import base64
from pathlib import Path

from fastapi import UploadFile

from app.domain.exceptions.excepciones import ErrorDominio

_EXTENSION_A_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
}
TAMANO_MAXIMO_BYTES = 1 * 1024 * 1024  # 1 MB (se transmite en cada carga de la pantalla de ingreso)


class ArchivoInvalidoError(ErrorDominio):
    codigo = "ARCHIVO_INVALIDO"


async def guardar_logo(archivo: UploadFile) -> str:
    """Valida la imagen subida y la devuelve codificada como data URI (`data:<mime>;base64,...`)."""
    extension = Path(archivo.filename or "").suffix.lower()
    tipo_mime = _EXTENSION_A_MIME.get(extension)
    if tipo_mime is None:
        raise ArchivoInvalidoError(
            "Formato de imagen no permitido. Usa PNG, JPG, SVG o WEBP"
        )

    contenido = await archivo.read()
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise ArchivoInvalidoError("La imagen no debe superar 1 MB")

    codificado = base64.b64encode(contenido).decode("ascii")
    return f"data:{tipo_mime};base64,{codificado}"
