"""Configuración centralizada de la aplicación mediante variables de entorno."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración global leída desde variables de entorno o archivo .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    database_url: str = (
        "postgresql+asyncpg://conjunto_user:conjunto_pass@localhost:5432/conjunto_db"
    )

    secret_key: str = "clave_de_desarrollo_no_usar_en_produccion"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    frontend_url: str = "http://localhost:5173"
    api_url: str = "http://localhost:8000"

    admin_plataforma_correo: str = "plataforma@conjunto.com"
    admin_plataforma_password: str = "Plataforma123!"

    @property
    def es_produccion(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def obtener_configuracion() -> Settings:
    """Devuelve una instancia única (cacheada) de la configuración."""
    return Settings()
