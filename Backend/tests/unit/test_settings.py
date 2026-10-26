"""Pruebas unitarias: la configuración rechaza secretos de ejemplo en producción."""
import pytest

from app.config.settings import Settings


def test_produccion_rechaza_secret_key_de_ejemplo() -> None:
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(environment="production", admin_plataforma_password="ClaveRealSegura123")


def test_produccion_rechaza_password_admin_de_ejemplo() -> None:
    with pytest.raises(ValueError, match="ADMIN_PLATAFORMA_PASSWORD"):
        Settings(environment="production", secret_key="una-clave-secreta-real-y-larga")


def test_produccion_acepta_secretos_personalizados() -> None:
    configuracion = Settings(
        environment="production",
        secret_key="una-clave-secreta-real-y-larga",
        admin_plataforma_password="ClaveRealSegura123",
    )
    assert configuracion.es_produccion is True


def test_desarrollo_acepta_los_valores_de_ejemplo() -> None:
    configuracion = Settings(environment="development")
    assert configuracion.es_produccion is False
