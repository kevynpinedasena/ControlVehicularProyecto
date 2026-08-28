"""Funciones de normalización de texto reutilizables."""
import re
import unicodedata


def normalizar_slug(valor: str) -> str:
    """Convierte un texto en un slug: minúsculas, sin tildes, separado por guiones."""
    sin_tildes = unicodedata.normalize("NFKD", valor).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", sin_tildes).strip("-").lower()
    return slug
