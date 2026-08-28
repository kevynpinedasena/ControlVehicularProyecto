"""Generación y verificación de tokens JWT (access y refresh)."""
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

from jose import JWTError, jwt

from app.config.settings import obtener_configuracion
from app.domain.exceptions.excepciones import TokenInvalidoError

configuracion = obtener_configuracion()


def _crear_token(datos: dict[str, Any], expira_en: timedelta, tipo: Literal["access", "refresh"]) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {**datos, "exp": ahora + expira_en, "iat": ahora, "tipo": tipo}
    return jwt.encode(payload, configuracion.secret_key, algorithm=configuracion.jwt_algorithm)


def crear_access_token(usuario_id: int, rol: str, unidad_negocio_id: int | None = None) -> str:
    return _crear_token(
        {"sub": str(usuario_id), "rol": rol, "unidad_negocio_id": unidad_negocio_id},
        timedelta(minutes=configuracion.access_token_expire_minutes),
        "access",
    )


def crear_refresh_token(usuario_id: int) -> str:
    return _crear_token(
        {"sub": str(usuario_id)},
        timedelta(days=configuracion.refresh_token_expire_days),
        "refresh",
    )


def decodificar_token(token: str, tipo_esperado: Literal["access", "refresh"]) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, configuracion.secret_key, algorithms=[configuracion.jwt_algorithm]
        )
    except JWTError as error:
        raise TokenInvalidoError("El token es inválido o ha expirado") from error

    if payload.get("tipo") != tipo_esperado:
        raise TokenInvalidoError("El tipo de token no es el esperado")

    return payload
