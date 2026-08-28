"""Siembra datos iniciales: roles del sistema y el usuario Administrador de Plataforma.

Ejecutar con: python -m app.infrastructure.database.seed
"""
import asyncio

from app.config.settings import obtener_configuracion
from app.domain.entities.enums import NombreRol
from app.domain.entities.usuario import Usuario
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.repositories.usuario_repository_impl import (
    UsuarioRepository,
    obtener_o_crear_rol,
)
from app.infrastructure.security.hashing import hashear_password
from app.shared.logging.logger import obtener_logger

logger = obtener_logger(__name__)


async def sembrar_datos_iniciales() -> None:
    configuracion = obtener_configuracion()
    correo_admin = configuracion.admin_plataforma_correo
    password_admin = configuracion.admin_plataforma_password

    async with SessionLocal() as sesion:
        for rol in NombreRol:
            await obtener_o_crear_rol(sesion, rol)

        usuarios = UsuarioRepository(sesion)
        if await usuarios.existe_correo(correo_admin):
            logger.info("El usuario Administrador de Plataforma ya existe, no se vuelve a crear")
            return

        await usuarios.crear(
            Usuario(
                id=None,
                nombre="Administrador de Plataforma",
                correo=correo_admin,
                password_hash=hashear_password(password_admin),
                rol=NombreRol.ADMIN_PLATAFORMA,
                unidad_negocio_id=None,
            )
        )
        logger.info("Usuario Administrador de Plataforma creado: %s", correo_admin)


if __name__ == "__main__":
    obtener_configuracion()
    asyncio.run(sembrar_datos_iniciales())
