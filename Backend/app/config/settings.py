"""Configuración centralizada de la aplicación mediante variables de entorno."""
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_SECRET_KEY_POR_DEFECTO = "clave_de_desarrollo_no_usar_en_produccion"
_ADMIN_PASSWORD_POR_DEFECTO = "Plataforma123!"


class Settings(BaseSettings):
    """Configuración global leída desde variables de entorno o archivo .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"

    database_url: str = (
        "postgresql+asyncpg://conjunto_user:conjunto_pass@localhost:5432/conjunto_db"
    )

    secret_key: str = _SECRET_KEY_POR_DEFECTO
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    frontend_url: str = "http://localhost:5173"
    api_url: str = "http://localhost:8000"

    # Tamaño del thread pool usado por asyncio.to_thread (ej. verificar_password/hashear_password,
    # que son CPU-bound). El default de asyncio (min(32, cpu_count+4)) se queda corto bajo ráfagas
    # grandes de login simultáneo y encola el trabajo; ver app/main.py.
    tamano_pool_hilos: int = 64

    # Pool de conexiones a la base de datos (ver app/infrastructure/database/session.py). El
    # default de SQLAlchemy (pool_size=5, max_overflow=10 => 15 conexiones) se agota bajo ráfagas
    # grandes de requests concurrentes y las que no alcanzan turno fallan con TimeoutError tras
    # 30s. Ajustar también si se reduce max_connections de Postgres (por defecto 100).
    db_pool_size: int = 20
    db_max_overflow: int = 40

    admin_plataforma_correo: str = "plataforma@conjunto.com"
    admin_plataforma_password: str = _ADMIN_PASSWORD_POR_DEFECTO

    @property
    def es_produccion(self) -> bool:
        return self.environment.lower() == "production"

    @model_validator(mode="after")
    def _validar_secretos_en_produccion(self) -> "Settings":
        """En producción, impide arrancar con los valores de ejemplo del repositorio."""
        if self.es_produccion:
            if self.secret_key == _SECRET_KEY_POR_DEFECTO:
                raise ValueError(
                    "SECRET_KEY no puede dejarse en su valor de ejemplo cuando ENVIRONMENT=production"
                )
            if self.admin_plataforma_password == _ADMIN_PASSWORD_POR_DEFECTO:
                raise ValueError(
                    "ADMIN_PLATAFORMA_PASSWORD no puede dejarse en su valor de ejemplo "
                    "cuando ENVIRONMENT=production"
                )
        return self


@lru_cache
def obtener_configuracion() -> Settings:
    """Devuelve una instancia única (cacheada) de la configuración."""
    return Settings()
