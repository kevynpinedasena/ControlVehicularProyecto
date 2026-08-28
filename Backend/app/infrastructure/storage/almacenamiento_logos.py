"""Almacenamiento local de archivos subidos (logos de unidades de negocio)."""
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.domain.exceptions.excepciones import ErrorDominio

DIRECTORIO_LOGOS = Path("uploads/logos")
EXTENSIONES_PERMITIDAS = {".png", ".jpg", ".jpeg", ".svg", ".webp"}
TAMANO_MAXIMO_BYTES = 5 * 1024 * 1024  # 5 MB


class ArchivoInvalidoError(ErrorDominio):
    codigo = "ARCHIVO_INVALIDO"


async def guardar_logo(archivo: UploadFile) -> str:
    """Guarda la imagen subida en disco y devuelve la ruta pública para servirla."""
    extension = Path(archivo.filename or "").suffix.lower()
    if extension not in EXTENSIONES_PERMITIDAS:
        raise ArchivoInvalidoError(
            "Formato de imagen no permitido. Usa PNG, JPG, SVG o WEBP"
        )

    contenido = await archivo.read()
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise ArchivoInvalidoError("La imagen no debe superar los 5 MB")

    DIRECTORIO_LOGOS.mkdir(parents=True, exist_ok=True)
    nombre_archivo = f"{uuid.uuid4().hex}{extension}"
    ruta = DIRECTORIO_LOGOS / nombre_archivo
    ruta.write_bytes(contenido)

    return f"/uploads/logos/{nombre_archivo}"
