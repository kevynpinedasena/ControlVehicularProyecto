"""Límite de intentos para endpoints sensibles a fuerza bruta (ej. login).

Ventana deslizante en memoria del proceso, por clave (IP + correo). Suficiente para un único
backend como este; si en el futuro se corre con varias réplicas, hay que mover el conteo a Redis.
"""
import time
from collections import defaultdict

from fastapi import Request

from app.domain.exceptions.excepciones import DemasiadosIntentosError

_MAX_INTENTOS = 5
_VENTANA_SEGUNDOS = 60

_intentos: dict[str, list[float]] = defaultdict(list)


def limitar_intentos_login(request: Request, correo: str) -> None:
    """Lanza DemasiadosIntentosError si la combinación IP+correo superó el límite de intentos."""
    clave = f"{request.client.host if request.client else 'desconocido'}:{correo.lower()}"
    ahora = time.monotonic()
    intentos = _intentos[clave]
    intentos[:] = [t for t in intentos if ahora - t < _VENTANA_SEGUNDOS]

    if len(intentos) >= _MAX_INTENTOS:
        raise DemasiadosIntentosError(
            "Demasiados intentos de inicio de sesión. Espera un minuto antes de volver a intentar."
        )

    intentos.append(ahora)


def reiniciar_limitador() -> None:
    """Limpia el estado del limitador. Uso exclusivo de las pruebas, para aislarlas entre sí."""
    _intentos.clear()
